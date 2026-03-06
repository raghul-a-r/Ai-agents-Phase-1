"""
Decision Maker Agent - Makes final BUY/HOLD/SELL decisions (₹ Rupees)
"""
import sys
sys.path.append('..')
from ai_client import call_ai

class DecisionMaker:
    def __init__(self):
        self.name = "Decision Maker"
        
    def decide(self, symbol, technical_analysis, sentiment_analysis, portfolio_value, available_cash):
        """Make final investment decision based on both analyses"""
        print(f"\n⚖️  {self.name} deciding on {symbol}...")
        
        system_prompt = """You are the Decision Maker AI agent for Indian stock market (NSE). 
You make final investment decisions in Indian Rupees (₹).

Your job: Synthesize technical and sentiment analysis to make BUY/HOLD/SELL decisions.

Decision Rules:
- BUY: Strong technical + positive sentiment, good risk/reward
- HOLD: Mixed signals or already own it, wait for clarity
- SELL: Weak technical or negative sentiment, cut losses

Be decisive and clear. Format your response as:

DECISION: [BUY/HOLD/SELL]
CONFIDENCE: [HIGH/MEDIUM/LOW]
REASONING: [2-3 sentences]
ALLOCATION: [₹ amount if BUY]"""
        
        user_prompt = f"""Make an investment decision for {symbol}:

=== TECHNICAL ANALYSIS ===
{technical_analysis['analysis']}

=== SENTIMENT ANALYSIS ===
{sentiment_analysis['analysis']}

=== PORTFOLIO INFO ===
Total Portfolio Value: ₹{portfolio_value:,.2f}
Available Cash: ₹{available_cash:,.2f}

Provide your decision (BUY/HOLD/SELL) with clear reasoning."""
        
        decision = call_ai(system_prompt, user_prompt, temperature=0.2)
        
        return {
            'agent': self.name,
            'symbol': symbol,
            'decision': decision,
            'technical_input': technical_analysis,
            'sentiment_input': sentiment_analysis
        }
