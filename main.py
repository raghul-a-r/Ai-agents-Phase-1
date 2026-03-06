"""
Main Agent System - WITH Market Hours Check and Agent Scheduling
Autonomous 5-agent trading system for NSE stocks

========================================
PROFESSOR: AGENT SCHEDULE OVERVIEW
========================================
9:30 AM Mon-Fri: Portfolio Analyzer runs
9:32 AM Mon-Fri: Market Scout runs (receives Portfolio Analyzer insights)
9:35 AM Mon-Fri: Agent Analysis runs (on updated watchlist)
11:30 AM: Agent Analysis runs
1:30 PM: Agent Analysis runs
3:30 PM: Market closes

See market_hours.py for detailed schedule implementation
========================================
"""
from agents.technical_analyst import TechnicalAnalyst
from agents.sentiment_analyst import SentimentAnalyst
from agents.decision_maker import DecisionMaker
from agents.market_scout import MarketScout
from agents.portfolio_analyzer import PortfolioAnalyzer
from portfolio import Portfolio
from data_fetcher import get_stock_data, get_nse_top_stocks
from market_hours import (
    is_market_open, get_market_status, 
    should_run_portfolio_analyzer, should_run_market_scout, 
    should_run_agent_analysis, get_next_run_times
)
import time
from datetime import datetime

# Track what has already run today to avoid duplicates
last_run_dates = {
    'portfolio_analyzer': None,
    'market_scout': None,
}

def run_portfolio_analyzer(portfolio, current_prices):
    """
    Run Portfolio Analyzer - analyzes portfolio health
    
    ========================================
    PROFESSOR: PORTFOLIO ANALYZER EXECUTION
    Lines 48-60: Runs at 9:30 AM Monday-Friday
    Provides insights about portfolio gaps and risks
    Output used by Market Scout for stock discovery
    ========================================
    """
    print("\n" + "="*70)
    print("🏥 PORTFOLIO ANALYZER - Daily Health Check")
    print("="*70)
    
    analyzer = PortfolioAnalyzer()
    analysis_result = analyzer.analyze_portfolio(portfolio, current_prices)
    
    print(f"\n{analysis_result['analysis']}")
    print(f"\n📊 Key Metrics:")
    print(f"   Total Value: ₹{analysis_result['metrics']['total_value']:,.2f}")
    print(f"   Return: {analysis_result['metrics']['return_pct']:.2f}%")
    print(f"   Positions: {analysis_result['metrics']['num_positions']}")
    print(f"   Cash: {analysis_result['metrics']['cash_pct']:.1f}%")
    
    return analysis_result

def run_market_scout(watchlist, portfolio, current_prices, portfolio_analysis):
    """
    Run Market Scout - discovers stocks and updates watchlist
    
    ========================================
    PROFESSOR: MARKET SCOUT EXECUTION
    Lines 75-100: Runs at 9:32 AM Monday-Friday
    Receives Portfolio Analyzer insights
    Adds new stocks to watchlist
    Removes stocks we don't hold
    Returns updated watchlist
    ========================================
    """
    print("\n" + "="*70)
    print("🔎 MARKET SCOUT - Stock Discovery & Watchlist Update")
    print("="*70)
    
    scout = MarketScout()
    scout_result = scout.discover_and_update_watchlist(
        current_watchlist=watchlist,
        portfolio_holdings=portfolio.holdings,
        portfolio_analysis=portfolio_analysis
    )
    
    # Print action summary
    print(scout_result['action_summary'])
    
    # Return updated watchlist
    return scout_result['updated_watchlist'], scout_result

def run_agent_analysis(watchlist, portfolio):
    """
    Run complete agent analysis on watchlist
    
    ========================================
    PROFESSOR: AGENT ANALYSIS EXECUTION
    Lines 107-180: Runs at 9:35 AM, 11:30 AM, 1:30 PM
    Analyzes all stocks in watchlist
    Makes BUY/HOLD/SELL decisions
    Executes trades automatically
    ========================================
    """
    print("\n" + "="*70)
    print("🤖 AGENT ANALYSIS - Stock Analysis & Trading")
    print("="*70)
    
    # Initialize agents
    tech_agent = TechnicalAnalyst()
    sentiment_agent = SentimentAnalyst()
    decision_agent = DecisionMaker()
    
    # Get current prices
    current_prices = {}
    for symbol in watchlist + list(portfolio.holdings.keys()):
        data = get_stock_data(symbol, days=1)
        if data:
            current_prices[symbol] = data['current_price']
    
    portfolio_value = portfolio.get_portfolio_value(current_prices)
    available_cash = portfolio.cash
    
    print(f"📊 Portfolio: ₹{portfolio_value:,.2f} | Cash: ₹{available_cash:,.2f}")
    print(f"📋 Analyzing {len(watchlist)} stocks...\n")
    
    results = []
    
    for symbol in watchlist:
        print(f"\n{'='*70}")
        print(f"Analyzing: {symbol}")
        print('='*70)
        
        # Bottom Level: Technical + Sentiment Analysis
        technical_result = tech_agent.analyze(symbol)
        time.sleep(1)
        
        sentiment_result = sentiment_agent.analyze(symbol)
        time.sleep(1)
        
        # Top Level: Decision Maker
        decision_result = decision_agent.decide(
            symbol, 
            technical_result, 
            sentiment_result,
            portfolio_value,
            available_cash
        )
        
        # Execute BUY decisions
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
        
        # Execute SELL decisions for holdings
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
    
    portfolio.save()
    return results

