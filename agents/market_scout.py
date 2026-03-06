"""
Market Scout Agent - Discovers trending NSE stocks and manages watchlist (Fourth Agent)
Runs ONCE per day at 9:32 AM after Portfolio Analyzer
Receives portfolio insights and manages watchlist intelligently
"""
import sys
sys.path.append('..')
from ai_client import call_ai

class MarketScout:
    def __init__(self):
        self.name = "Market Scout"
        self.action_log = []  # Track what was added/removed and why
        
    def discover_and_update_watchlist(self, current_watchlist, portfolio_holdings, portfolio_analysis):
        """
        Discover new stocks and update watchlist based on portfolio insights
        
        This runs at 9:32 AM Monday-Friday (see market_hours.py line 89)
        Receives insights from Portfolio Analyzer
        Adds new stocks and removes stocks we don't hold
        
        Args:
            current_watchlist: List of stock symbols currently being watched
            portfolio_holdings: Dict of stocks we actually own
            portfolio_analysis: Insights from Portfolio Analyzer
        
        Returns:
            dict with updated watchlist, additions, removals, and reasoning
        """
        print(f"\n🔎 {self.name} analyzing portfolio and discovering stocks...")
        print(f"Current watchlist size: {len(current_watchlist)}")
        print(f"Current holdings: {len(portfolio_holdings)}")
        
        # Identify stocks in watchlist that we don't hold
        stocks_to_potentially_remove = [
            s for s in current_watchlist 
            if s not in portfolio_holdings
        ]
        
        # AI-powered stock discovery
        system_prompt = """You are the Market Scout AI agent for Indian stock market (NSE).

Your job: 
1. Analyze portfolio insights to identify gaps
2. Suggest 2-3 NEW trending NSE stocks that fill those gaps
3. Decide which watchlist stocks to REMOVE (stocks we don't own anymore)

Focus on:
- Sector diversification based on portfolio gaps
- Stocks with good momentum and fundamentals
- Liquid large-cap NSE stocks only
- Remove underperforming stocks we don't hold

Format your response EXACTLY as:

STOCKS TO ADD:
1. [SYMBOL].NS - [Reason why this fills portfolio gap]
2. [SYMBOL].NS - [Reason]

STOCKS TO REMOVE:
1. [SYMBOL].NS - [Reason why removing]

REASONING:
[2-3 sentences explaining overall strategy]"""
        
        # Prepare portfolio context
        holdings_list = ", ".join([s.replace('.NS', '') for s in portfolio_holdings.keys()]) if portfolio_holdings else "None"
        watchlist_no_holdings = ", ".join([s.replace('.NS', '') for s in stocks_to_potentially_remove])
        
        user_prompt = f"""Analyze portfolio and update watchlist:

=== PORTFOLIO INSIGHTS ===
{portfolio_analysis['analysis']}

=== CURRENT STATE ===
Watchlist: {', '.join([s.replace('.NS', '') for s in current_watchlist])}
Holdings: {holdings_list}
Watchlist stocks we DON'T own: {watchlist_no_holdings}

=== YOUR TASK ===
1. Suggest 2-3 NEW stocks that address portfolio gaps
2. Decide which stocks to REMOVE from watchlist (focus on stocks we don't own)
3. Max watchlist size: 10 stocks

Provide recommendations following the exact format above."""
        
        ai_response = call_ai(system_prompt, user_prompt, temperature=0.7)
        
        # Parse AI response
        additions = []
        removals = []
        reasoning = ""
        
        lines = ai_response.split('\n')
        current_section = None
        
        for line in lines:
            line_upper = line.upper().strip()
            
            if 'STOCKS TO ADD' in line_upper:
                current_section = 'add'
                continue
            elif 'STOCKS TO REMOVE' in line_upper:
                current_section = 'remove'
                continue
            elif 'REASONING' in line_upper:
                current_section = 'reasoning'
                continue
            
            if current_section == 'add' and '.NS' in line.upper():
                # Extract symbol
                parts = line.split('-')
                if len(parts) >= 2:
                    symbol_part = parts[0].strip()
                    reason_part = '-'.join(parts[1:]).strip()
                    # Clean symbol
                    for word in symbol_part.split():
                        if '.NS' in word.upper():
                            symbol = word.strip('.,!?').upper()
                            if not symbol.endswith('.NS'):
                                symbol = f"{symbol.split('.')[0]}.NS"
                            additions.append({'symbol': symbol, 'reason': reason_part})
                            break
            
            elif current_section == 'remove' and '.NS' in line.upper():
                # Extract symbol
                parts = line.split('-')
                if len(parts) >= 2:
                    symbol_part = parts[0].strip()
                    reason_part = '-'.join(parts[1:]).strip()
                    # Clean symbol
                    for word in symbol_part.split():
                        if '.NS' in word.upper():
                            symbol = word.strip('.,!?').upper()
                            if not symbol.endswith('.NS'):
                                symbol = f"{symbol.split('.')[0]}.NS"
                            removals.append({'symbol': symbol, 'reason': reason_part})
                            break
            
            elif current_section == 'reasoning':
                reasoning += line + "\n"
        
        # Fallback if parsing fails
        if not additions:
            print("⚠️ AI parsing failed, using fallback stocks")
            fallback_stocks = [
                {'symbol': 'WIPRO.NS', 'reason': 'IT sector diversification'},
                {'symbol': 'BAJFINANCE.NS', 'reason': 'Financial services exposure'},
            ]
            additions = [s for s in fallback_stocks if s['symbol'] not in current_watchlist][:2]
        
        # Apply changes to watchlist
        updated_watchlist = current_watchlist.copy()
        
        # Remove stocks
        actually_removed = []
        for removal in removals:
            if removal['symbol'] in updated_watchlist:
                # Only remove if we don't own it
                if removal['symbol'] not in portfolio_holdings:
                    updated_watchlist.remove(removal['symbol'])
                    actually_removed.append(removal)
                    print(f"❌ Removed {removal['symbol']}: {removal['reason']}")
        
        # Add new stocks
        actually_added = []
        for addition in additions:
            if addition['symbol'] not in updated_watchlist and len(updated_watchlist) < 10:
                updated_watchlist.append(addition['symbol'])
                actually_added.append(addition)
                print(f"✅ Added {addition['symbol']}: {addition['reason']}")
        
        # Create action log entry
        action_summary = f"""
=== MARKET SCOUT ACTIONS ===

ADDED TO WATCHLIST:
{chr(10).join([f"• {a['symbol'].replace('.NS', '')}: {a['reason']}" for a in actually_added]) if actually_added else "• None"}

REMOVED FROM WATCHLIST:
{chr(10).join([f"• {r['symbol'].replace('.NS', '')}: {r['reason']}" for r in actually_removed]) if actually_removed else "• None"}

OVERALL STRATEGY:
{reasoning.strip()}

Updated watchlist size: {len(updated_watchlist)} stocks
"""
        
        self.action_log.append({
            'timestamp': str(datetime.now()),
            'additions': actually_added,
            'removals': actually_removed,
            'reasoning': reasoning.strip()
        })
        
        return {
            'agent': self.name,
            'updated_watchlist': updated_watchlist,
            'additions': actually_added,
            'removals': actually_removed,
            'reasoning': ai_response,
            'action_summary': action_summary,
            'portfolio_context': portfolio_analysis
        }
    
    def get_action_log(self):
        """Get history of watchlist changes"""
        return self.action_log


from datetime import datetime
