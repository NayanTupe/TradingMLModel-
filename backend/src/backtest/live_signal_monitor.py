import pandas as pd
import numpy as np
import time
from sklearn.ensemble import RandomForestClassifier

# ======================
# LOAD DATA
# ======================
df = pd.read_csv('data/processed/features.csv')

# Use latest rows
df = df.tail(100000).reset_index(drop=True)

# Clean invalid values
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
# SETTINGS
# ======================
confidence_threshold = 0.50

stop_loss_pct = 0.0025
target_pct = 0.007

hold_candles = 45

capital_per_trade = 100000

# Demo speed
monitor_rows = 300
sleep_seconds = 0.2

# ======================
# POSITION STATE
# ======================
position_open = False

entry_price = None
entry_index = None
entry_date = None
entry_stock = None

quantity = 0

stop_loss_price = None
target_price = None

# ======================
# LIVE TRADE LOGS
# ======================
live_trade_logs = []

# ======================
# START
# ======================
print("\n🚀 POSITION-AWARE LIVE SIGNAL MONITOR STARTED")
print("Mode: Paper Trading Simulation")
print("-" * 60)

# ======================
# LIVE LOOP
# ======================
for i in range(min(monitor_rows, len(live_df))):

    row = live_df.iloc[i]

    current_features = pd.DataFrame(
        [row[features].values],
        columns=features
    )

    confidence = model.predict_proba(
        current_features
    )[0][1]

    # ======================
    # OPEN POSITION
    # ======================
    if position_open:

        exit_reason = None
        exit_price = None

        # STOP LOSS
        if row['low'] <= stop_loss_price:

            exit_price = stop_loss_price
            exit_reason = "STOP LOSS"

        # TARGET
        elif row['high'] >= target_price:

            exit_price = target_price
            exit_reason = "TARGET"

        # TIME EXIT
        elif i - entry_index >= hold_candles:

            exit_price = row['close']
            exit_reason = "TIME EXIT"

        # ======================
        # EXIT TRADE
        # ======================
        if exit_reason:

            gross_profit = (
                (exit_price - entry_price)
                * quantity
            )

            # SAVE EXIT LOG
            live_trade_logs.append({
                "date": row['date'],
                "stock": entry_stock,
                "action": exit_reason,
                "price": round(exit_price, 2),
                "confidence": round(confidence, 4),
                "pnl": round(gross_profit, 2)
            })

            print(
                f"\n❌ EXIT | "
                f"{row['date']} | "
                f"{entry_stock} | "
                f"Reason: {exit_reason} | "
                f"Entry: {round(entry_price, 2)} | "
                f"Exit: {round(exit_price, 2)} | "
                f"Qty: {quantity} | "
                f"PnL: {round(gross_profit, 2)}"
            )

            # RESET POSITION
            position_open = False

            entry_price = None
            entry_index = None
            entry_date = None
            entry_stock = None

            quantity = 0

            stop_loss_price = None
            target_price = None

        # ======================
        # HOLD POSITION
        # ======================
        else:

            print(
                f"\n📌 HOLD | "
                f"{row['date']} | "
                f"{entry_stock} | "
                f"Close: {round(row['close'], 2)} | "
                f"SL: {round(stop_loss_price, 2)} | "
                f"Target: {round(target_price, 2)}"
            )

    # ======================
    # NO POSITION
    # ======================
    else:

        if (
            confidence >= confidence_threshold and
            row['market_regime'] == 1
        ):

            # ENTRY
            entry_price = row['close']

            entry_index = i
            entry_date = row['date']
            entry_stock = row['stock']

            quantity = int(
                capital_per_trade / entry_price
            )

            stop_loss_price = (
                entry_price *
                (1 - stop_loss_pct)
            )

            target_price = (
                entry_price *
                (1 + target_pct)
            )

            position_open = True

            # SAVE BUY LOG
            live_trade_logs.append({
                "date": row['date'],
                "stock": entry_stock,
                "action": "BUY",
                "price": round(entry_price, 2),
                "confidence": round(confidence, 4),
                "pnl": 0
            })

            print(
                f"\n🟢 BUY | "
                f"{row['date']} | "
                f"{entry_stock} | "
                f"Entry: {round(entry_price, 2)} | "
                f"Qty: {quantity} | "
                f"Confidence: {round(confidence, 4)} | "
                f"SL: {round(stop_loss_price, 2)} | "
                f"Target: {round(target_price, 2)}"
            )

        else:

            print(
                f"\n⚪ NO TRADE | "
                f"{row['date']} | "
                f"{row['stock']} | "
                f"Close: {round(row['close'], 2)} | "
                f"Confidence: {round(confidence, 4)} | "
                f"Market Regime: {row['market_regime']}"
            )

    # Simulate live feed
    time.sleep(sleep_seconds)

# ======================
# SAVE LOGS
# ======================
logs_df = pd.DataFrame(live_trade_logs)

logs_df.to_csv(
    'trade_logs/live_trade_monitor_logs.csv',
    index=False
)

# ======================
# COMPLETE
# ======================
print("\n✅ Live monitoring completed")

print("\n✅ Saved live monitor logs")
print("trade_logs/live_trade_monitor_logs.csv")