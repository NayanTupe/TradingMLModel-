# buy/sell logic
"""
Trading strategy logic: signal generation, entry/exit conditions.
Assumes model confidence output is already available.
"""

import pandas as pd
import numpy as np
from datetime import timedelta

class TradingStrategy:
    def __init__(self, config):
        """
        config: dict from strategy_config.yaml
        """
        self.confidence_threshold = config['strategy']['confidence_threshold']
        self.stop_loss_pct = config['strategy']['stop_loss_pct']
        self.target_pct = config['strategy']['target_pct']
        self.max_hold_minutes = config['strategy']['max_hold_minutes']
    
    def generate_signals(self, df_predictions):
        """
        df_predictions: DataFrame with columns: date, stock, close, confidence
        Returns: DataFrame with signals (1 = BUY, 0 = NO TRADE)
        """
        df = df_predictions.copy()
        df['signal'] = 0
        df.loc[df['confidence'] >= self.confidence_threshold, 'signal'] = 1
        return df
    
    def should_exit(self, entry_price, current_price, entry_time, current_time):
        """
        Check if trade should exit based on stop loss, target, or time.
        """
        pnl_pct = (current_price - entry_price) / entry_price
        # Stop loss hit
        if pnl_pct <= -self.stop_loss_pct:
            return True, "stop_loss"
        # Target hit
        if pnl_pct >= self.target_pct:
            return True, "target"
        # Time exit
        hold_duration = (current_time - entry_time).total_seconds() / 60
        if hold_duration >= self.max_hold_minutes:
            return True, "time_exit"
        return False, None
    
    def calculate_position_size(self, capital, price, confidence, risk_per_trade_pct=0.02):
        """
        Fixed fraction position sizing based on risk per trade.
        """
        risk_amount = capital * risk_per_trade_pct
        stop_loss_in_rupees = price * self.stop_loss_pct
        if stop_loss_in_rupees <= 0:
            return 0
        quantity = int(risk_amount / stop_loss_in_rupees)
        # Cap quantity by available capital
        max_qty = int(capital / price)
        quantity = min(quantity, max_qty)
        return max(quantity, 0)