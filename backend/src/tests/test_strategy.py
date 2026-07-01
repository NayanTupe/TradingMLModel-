import unittest
import pandas as pd
import sys
sys.path.append('.')
from src.strategy.strategy import TradingStrategy

class TestStrategy(unittest.TestCase):
    def setUp(self):
        config = {
            'strategy': {
                'confidence_threshold': 0.5,
                'stop_loss_pct': 0.0025,
                'target_pct': 0.007,
                'max_hold_minutes': 45
            }
        }
        self.strategy = TradingStrategy(config)
    
    def test_generate_signals(self):
        df = pd.DataFrame({
            'date': pd.date_range('2025-01-01', periods=5),
            'stock': ['TCS']*5,
            'close': [100]*5,
            'confidence': [0.2, 0.6, 0.55, 0.49, 0.8]
        })
        signals = self.strategy.generate_signals(df)
        expected = [0,1,1,0,1]
        self.assertEqual(list(signals['signal']), expected)
    
    def test_should_exit(self):
        entry_price = 100
        entry_time = pd.Timestamp('2025-01-01 09:15:00')
        # Stop loss
        exit_reason = self.strategy.should_exit(entry_price, 99.75, entry_time, entry_time + pd.Timedelta(minutes=10))
        self.assertEqual(exit_reason[1], 'stop_loss')
        # Target
        exit_reason = self.strategy.should_exit(entry_price, 100.7, entry_time, entry_time + pd.Timedelta(minutes=10))
        self.assertEqual(exit_reason[1], 'target')
        # Time exit
        exit_reason = self.strategy.should_exit(entry_price, 100.2, entry_time, entry_time + pd.Timedelta(minutes=60))
        self.assertEqual(exit_reason[1], 'time_exit')
    
    def test_position_size(self):
        qty = self.strategy.calculate_position_size(100000, 100, 0.75, 0.02)
        self.assertGreater(qty, 0)
        self.assertLessEqual(qty, 1000)  # max 1000 shares

if __name__ == '__main__':
    unittest.main()