import pandas as pd

# Load data
df = pd.read_csv('data/processed/combined_data.csv')

# Convert date
df['date'] = pd.to_datetime(df['date'])

# Sort
df = df.sort_values(by=['stock', 'date'])

# ======================
# Moving Average
# ======================
df['ma_10'] = df.groupby('stock')['close'].transform(lambda x: x.rolling(10).mean())
df['ma_20'] = df.groupby('stock')['close'].transform(lambda x: x.rolling(20).mean())

# ======================
# RSI
# ======================
def calculate_rsi(series, window=14):
    delta = series.diff()

    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()

    rs = gain / loss
    return 100 - (100 / (1 + rs))

df['rsi'] = df.groupby('stock')['close'].transform(calculate_rsi)

# ======================
# FEATURES
# ======================
df['price_change'] = df.groupby('stock')['close'].pct_change()
df['volatility'] = df['high'] - df['low']
df['momentum'] = df['close'] - df['ma_10']

# ======================
# TARGET (LESS NOISE)
# ======================
# Predict next 5 candles (5 minutes)
df['future_close'] = df.groupby('stock')['close'].shift(-5)

# Smaller threshold (0.2%)
df['target'] = (df['future_close'] > df['close'] * 1.002).astype(int)
# ======================
# Clean
# ======================
df = df.dropna()

# Save
df.to_csv('data/processed/features.csv', index=False)

print("✅ Features created")
print(df['target'].value_counts())