import pandas as pd
import numpy as np

# ======================
# LOAD DATA
# ======================
df = pd.read_csv("data/processed/features.csv")

print("\n🔍 LEAKAGE CHECK STARTED")

print("\nRows:", len(df))
print("Columns:", len(df.columns))

# ======================
# CHECK 1: Suspicious columns
# ======================
suspicious_keywords = [
    "future",
    "target",
    "next",
    "label",
    "profit",
    "return"
]

suspicious_cols = []

for col in df.columns:
    for word in suspicious_keywords:
        if word.lower() in col.lower():
            suspicious_cols.append(col)

print("\n⚠️ Suspicious Columns:")
print(sorted(set(suspicious_cols)))

# ======================
# CHECK 2: Feature correlation with target
# ======================
features = [
    'ma_10',
    'ma_20',
    'rsi',
    'price_change',
    'volatility',
    'momentum',
    'vwap',
    'atr',
    'volume_spike',
    'candle_body_pct',
    'trend_strength',
    'near_prev_day_high',
    'near_prev_day_low',
    'orb_breakout',
    'orb_breakdown'
]

available_features = [f for f in features if f in df.columns]

clean_df = df[available_features + ['target']].replace([np.inf, -np.inf], np.nan).dropna()

corr = clean_df.corr(numeric_only=True)['target'].sort_values(ascending=False)

print("\n📊 Feature Correlation With Target:")
print(corr)

high_corr = corr[
    (corr.index != 'target') &
    (corr.abs() > 0.50)
]

print("\n🚨 High Correlation Features > 0.50:")
if len(high_corr) == 0:
    print("No very high correlation found.")
else:
    print(high_corr)

# ======================
# CHECK 3: Duplicate rows
# ======================
duplicates = df.duplicated().sum()

print("\n🔁 Duplicate Rows:")
print(duplicates)

# ======================
# CHECK 4: Same date-stock duplicates
# ======================
if 'date' in df.columns and 'stock' in df.columns:
    date_stock_duplicates = df.duplicated(subset=['date', 'stock']).sum()
    print("\n🔁 Duplicate date-stock rows:")
    print(date_stock_duplicates)

# ======================
# CHECK 5: Target distribution
# ======================
print("\n🎯 Target Distribution:")
print(df['target'].value_counts(normalize=True) * 100)
print(df['target'].value_counts())

# ======================
# CHECK 6: Future close leakage
# ======================
if 'future_close' in df.columns:
    print("\n⚠️ future_close exists in features.csv.")
    print("This is okay only if backtest/model drops it before training.")

# ======================
# CHECK 7: Infinite / NaN values
# ======================
inf_count = np.isinf(
    df.select_dtypes(include=[np.number])
).sum().sum()

nan_count = df.isna().sum().sum()

print("\n♾️ Infinite Values:")
print(inf_count)

print("\n🕳️ NaN Values:")
print(nan_count)

# ======================
# CHECK 8: Date range
# ======================
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    print("\n📅 Date Range:")
    print("Start:", df['date'].min())
    print("End:", df['date'].max())

# ======================
# CHECK 9: Stock count
# ======================
if 'stock' in df.columns:
    print("\n📈 Stocks:")
    print(df['stock'].value_counts())

print("\n✅ Leakage check completed")