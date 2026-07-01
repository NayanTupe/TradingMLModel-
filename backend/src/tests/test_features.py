import unittest
import pandas as pd
import numpy as np

class TestFeatures(unittest.TestCase):
    def test_feature_consistency(self):
        # Load features list from saved file
        with open('saved_models/model_features.txt', 'r') as f:
            features = [line.strip() for line in f if line.strip()]
        self.assertEqual(len(features), 20)  # You have 20 features
        # Check that all required features exist
        required = ['ma_10', 'ma_20', 'rsi', 'atr', 'vwap']
        for r in required:
            self.assertIn(r, features)

if __name__ == '__main__':
    unittest.main()