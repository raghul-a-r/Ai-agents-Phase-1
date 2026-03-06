"""
Main Agent System - DEMO VERSION (NO Market Hours Check)
Use this for demonstrations outside market hours (like 4:30 PM meeting)

Runs complete workflow once:
1. Portfolio Analyzer
2. Market Scout (updates watchlist)
3. Agent Analysis (on updated watchlist)
"""
from agents.technical_analyst import TechnicalAnalyst
from agents.sentiment_analyst import SentimentAnalyst
from agents.decision_maker import DecisionMaker
from agents.market_scout import MarketScout
from agents.portfolio_analyzer import PortfolioAnalyzer
from portfolio import Portfolio
from data_fetcher import get_stock_data, get_nse_top_stocks
import time

def main():
    """Main demo flow - runs complete workflow once"""
    print("\n🚀 AI Stock Agent System - NSE (DEMO MODE)")
    print("🎬 Running complete workflow demonstration")
    print("="*70 + "\n")
    
    # Initialize
    portfolio = Portfolio(starting_cash=100000)
    portfolio.load()
    
    watchlist = get_nse_top_stocks()[:5]
    
    print(f"📋 Initial Watchlist: {', '.join([s.replace('.NS', '') for s in watchlist])}\n")
    
    # Get current prices
    current_prices = {}
    for symbol in list(portfolio.holdings.keys()) + watchlist:
        data = get_stock_data(symbol, days=1)
        if data:
            current_prices[symbol] = data['current_price']
    
    # ========================================
    # STEP 1: Portfolio Analyzer
    # ========================================
    print("="*70)
    print("STEP 1: 🏥 PORTFOLIO ANALYZER")
    print("="*70)
    print("Analyzing portfolio health and identifying gaps...\n")
    
    analyzer = PortfolioAnalyzer()
    portfolio_analysis = analyzer.analyze_portfolio(portfolio, current_prices)
    
    print(portfolio_analysis['analysis'])
    print(f"\n📊 Metrics: {portfolio_analysis['metrics']['num_positions']} positions, "
          f"{portfolio_analysis['metrics']['return_pct']:.2f}% return\n")
    
    time.sleep(2)
    
    # ========================================
    # STEP 2: Market Scout
    # ========================================
    print("\n" + "="*70)
    print("STEP 2: 🔎 MARKET SCOUT")
    print("="*70)
    print("Receiving portfolio insights and updating watchlist...\n")
    
    scout = MarketScout()
    scout_result = scout.discover_and_update_watchlist(
        current_watchlist=watchlist,
        portfolio_holdings=portfolio.holdings,
        portfolio_analysis=portfolio_analysis
    )
    
    print(scout_result['action_summary'])
    
    # Update watchlist
    watchlist = scout_result['updated_watchlist']
    print(f"\n📋 Updated Watchlist ({len(watchlist)} stocks): {', '.join([s.replace('.NS', '') for s in watchlist])}\n")
    
    time.sleep(2)
    
    # ========================================
    # STEP 3: Agent Analysis
    # ========================================
    print("\n" + "="*70)
    print("STEP 3: 🤖 AGENT ANALYSIS")
    print("="*70)
    print("Running analysis on updated watchlist...\n")
    
    # Initialize agents
    tech_agent = TechnicalAnalyst()
    sentiment_agent = SentimentAnalyst()
    decision_agent = DecisionMaker()
    
    # Update current prices for new watchlist
    for symbol in watchlist:
        if symbol not in current_prices:
            data = get_stock_data(symbol, days=1)
            if data:
                current_prices[symbol] = data['current_price']
    
    portfolio_value = portfolio.get_portfolio_value(current_prices)
    available_cash = portfolio.cash
    
    print(f"📊 Portfolio: ₹{portfolio_value:,.2f} | Cash: ₹{available_cash:,.2f}\n")
    
    results = []
    
    for symbol in watchlist:
        print(f"\n{'='*70}")
        print(f"Analyzing: {symbol}")
        print('='*70)
        
        # Technical Analysis
        technical_result = tech_agent.analyze(symbol)
        time.sleep(1)
        
        # Sentiment Analysis
        sentiment_result = sentiment_agent.analyze(symbol)
        time.sleep(1)
        
        # Decision Making
        decision_result = decision_agent.decide(
            symbol, 
            technical_result, 
            sentiment_result,
            portfolio_value,
            available_cash
        )
        
        print(f"\n📊 Decision:")
        print(decision_result['decision'])
        
        # Execute trades
        decision_text = decision_result['decision'].upper()
        
        if 'BUY' in decision_text and available_cash > 10000:
            max_allocation = available_cash * 0.20
            price = current_prices.get(symbol, 0)
            if price > 0:
                shares = int(max_allocation / price)
                if shares > 0:
                    success, msg = portfolio.buy(symbol, shares, price)
                    if success:
                        print(f"\n✅ EXECUTED: {msg}")
                        decision_result['executed'] = True
                        available_cash = portfolio.cash
        
        elif 'SELL' in decision_text and symbol in portfolio.holdings:
            price = current_prices.get(symbol, 0)
            if price > 0:
                shares = portfolio.holdings[symbol]['shares']
                success, msg = portfolio.sell(symbol, shares, price)
                if success:
                    print(f"\n✅ EXECUTED: {msg}")
                    decision_result['executed'] = True
                    available_cash = portfolio.cash
        
        results.append(decision_result)
        time.sleep(1)
    
    # Save portfolio
    portfolio.save()
    
    # ========================================
    # FINAL SUMMARY
    # ========================================
    print("\n" + "="*70)
    print("📈 FINAL SUMMARY")
    print("="*70)
    
    # Update prices one more time
    for symbol in list(portfolio.holdings.keys()) + watchlist:
        data = get_stock_data(symbol, days=1)
        if data:
            current_prices[symbol] = data['current_price']
    
    summary = portfolio.get_summary(current_prices)
    
    print(f"\n💰 Portfolio Value: ₹{summary['total_value']:,.2f}")
    print(f"💵 Cash: ₹{summary['cash']:,.2f}")
    print(f"📊 Holdings Value: ₹{summary['holdings_value']:,.2f}")
    print(f"📈 Return: ₹{summary['return_rupees']:,.2f} ({summary['return_pct']:.2f}%)")
    
    if portfolio.holdings:
        print(f"\n🎯 Holdings ({len(portfolio.holdings)} positions):")
        for symbol, info in portfolio.holdings.items():
            current_price = current_prices.get(symbol, 0)
            current_value = info['shares'] * current_price
            gain = current_value - (info['shares'] * info['avg_price'])
            gain_pct = (gain / (info['shares'] * info['avg_price'])) * 100 if info['avg_price'] > 0 else 0
            print(f"  {symbol.replace('.NS', '')}: {info['shares']} shares @ ₹{info['avg_price']:.2f} "
                  f"| Current: ₹{current_price:.2f} | Gain: ₹{gain:.2f} ({gain_pct:.2f}%)")
    
    print("\n" + "="*70)
    print("✅ Demo Complete!")
    print("💡 Run 'streamlit run app.py' for interactive dashboard")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
