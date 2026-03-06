"""
Streamlit Dashboard with Agent Status, Countdown Timers, and Manual Trading
Shows when agents will run next and displays live agent actions
"""
import streamlit as st
from agents.technical_analyst import TechnicalAnalyst
from agents.sentiment_analyst import SentimentAnalyst
from agents.decision_maker import DecisionMaker
from agents.market_scout import MarketScout
from agents.portfolio_analyzer import PortfolioAnalyzer
from portfolio import Portfolio
from data_fetcher import get_stock_data, get_nse_top_stocks
from market_hours import get_market_status, get_next_run_times
import pandas as pd
import time
import re
from datetime import datetime, timedelta

st.set_page_config(page_title="AI Stock Agents - NSE", page_icon="🤖", layout="wide")

# Initialize session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = Portfolio(starting_cash=100000)
    st.session_state.portfolio.load()

if 'results' not in st.session_state:
    st.session_state.results = []

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = get_nse_top_stocks()[:5]

if 'agent_log' not in st.session_state:
    st.session_state.agent_log = []

# Title
st.title("🤖 5-Agent Autonomous Trading System - NSE")

# Market status and countdown timers
market_open, status_msg = get_market_status()
next_runs = get_next_run_times()

col1, col2 = st.columns([2, 1])
with col1:
    if market_open:
        st.success(status_msg)
    else:
        st.warning(status_msg)