def main():
    """
    Main orchestration loop with agent scheduling
    
    ========================================
    PROFESSOR: MAIN CONTROL LOOP
    Lines 200-280: Controls agent execution timing
    Checks market hours and schedules
    Runs agents at specified times only
    ========================================
    """
    print("\n🚀 AI Stock Agent System - NSE")
    print("⏰ Market Hours: 9:30 AM - 3:30 PM IST Monday-Friday")
    print("📅 Agent Schedule:")
    print("   9:30 AM: Portfolio Analyzer")
    print("   9:32 AM: Market Scout")
    print("   9:35 AM: Agent Analysis")
    print("   11:30 AM: Agent Analysis")
    print("   1:30 PM: Agent Analysis\n")
    
    # Initialize
    portfolio = Portfolio(starting_cash=100000)
    portfolio.load()
    
    watchlist = get_nse_top_stocks()[:5]
    portfolio_analysis = None
    
    while True:
        # Check if market is open
        market_open, status_msg = get_market_status()
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"\n{status_msg}")
        
        if not market_open:
            # Show portfolio status
            current_prices = {}
            for symbol in list(portfolio.holdings.keys()) + watchlist:
                data = get_stock_data(symbol, days=1)
                if data:
                    current_prices[symbol] = data['current_price']
            
            summary = portfolio.get_summary(current_prices)
            print(f"\n📊 Portfolio: ₹{summary['total_value']:,.2f} | Return: {summary['return_pct']:.2f}%")
            
            # Show next run times
            next_runs = get_next_run_times()
            print(f"\n⏰ Next Agent Runs:")
            print(f"   Portfolio Analyzer: {next_runs['portfolio_analyzer'].strftime('%a %I:%M %p')}")
            print(f"   Market Scout: {next_runs['market_scout'].strftime('%a %I:%M %p')}")
            print(f"   Agent Analysis: {next_runs['agent_analysis'].strftime('%a %I:%M %p')}")
            
            print(f"\n⏰ Checking again in 10 minutes...")
            time.sleep(600)  # Check every 10 minutes when market closed
            continue
        
        # Market is open - check what should run
        
        # ========================================
        # PROFESSOR: PORTFOLIO ANALYZER TRIGGER
        # Lines 261-272: Checks if 9:30 AM and hasn't run today
        # ========================================
        if should_run_portfolio_analyzer() and last_run_dates['portfolio_analyzer'] != current_date:
            # Get current prices
            current_prices = {}
            for symbol in list(portfolio.holdings.keys()) + watchlist:
                data = get_stock_data(symbol, days=1)
                if data:
                    current_prices[symbol] = data['current_price']
            
            portfolio_analysis = run_portfolio_analyzer(portfolio, current_prices)
            last_run_dates['portfolio_analyzer'] = current_date
            print("\n✅ Portfolio Analyzer completed")
            time.sleep(60)  # Wait before Market Scout
        
        # ========================================
        # PROFESSOR: MARKET SCOUT TRIGGER
        # Lines 277-285: Checks if 9:32 AM and hasn't run today
        # Requires Portfolio Analyzer to have run first
        # ========================================
        if should_run_market_scout() and last_run_dates['market_scout'] != current_date and portfolio_analysis:
            current_prices = {}
            for symbol in list(portfolio.holdings.keys()) + watchlist:
                data = get_stock_data(symbol, days=1)
                if data:
                    current_prices[symbol] = data['current_price']
            
            watchlist, scout_result = run_market_scout(watchlist, portfolio, current_prices, portfolio_analysis)
            last_run_dates['market_scout'] = current_date
            print("\n✅ Market Scout completed")
            print(f"📋 Updated watchlist: {', '.join([s.replace('.NS', '') for s in watchlist])}")
            
            # Immediately trigger Agent Analysis
            print("\n🚀 Triggering Agent Analysis on updated watchlist...")
            time.sleep(30)
            results = run_agent_analysis(watchlist, portfolio)
            print("\n✅ Agent Analysis completed")
        
        # ========================================
        # PROFESSOR: AGENT ANALYSIS TRIGGER
        # Lines 305-310: Checks if 11:30 AM or 1:30 PM
        # Runs on existing watchlist
        # ========================================
        elif should_run_agent_analysis():
            results = run_agent_analysis(watchlist, portfolio)
            print("\n✅ Agent Analysis completed")
            time.sleep(120)  # Wait 2 minutes before next check
        
        # Show next run
        next_runs = get_next_run_times()
        print(f"\n⏰ Next run: {next_runs['agent_analysis'].strftime('%I:%M %p')}")
        
        # Wait before next check (check every minute during market hours)
        time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 System stopped by user")
