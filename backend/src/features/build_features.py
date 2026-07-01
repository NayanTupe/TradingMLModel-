import pandas as pd
import numpy as np

# ======================
# LOAD EQUITY DATA
# ======================
equity_df = pd.read_csv('data/processed/combined_data.csv')
equity_df['date'] = pd.to_datetime(equity_df['date'])
equity_df = equity_df.sort_values(by=['stock', 'date']).reset_index(drop=True)

# ======================
# LOAD OPTIONS DATA
# ======================
option_df = pd.read_csv('data/raw/options/option_data.csv')
# standardize column names
option_df.columns = option_df.columns.str.lower()
option_df['date'] = pd.to_datetime(option_df['timestamp'])

# ======================
# BASIC EQUITY FEATURES
# ======================
equity_df['ma_10'] = equity_df.groupby('stock')['close'].transform(lambda x: x.rolling(10).mean())
equity_df['ma_20'] = equity_df.groupby('stock')['close'].transform(lambda x: x.rolling(20).mean())

def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

equity_df['rsi'] = equity_df.groupby('stock')['close'].transform(calculate_rsi)
equity_df['price_change'] = equity_df.groupby('stock')['close'].pct_change()
equity_df['volatility'] = equity_df['high'] - equity_df['low']
equity_df['momentum'] = equity_df['close'] - equity_df['ma_10']

# ======================
# VWAP
# ======================
equity_df['typical_price'] = (equity_df['high'] + equity_df['low'] + equity_df['close']) / 3
equity_df['tp_volume'] = equity_df['typical_price'] * equity_df['volume']
equity_df['cumulative_tp_volume'] = equity_df.groupby('stock')['tp_volume'].cumsum()
equity_df['cumulative_volume'] = equity_df.groupby('stock')['volume'].cumsum()
equity_df['vwap'] = equity_df['cumulative_tp_volume'] / equity_df['cumulative_volume']

# ======================
# ATR
# ======================
equity_df['prev_close'] = equity_df.groupby('stock')['close'].shift(1)
equity_df['tr1'] = equity_df['high'] - equity_df['low']
equity_df['tr2'] = abs(equity_df['high'] - equity_df['prev_close'])
equity_df['tr3'] = abs(equity_df['low'] - equity_df['prev_close'])
equity_df['true_range'] = equity_df[['tr1', 'tr2', 'tr3']].max(axis=1)
equity_df['atr'] = equity_df.groupby('stock')['true_range'].transform(lambda x: x.rolling(14).mean())

# ======================
# VOLUME SPIKE
# ======================
equity_df['volume_ma_20'] = equity_df.groupby('stock')['volume'].transform(lambda x: x.rolling(20).mean())
equity_df['volume_spike'] = equity_df['volume'] / equity_df['volume_ma_20']

# ======================
# CANDLE BODY %
# ======================
equity_df['candle_range'] = equity_df['high'] - equity_df['low']
equity_df['candle_body_pct'] = np.where(
    equity_df['candle_range'] != 0,
    abs(equity_df['close'] - equity_df['open']) / equity_df['candle_range'],
    0
)

# ======================
# TREND STRENGTH
# ======================
equity_df['trend_strength'] = np.where(
    equity_df['close'] != 0,
    (equity_df['ma_10'] - equity_df['ma_20']) / equity_df['close'],
    0
)

# ======================
# MARKET REGIME
# ======================
equity_df['atr_pct'] = np.where(
    equity_df['close'] != 0,
    equity_df['atr'] / equity_df['close'],
    0
)
equity_df['above_vwap'] = (equity_df['close'] > equity_df['vwap']).astype(int)
equity_df['high_volume'] = (equity_df['volume_spike'] > 1.2).astype(int)
equity_df['uptrend'] = (equity_df['ma_10'] > equity_df['ma_20']).astype(int)

equity_df['market_regime'] = (
    ((equity_df['above_vwap'] == 1) | (equity_df['uptrend'] == 1)) &
    (equity_df['atr_pct'] > 0.0005)
).astype(int)

# ======================
# PREVIOUS DAY HIGH / LOW
# ======================
equity_df['day'] = equity_df['date'].dt.date
daily = equity_df.groupby(['stock', 'day']).agg(day_high=('high', 'max'), day_low=('low', 'min')).reset_index()
daily['prev_day_high'] = daily.groupby('stock')['day_high'].shift(1)
daily['prev_day_low'] = daily.groupby('stock')['day_low'].shift(1)
equity_df = equity_df.merge(daily[['stock', 'day', 'prev_day_high', 'prev_day_low']], on=['stock', 'day'], how='left')
equity_df['near_prev_day_high'] = np.where(equity_df['close'] != 0, (equity_df['close'] - equity_df['prev_day_high']) / equity_df['close'], 0)
equity_df['near_prev_day_low'] = np.where(equity_df['close'] != 0, (equity_df['close'] - equity_df['prev_day_low']) / equity_df['close'], 0)

# ======================
# OPENING RANGE BREAKOUT
# ======================
equity_df['time'] = equity_df['date'].dt.time
opening_range = equity_df.groupby(['stock', 'day']).head(15)
orb = opening_range.groupby(['stock', 'day']).agg(
    opening_range_high=('high', 'max'),
    opening_range_low=('low', 'min')
).reset_index()
equity_df = equity_df.merge(orb, on=['stock', 'day'], how='left')
equity_df['orb_breakout'] = (equity_df['close'] > equity_df['opening_range_high']).astype(int)
equity_df['orb_breakdown'] = (equity_df['close'] < equity_df['opening_range_low']).astype(int)

# ======================
# TARGET
# ======================
equity_df['future_close'] = equity_df.groupby('stock')['close'].shift(-5)
equity_df['target'] = (equity_df['future_close'] > equity_df['close'] * 1.002).astype(int)

# ======================
# FINAL CLEAN
# ======================
equity_df = equity_df.replace([np.inf, -np.inf], 0)
equity_df = equity_df.fillna(0)
equity_df = equity_df.drop(columns=['cumulative_tp_volume', 'cumulative_volume', 'candle_range'], errors='ignore')

# ======================
# SAVE
# ======================
equity_df.to_csv('data/processed/features.csv', index=False)

print("✅ Equity features created with advanced indicators")
print(equity_df['target'].value_counts())
print("Total rows:", len(equity_df))