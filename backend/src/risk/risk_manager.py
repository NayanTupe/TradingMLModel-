"""
Risk management: daily loss limit, max drawdown, position sizing.
"""

import logging

class RiskManager:
    def __init__(self, config):
        self.max_daily_loss = config['risk']['max_daily_loss']
        self.max_drawdown_pct = config['risk']['max_drawdown_pct']
        self.max_position_value = config['risk']['max_position_value']
        self.max_concurrent_trades = config['risk']['max_concurrent_trades']
        
        self.daily_pnl = 0.0
        self.peak_equity = 0.0
        self.current_trades = 0
        self.logger = logging.getLogger(__name__)
    
    def update_equity(self, current_equity):
        """Update peak equity for drawdown calculation."""
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity
    
    def daily_reset(self):
        """Reset daily PnL at start of new trading day."""
        self.daily_pnl = 0.0
    
    def can_enter_trade(self, current_equity, confidence):
        """Check if new trade is allowed."""
        # Drawdown limit
        if self.peak_equity > 0:
            drawdown = (self.peak_equity - current_equity) / self.peak_equity
            if drawdown >= self.max_drawdown_pct:
                self.logger.warning(f"Max drawdown reached: {drawdown:.2%}")
                return False, "max_drawdown"
        
        # Daily loss limit
        if self.daily_pnl <= -self.max_daily_loss:
            self.logger.warning(f"Daily loss limit reached: {self.daily_pnl}")
            return False, "daily_loss_limit"
        
        # Concurrent trades limit
        if self.current_trades >= self.max_concurrent_trades:
            self.logger.warning(f"Max concurrent trades reached: {self.current_trades}")
            return False, "max_concurrent"
        
        # Confidence filter (optional, could be part of strategy)
        if confidence < 0.50:
            return False, "low_confidence"
        
        return True, "ok"
    
    def record_trade_result(self, pnl):
        """Update daily PnL after a trade closes."""
        self.daily_pnl += pnl
        self.current_trades -= 1
        self.logger.info(f"Trade result: {pnl:.2f}, Daily PnL: {self.daily_pnl:.2f}")
    
    def open_trade(self):
        """Increment open trades counter."""
        self.current_trades += 1