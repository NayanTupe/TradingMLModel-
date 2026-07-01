import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# ======================
# LOAD FEATURES
# ======================
df = pd.read_csv('data/processed/features.csv')

# Recent data only
df = df.tail(100000).reset_index(drop=True)

# Clean values
df = df.replace([np.inf, -np.inf], 0)
df = df.fillna(0)

# ======================
# REMOVE LEAKAGE
# ======================
leakage_cols = [
    'future_close',
    'future_high',
    'future_low'
]

for col in leakage_cols:
    if col in df.columns:
        df = df.drop(columns=[col])

# ======================
# FEATURES
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
    'orb_breakdown',
    'atr_pct',
    'above_vwap',
    'high_volume',
    'uptrend',
    'market_regime'
]

X = df[features]
y = df['target']

# ======================
# TRAIN TEST SPLIT
# ======================
split_index = int(len(df) * 0.8)

X_train = X.iloc[:split_index]
X_live = X.iloc[split_index:]

y_train = y.iloc[:split_index]

live_df = df.iloc[split_index:].copy().reset_index(drop=True)

# ======================
# MODEL
# ======================
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_leaf=8,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# ======================
# LIVE CONFIDENCE
# ======================
proba = model.predict_proba(X_live)

live_df['confidence'] = proba[:, 1]

# ======================
# PAPER TRADING SETTINGS
# ======================
confidence_threshold = 0.50

# ======================
# SIGNAL GENERATION
# ======================
signals = []

for _, row in live_df.tail(20).iterrows():

    signal = "NO TRADE"

    if (
        row['confidence'] >= confidence_threshold and
        row['market_regime'] == 1
    ):

        signal = "BUY"

    signals.append({
        "date": row['date'],
        "stock": row['stock'],
        "close": round(row['close'], 2),
        "confidence": round(row['confidence'], 4),
        "market_regime": row['market_regime'],
        "signal": signal
    })

# ======================
# SIGNAL OUTPUT
# ======================
signals_df = pd.DataFrame(signals)

print("\n📡 PAPER TRADING SIGNALS")
print(signals_df.to_string(index=False))

# ======================
# SAVE
# ======================
signals_df.to_csv(
    'trade_logs/paper_trading_signals.csv',
    index=False
)

print("\n✅ Saved paper trading signals")

print(
    "trade_logs/paper_trading_signals.csv"
)