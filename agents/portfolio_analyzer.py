"""
Portfolio Analyzer Agent - Analyzes portfolio health and risk (Fifth Agent)
Runs at 9:30 AM Monday-Friday to provide insights to Market Scout
"""
import sys
sys.path.append('..')
from ai_client import call_ai

class PortfolioAnalyzer:
    def __init__(self):
        self.name = "Portfolio Analyzer"
        
    def analyze_portfolio(self, portfolio, current_prices):
        """
        Analyze overall portfolio health and provide insights
        
        This runs at 9:30 AM Monday-Friday (see market_hours.py line 58)
        Provides insights to Market Scout for stock discovery
        """
        print(f"\n📊 {self.name} analyzing portfolio...")
        
        summary = portfolio.get_summary(current_prices)
        
        # Calculate detailed metrics
        holdings_list = []
        for symbol, info in portfolio.holdings.items():
            current_price = current_prices.get(symbol, 0)
            current_value = info['shares'] * current_price
            allocation_pct = (current_value / summary['total_value']) * 100 if summary['total_value'] > 0 else 0
            gain = current_value - (info['shares'] * info['avg_price'])
            gain_pct = (gain / (info['shares'] * info['avg_price'])) * 100 if info['avg_price'] > 0 else 0
            
            holdings_list.append({
                'symbol': symbol,
                'shares': info['shares'],
                'avg_price': info['avg_price'],
                'current_price': current_price,
                'value': current_value,
                'allocation_pct': allocation_pct,
                'gain': gain,
                'gain_pct': gain_pct
            })
        
        # Create analysis prompt
        system_prompt = """You are a Portfolio Analyzer AI agent for Indian stock market.
Analyze portfolio health, risk, and performance.

IMPORTANT: Your analysis will be used by Market Scout to discover new stocks.
Identify gaps in diversification and sectors that need more exposure.

Provide actionable insights on:
- Diversification and concentration risk
- Sector exposure gaps
- Performance analysis
- What types of stocks should be added

Be concise and specific. Use Indian Rupees (₹)."""
        
        holdings_summary = "\n".join([
            f"- {h['symbol']}: {h['allocation_pct']:.1f}% of portfolio, Gain: ₹{h['gain']:.2f} ({h['gain_pct']:.2f}%)"
            for h in holdings_list
        ]) if holdings_list else "No holdings"
        
        user_prompt = f"""Analyze this portfolio and suggest what to look for in new stocks:

Total Value: ₹{summary['total_value']:,.2f}
Cash: ₹{summary['cash']:,.2f} ({(summary['cash']/summary['total_value']*100):.1f}%)
Holdings Value: ₹{summary['holdings_value']:,.2f}
Overall Return: ₹{summary['return_rupees']:,.2f} ({summary['return_pct']:.2f}%)
Number of Positions: {len(portfolio.holdings)}

Holdings:
{holdings_summary}

Provide:
1. RISK ASSESSMENT (concentration, diversification)
2. SECTOR GAPS (what sectors are missing or underrepresented)
3. RECOMMENDATIONS (what type of stocks to add to improve portfolio)
4. OVERALL HEALTH SCORE (1-10)"""
        
        analysis = call_ai(system_prompt, user_prompt, temperature=0.3)
        
        return {
            'agent': self.name,
            'analysis': analysis,
            'metrics': {
                'total_value': summary['total_value'],
                'return_pct': summary['return_pct'],
                'cash_pct': (summary['cash']/summary['total_value']*100) if summary['total_value'] > 0 else 0,
                'num_positions': len(portfolio.holdings),
                'largest_position_pct': max([h['allocation_pct'] for h in holdings_list]) if holdings_list else 0
            },
            'holdings_list': holdings_list
        }
    
    def explain_decision(self, symbol, decision_result):
        """Explain why agent made a specific decision"""
        print(f"\n🔍 {self.name} explaining decision for {symbol}...")
        
        system_prompt = """You are a Portfolio Analyzer AI agent.
Explain investment decisions in simple terms for non-experts.
Break down the reasoning clearly."""
        
        user_prompt = f"""Explain why the agents decided this for {symbol}:

TECHNICAL ANALYSIS:
{decision_result['technical_input']['analysis']}

SENTIMENT ANALYSIS:
{decision_result['sentiment_input']['analysis']}

FINAL DECISION:
{decision_result['decision']}

Explain in simple terms:
1. What the technical indicators showed
2. What the market sentiment was
3. Why the final decision was made
4. What risks were considered"""
        
        explanation = call_ai(system_prompt, user_prompt, temperature=0.3)
        
        return {
            'agent': self.name,
            'symbol': symbol,
            'explanation': explanation
        }
