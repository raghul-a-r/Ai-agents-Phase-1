"""
Stock Data Fetcher - Gets historical data and news for NSE stocks
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_stock_data(symbol, days=30):
    """Get historical stock data for analysis (NSE stocks)"""
    try:
        # Ensure NSE suffix for Indian stocks
        if not symbol.endswith('.NS'):
            symbol = f"{symbol}.NS"
        
        stock = yf.Ticker(symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get historical data
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty:
            print(f"No data available for {symbol}")
            return None
        
        # Get current info
        info = stock.info
        
        return {
            'symbol': symbol,
            'history': hist,
            'current_price': info.get('currentPrice', hist['Close'].iloc[-1]),
            'company_name': info.get('longName', symbol),
            'sector': info.get('sector', 'Unknown'),
            'market_cap': info.get('marketCap', 0)
        }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def calculate_rsi(data, period=14):
    """Calculate RSI indicator"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_moving_averages(data):
    """Calculate moving averages"""
    ma_20 = data['Close'].rolling(window=20).mean().iloc[-1]
    ma_50 = data['Close'].rolling(window=50).mean().iloc[-1] if len(data) >= 50 else None
    current = data['Close'].iloc[-1]
    
    return {
        'ma_20': ma_20,
        'ma_50': ma_50,
        'current_price': current,
        'above_ma_20': current > ma_20,
        'above_ma_50': current > ma_50 if ma_50 else None
    }

def get_news_headlines(symbol, count=5):
    """Get recent news for sentiment analysis"""
    try:
        # Ensure NSE suffix
        if not symbol.endswith('.NS'):
            symbol = f"{symbol}.NS"
        
        stock = yf.Ticker(symbol)
        news = stock.news[:count] if hasattr(stock, 'news') else []
        
        if not news:
            # Fallback - use base symbol name for news
            base_symbol = symbol.replace('.NS', '')
            return [f"Check latest {base_symbol} news on financial websites"]
        
        headlines = [item['title'] for item in news]
        return headlines
    except:
        base_symbol = symbol.replace('.NS', '')
        return [f"No recent news available for {base_symbol}"]

def get_technical_summary(symbol, days=30):
    """Get complete technical analysis data"""
    data = get_stock_data(symbol, days)
    if not data:
        return None
    
    hist = data['history']
    rsi = calculate_rsi(hist)
    ma_data = calculate_moving_averages(hist)
    
    # Calculate price change
    price_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
    
    return {
        'symbol': symbol,
        'company_name': data['company_name'],
        'current_price': data['current_price'],
        'rsi': rsi,
        'ma_20': ma_data['ma_20'],
        'ma_50': ma_data['ma_50'],
        'above_ma_20': ma_data['above_ma_20'],
        'above_ma_50': ma_data['above_ma_50'],
        'price_change_30d': price_change,
        'sector': data['sector']
    }

def get_nse_top_stocks():
    """Get popular NSE stocks for initial watchlist"""
    return [
        'RELIANCE.NS',
        'TCS.NS',
        'HDFCBANK.NS',
        'INFY.NS',
        'ICICIBANK.NS',
        'HINDUNILVR.NS',
        'SBIN.NS',
        'BHARTIARTL.NS',
        'ITC.NS',
        'LT.NS'
    ]
