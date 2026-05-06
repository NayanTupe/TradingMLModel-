import pandas as pd
import numpy as np

# ======================
# LOAD DATA
# ======================
df = pd.read_csv('data/processed/combined_data.csv')

df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(by=['stock', 'date'])

# ======================
# BASIC FEATURES
# ======================
df['ma_10'] = df.groupby('stock')['close'].transform(lambda x: x.rolling(10).mean())
df['ma_20'] = df.groupby('stock')['close'].transform(lambda x: x.rolling(20).mean())

def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

df['rsi'] = df.groupby('stock')['close'].transform(calculate_rsi)

df['price_change'] = df.groupby('stock')['close'].pct_change()
df['volatility'] = df['high'] - df['low']
df['momentum'] = df['close'] - df['ma_10']

# ======================
# VWAP
# ======================
df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
df['tp_volume'] = df['typical_price'] * df['volume']

df['vwap'] = (
    df.groupby('stock')['tp_volume'].cumsum() /
    df.groupby('stock')['volume'].cumsum()
)

# ======================
# ATR
# ======================
df['prev_close'] = df.groupby('stock')['close'].shift(1)

df['tr1'] = df['high'] - df['low']
df['tr2'] = abs(df['high'] - df['prev_close'])
df['tr3'] = abs(df['low'] - df['prev_close'])

df['true_range'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)

df['atr'] = df.groupby('stock')['true_range'].transform(
    lambda x: x.rolling(14).mean()
)

# ======================
# VOLUME SPIKE
# ======================
df['volume_ma_20'] = df.groupby('stock')['volume'].transform(
    lambda x: x.rolling(20).mean()
)

df['volume_spike'] = df['volume'] / df['volume_ma_20']

# ======================
# CANDLE BODY %
# ======================
df['candle_body_pct'] = abs(df['close'] - df['open']) / (df['high'] - df['low'])
df['candle_body_pct'] = df['candle_body_pct'].replace([np.inf, -np.inf], 0)

# ======================
# TREND STRENGTH
# ======================
df['trend_strength'] = (df['ma_10'] - df['ma_20']) / df['close']

# ======================
# PREVIOUS DAY HIGH / LOW
# ======================
df['day'] = df['date'].dt.date

daily = df.groupby(['stock', 'day']).agg(
    day_high=('high', 'max'),
    day_low=('low', 'min')
).reset_index()

daily['prev_day_high'] = daily.groupby('stock')['day_high'].shift(1)
daily['prev_day_low'] = daily.groupby('stock')['day_low'].shift(1)

df = df.merge(
    daily[['stock', 'day', 'prev_day_high', 'prev_day_low']],
    on=['stock', 'day'],
    how='left'
)

df['near_prev_day_high'] = (df['close'] - df['prev_day_high']) / df['close']
df['near_prev_day_low'] = (df['close'] - df['prev_day_low']) / df['close']

# ======================
# OPENING RANGE BREAKOUT
# ======================
df['time'] = df['date'].dt.time

opening_range = df.groupby(['stock', 'day']).head(15)

orb = opening_range.groupby(['stock', 'day']).agg(
    opening_range_high=('high', 'max'),
    opening_range_low=('low', 'min')
).reset_index()

df = df.merge(orb, on=['stock', 'day'], how='left')

df['orb_breakout'] = (df['close'] > df['opening_range_high']).astype(int)
df['orb_breakdown'] = (df['close'] < df['opening_range_low']).astype(int)

# ======================
# TARGET
# ======================
df['future_close'] = df.groupby('stock')['close'].shift(-5)

df['target'] = (
    df['future_close'] > df['close'] * 1.002
).astype(int)

# ======================
# CLEAN
# ======================
df = df.dropna()

df.to_csv('data/processed/features.csv', index=False)

print("✅ Features created with advanced free indicators")
print(df['target'].value_counts())
print("Total rows:", len(df))