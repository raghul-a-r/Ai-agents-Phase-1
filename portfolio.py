"""
Portfolio Simulator - Tracks holdings and simulates trades (in ₹ Rupees)
"""
import json
from datetime import datetime

class Portfolio:
    def __init__(self, starting_cash=100000):  # Default ₹1,00,000
        self.cash = starting_cash
        self.holdings = {}  # {symbol: {'shares': X, 'avg_price': Y}}
        self.history = []
        self.starting_value = starting_cash
        self.hold_mode = False  # For HOLD command
        
    def buy(self, symbol, shares, price):
        """Buy shares of a stock"""
        if self.hold_mode:
            return False, "HOLD mode active - buying paused"
        
        cost = shares * price
        if cost > self.cash:
            return False, "Insufficient funds"
        
        self.cash -= cost
        
        if symbol in self.holdings:
            # Update average price
            old_shares = self.holdings[symbol]['shares']
            old_avg = self.holdings[symbol]['avg_price']
            new_shares = old_shares + shares
            new_avg = ((old_shares * old_avg) + (shares * price)) / new_shares
            self.holdings[symbol] = {'shares': new_shares, 'avg_price': new_avg}
        else:
            self.holdings[symbol] = {'shares': shares, 'avg_price': price}
        
        self.history.append({
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'action': 'BUY',
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'total': cost
        })
        
        return True, f"Bought {shares} shares of {symbol} at ₹{price:.2f}"
    
    def sell(self, symbol, shares, price):
        """Sell shares of a stock"""
        if symbol not in self.holdings:
            return False, "Don't own this stock"
        
        if self.holdings[symbol]['shares'] < shares:
            return False, "Insufficient shares"
        
        proceeds = shares * price
        self.cash += proceeds
        
        self.holdings[symbol]['shares'] -= shares
        if self.holdings[symbol]['shares'] == 0:
            del self.holdings[symbol]
        
        self.history.append({
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'action': 'SELL',
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'total': proceeds
        })
        
        return True, f"Sold {shares} shares of {symbol} at ₹{price:.2f}"
    
    def sell_all(self, current_prices):
        """Liquidate entire portfolio"""
        results = []
        for symbol in list(self.holdings.keys()):
            price = current_prices.get(symbol, 0)
            if price > 0:
                shares = self.holdings[symbol]['shares']
                success, msg = self.sell(symbol, shares, price)
                results.append(msg)
        return results
    
    def get_portfolio_value(self, current_prices):
        """Calculate total portfolio value"""
        holdings_value = sum(
            self.holdings[symbol]['shares'] * current_prices.get(symbol, 0)
            for symbol in self.holdings
        )
        return self.cash + holdings_value
    
    def get_summary(self, current_prices):
        """Get portfolio summary"""
        total_value = self.get_portfolio_value(current_prices)
        holdings_value = total_value - self.cash
        
        return {
            'cash': self.cash,
            'holdings_value': holdings_value,
            'total_value': total_value,
            'holdings': self.holdings,
            'return_pct': ((total_value - self.starting_value) / self.starting_value) * 100,
            'return_rupees': total_value - self.starting_value,
            'hold_mode': self.hold_mode
        }
    
    def save(self, filename='portfolio.json'):
        """Save portfolio to file"""
        data = {
            'cash': self.cash,
            'holdings': self.holdings,
            'history': self.history,
            'starting_value': self.starting_value,
            'hold_mode': self.hold_mode
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filename='portfolio.json'):
        """Load portfolio from file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.cash = data['cash']
                self.holdings = data['holdings']
                self.history = data['history']
                self.starting_value = data.get('starting_value', 100000)
                self.hold_mode = data.get('hold_mode', False)
            return True
        except FileNotFoundError:
            return False
