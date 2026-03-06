"""
Sentiment Analyst Agent - Analyzes news and market sentiment
"""
import sys
sys.path.append('..')
from ai_client import call_ai
from data_fetcher import get_news_headlines

class SentimentAnalyst:
    def __init__(self):
        self.name = "Sentiment Analyst"
        
    def analyze(self, symbol):
        """Analyze news sentiment for a stock"""
        print(f"\n📰 {self.name} analyzing {symbol}...")
        
        # Get news headlines
        headlines = get_news_headlines(symbol, count=5)
        
        # Create analysis prompt
        system_prompt = """You are a Sentiment Analyst AI agent for Indian stock market (NSE). 
Analyze news headlines and market sentiment.
Rate sentiment as POSITIVE/NEGATIVE/NEUTRAL and provide reasoning.
Consider: news tone, market impact, investor sentiment."""
        
        user_prompt = f"""Analyze sentiment for {symbol} based on these recent headlines:

Headlines:
{chr(10).join([f"- {h}" for h in headlines])}

Provide sentiment analysis with overall rating (POSITIVE/NEGATIVE/NEUTRAL) and key insights."""
        
        analysis = call_ai(system_prompt, user_prompt, temperature=0.3)
        
        return {
            'agent': self.name,
            'symbol': symbol,
            'headlines': headlines,
            'analysis': analysis
        }