with col2:
    now = next_runs['current_time']
    
    # Countdown to next Portfolio Analyzer
    pa_delta = next_runs['portfolio_analyzer'] - now
    pa_hours = int(pa_delta.total_seconds() // 3600)
    pa_mins = int((pa_delta.total_seconds() % 3600) // 60)
    
    # Countdown to next Market Scout
    ms_delta = next_runs['market_scout'] - now
    ms_hours = int(ms_delta.total_seconds() // 3600)
    ms_mins = int((ms_delta.total_seconds() % 3600) // 60)
    
    # Countdown to next Agent Analysis
    aa_delta = next_runs['agent_analysis'] - now
    aa_hours = int(aa_delta.total_seconds() // 3600)
    aa_mins = int((aa_delta.total_seconds() % 3600) // 60)
    
    st.metric("⏰ Next Portfolio Analyzer", f"{pa_hours}h {pa_mins}m")
    st.metric("⏰ Next Market Scout", f"{ms_hours}h {ms_mins}m")
    st.metric("⏰ Next Agent Analysis", f"{aa_hours}h {aa_mins}m")

st.markdown("---")

# Sidebar
st.sidebar.header("⚙️ Controls")

# Watchlist
st.sidebar.subheader("📋 Watchlist")
watchlist_display = ", ".join([s.replace('.NS', '') for s in st.session_state.watchlist])
st.sidebar.text(watchlist_display)

new_stock = st.sidebar.text_input("Add stock (e.g., WIPRO)", key="add_stock")
if st.sidebar.button("➕ Add to Watchlist"):
    if new_stock:
        symbol = new_stock.upper()
        if not symbol.endswith('.NS'):
            symbol = f"{symbol}.NS"
        if symbol not in st.session_state.watchlist:
            st.session_state.watchlist.append(symbol)
            st.sidebar.success(f"Added {symbol}")
        else:
            st.sidebar.warning("Already in watchlist")

# Run controls
run_portfolio_analyzer = st.sidebar.button("🏥 Run Portfolio Analyzer")
run_market_scout = st.sidebar.button("🔎 Run Market Scout")
run_analysis = st.sidebar.button("🚀 Run Agent Analysis", type="primary")

# Portfolio commands
st.sidebar.markdown("---")
st.sidebar.subheader("💼 Portfolio Commands")
col1, col2 = st.sidebar.columns(2)
if col1.button("⏸️ HOLD"):
    st.session_state.portfolio.hold_mode = True
    st.session_state.portfolio.save()
    st.sidebar.success("HOLD mode activated")

if col2.button("▶️ RESUME"):
    st.session_state.portfolio.hold_mode = False
    st.session_state.portfolio.save()
    st.sidebar.success("HOLD mode deactivated")

if st.sidebar.button("🔴 SELL ALL", type="secondary"):
    current_prices = {}
    for symbol in st.session_state.portfolio.holdings.keys():
        data = get_stock_data(symbol, days=1)
        if data:
            current_prices[symbol] = data['current_price']
    
    results = st.session_state.portfolio.sell_all(current_prices)
    st.session_state.portfolio.save()
    st.sidebar.success("Sold all holdings!")
    st.rerun()

if st.sidebar.button("🔄 Reset Portfolio"):
    st.session_state.portfolio = Portfolio(starting_cash=100000)
    st.session_state.portfolio.save()
    st.success("Portfolio reset to ₹1,00,000")
    st.rerun()

# Portfolio Summary
st.header("📊 Portfolio Summary")

current_prices = {}
for symbol in st.session_state.watchlist + list(st.session_state.portfolio.holdings.keys()):
    data = get_stock_data(symbol, days=1)
    if data:
        current_prices[symbol] = data['current_price']

summary = st.session_state.portfolio.get_summary(current_prices)

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Value", f"₹{summary['total_value']:,.2f}")
col2.metric("💵 Cash", f"₹{summary['cash']:,.2f}")
col3.metric("📈 Holdings", f"₹{summary['holdings_value']:,.2f}")
col4.metric("📊 Return", f"{summary['return_pct']:.2f}%", f"₹{summary['return_rupees']:,.2f}")

if summary['hold_mode']:
    st.warning("⏸️ HOLD MODE ACTIVE - New purchases paused")

# Holdings Table
if st.session_state.portfolio.holdings:
    st.subheader("🎯 Current Holdings")
    holdings_data = []
    for symbol, info in st.session_state.portfolio.holdings.items():
        current_price = current_prices.get(symbol, 0)
        current_value = info['shares'] * current_price
        gain = current_value - (info['shares'] * info['avg_price'])
        gain_pct = (gain / (info['shares'] * info['avg_price'])) * 100 if info['avg_price'] > 0 else 0
        
        holdings_data.append({
            'Symbol': symbol.replace('.NS', ''),
            'Shares': info['shares'],
            'Avg Price': f"₹{info['avg_price']:.2f}",
            'Current Price': f"₹{current_price:.2f}",
            'Value': f"₹{current_value:.2f}",
            'Gain/Loss': f"₹{gain:.2f} ({gain_pct:.2f}%)"
        })
    
    st.dataframe(pd.DataFrame(holdings_data), use_container_width=True)

st.markdown("---")

# Run Portfolio Analyzer
if run_portfolio_analyzer:
    st.header("🏥 Portfolio Analyzer")
    with st.spinner("Analyzing portfolio health..."):
        analyzer = PortfolioAnalyzer()
        result = analyzer.analyze_portfolio(st.session_state.portfolio, current_prices)
        
        st.write(result['analysis'])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Positions", result['metrics']['num_positions'])
        col2.metric("Return", f"{result['metrics']['return_pct']:.2f}%")
        col3.metric("Cash %", f"{result['metrics']['cash_pct']:.1f}%")
        
        # Store for Market Scout
        st.session_state.portfolio_analysis = result

# Run Market Scout
if run_market_scout:
    if 'portfolio_analysis' not in st.session_state:
        st.warning("⚠️ Run Portfolio Analyzer first!")
    else:
        st.header("🔎 Market Scout")
        with st.spinner("Discovering stocks and updating watchlist..."):
            scout = MarketScout()
            scout_result = scout.discover_and_update_watchlist(
                current_watchlist=st.session_state.watchlist,
                portfolio_holdings=st.session_state.portfolio.holdings,
                portfolio_analysis=st.session_state.portfolio_analysis
            )
            
            st.write(scout_result['action_summary'])
            
            # Update watchlist
            st.session_state.watchlist = scout_result['updated_watchlist']
            st.success(f"✅ Watchlist updated! Now tracking {len(st.session_state.watchlist)} stocks")
            time.sleep(1)
            st.rerun()

# Run Full Analysis
if run_analysis:
    st.header("🔍 Agent Analysis")
    
    tech_agent = TechnicalAnalyst()
    sentiment_agent = SentimentAnalyst()
    decision_agent = DecisionMaker()
    
    portfolio_value = st.session_state.portfolio.get_portfolio_value(current_prices)
    available_cash = st.session_state.portfolio.cash
    
    results = []
    
    for symbol in st.session_state.watchlist:
        with st.expander(f"📊 {symbol.replace('.NS', '')} Analysis", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔍 Technical Analysis")
                with st.spinner("Analyzing..."):
                    tech_result = tech_agent.analyze(symbol)
                    if tech_result['data']:
                        st.write(tech_result['analysis'])
                    else:
                        st.error("Unable to fetch data")
                        continue
            
            with col2:
                st.subheader("📰 Sentiment Analysis")
                with st.spinner("Analyzing..."):
                    sentiment_result = sentiment_agent.analyze(symbol)
                    st.write(sentiment_result['analysis'])
            
            st.subheader("⚖️ Final Decision")
            with st.spinner("Deciding..."):
                decision_result = decision_agent.decide(
                    symbol, 
                    tech_result, 
                    sentiment_result,
                    portfolio_value,
                    available_cash
                )
                st.write(decision_result['decision'])
                
                # Execute decisions
                decision_text = decision_result['decision'].upper()
                if 'BUY' in decision_text and available_cash > 10000:
                    max_allocation = available_cash * 0.20
                    price = current_prices.get(symbol, 0)
                    if price > 0:
                        shares = int(max_allocation / price)
                        if shares > 0:
                            success, msg = st.session_state.portfolio.buy(symbol, shares, price)
                            if success:
                                st.success(f"✅ {msg}")
                                decision_result['executed'] = True
                                available_cash = st.session_state.portfolio.cash
                            else:
                                st.warning(f"⚠️ {msg}")
                
                results.append(decision_result)
    
    st.session_state.portfolio.save()
    st.session_state.results = results
    time.sleep(1)
    st.rerun()

# Transaction History
if st.session_state.portfolio.history:
    st.markdown("---")
    st.header("📜 Transaction History")
    history_df = pd.DataFrame(st.session_state.portfolio.history)
    st.dataframe(history_df, use_container_width=True)
