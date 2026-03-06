"""
Technical Analyst Agent - Analyzes stock technical indicators (₹ Rupees)
"""
import sys
sys.path.append('..')
from ai_client import call_ai
from data_fetcher import get_technical_summary

class TechnicalAnalyst:
    def __init__(self):
        self.name = "Technical Analyst"
        
    def analyze(self, symbol):
        """Analyze technical indicators for a stock"""
        print(f"\n🔍 {self.name} analyzing {symbol}...")
        
        # Get technical data
        tech_data = get_technical_summary(symbol)
        if not tech_data:
            return {
                'agent': self.name,
                'symbol': symbol,
                'data': None,
                'analysis': f"Unable to fetch data for {symbol}"
            }
        
        # Format 50-day MA properly (might be None)
        ma_50_str = f"₹{tech_data['ma_50']:.2f}" if tech_data['ma_50'] is not None else 'N/A'
        above_ma_50_str = str(tech_data['above_ma_50']) if tech_data['above_ma_50'] is not None else 'N/A'
        
        # Create analysis prompt
        system_prompt = """You are a Technical Analyst AI agent for Indian stock market (NSE). 
Analyze stock technical indicators and provide clear recommendations.
Focus on: RSI, Moving Averages, Price Trends.
Be concise and actionable. Format: BULLISH/BEARISH/NEUTRAL + reasoning.
Currency is in Indian Rupees (₹)."""
        
        user_prompt = f"""Analyze this NSE stock:

Symbol: {tech_data['symbol']}
Company: {tech_data['company_name']}
Current Price: ₹{tech_data['current_price']:.2f}
RSI (14): {tech_data['rsi']:.2f}
20-Day MA: ₹{tech_data['ma_20']:.2f}
50-Day MA: {ma_50_str}
Above 20-MA: {tech_data['above_ma_20']}
Above 50-MA: {above_ma_50_str}
30-Day Price Change: {tech_data['price_change_30d']:.2f}%
Sector: {tech_data['sector']}

Provide technical analysis with BUY/HOLD/SELL recommendation."""
        
        analysis = call_ai(system_prompt, user_prompt, temperature=0.3)
        
        return {
            'agent': self.name,
            'symbol': symbol,
            'data': tech_data,
            'analysis': analysis
        }
