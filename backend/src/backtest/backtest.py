import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# ======================
# LOAD DATA
# ======================
df = pd.read_csv('data/processed/features.csv')
df = df.tail(100000).reset_index(drop=True)

df = df.replace([np.inf, -np.inf], 0)
df = df.fillna(0)

# ======================
# REMOVE LEAKAGE
# ======================
leakage_cols = ['future_close', 'future_high', 'future_low']
for col in leakage_cols:
    if col in df.columns:
        df = df.drop(columns=[col])

# ======================
# FEATURES
# ======================
features = [
    'ma_10', 'ma_20', 'rsi', 'price_change', 'volatility', 'momentum',
    'vwap', 'atr', 'volume_spike', 'candle_body_pct', 'trend_strength',
    'near_prev_day_high', 'near_prev_day_low', 'orb_breakout', 'orb_breakdown',
    'atr_pct', 'above_vwap', 'high_volume', 'uptrend', 'market_regime'
]

X = df[features]
y = df['target']

split_index = int(len(df) * 0.8)
X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]
y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]
df_test = df.iloc[split_index:].copy().reset_index(drop=True)

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
# PREDICTION
# ======================
df_test['confidence'] = model.predict_proba(X_test)[:, 1]

# ======================
# BACKTEST SETTINGS
# ======================
confidence_threshold = 0.50
stop_loss_pct = 0.0025
target_pct = 0.007
hold_candles = 45
capital_per_trade = 100000
brokerage_pct = 0.00005

trades = []

# ======================
# BACKTEST LOGIC
# ======================
for i in range(len(df_test) - hold_candles):
    row = df_test.iloc[i]

    if row['confidence'] >= confidence_threshold and row['market_regime'] == 1:
        entry_price = row['close']
        quantity = int(capital_per_trade / entry_price)
        if quantity <= 0:
            continue

        stop_loss_price = entry_price * (1 - stop_loss_pct)
        target_price = entry_price * (1 + target_pct)
        exit_price = None
        exit_reason = "time_exit"

        future_rows = df_test.iloc[i + 1:i + hold_candles + 1]

        for _, future in future_rows.iterrows():
            if future['low'] <= stop_loss_price:
                exit_price = stop_loss_price
                exit_reason = "stop_loss"
                break
            if future['high'] >= target_price:
                exit_price = target_price
                exit_reason = "target"
                break

        if exit_price is None:
            exit_price = df_test.iloc[i + hold_candles]['close']

        buy_value = entry_price * quantity
        sell_value = exit_price * quantity
        gross_profit = sell_value - buy_value
        brokerage = (buy_value + sell_value) * brokerage_pct
        net_profit = gross_profit - brokerage

        trades.append({
            "entry": entry_price,
            "exit": exit_price,
            "quantity": quantity,
            "confidence": row['confidence'],
            "gross_profit": gross_profit,
            "brokerage": brokerage,
            "net_profit": net_profit,
            "exit_reason": exit_reason
        })

# ======================
# RESULTS
# ======================
trades_df = pd.DataFrame(trades)
total_trades = len(trades_df)

if total_trades == 0:
    print("❌ No trades found.")
else:
    wins = len(trades_df[trades_df['net_profit'] > 0])
    losses = len(trades_df[trades_df['net_profit'] <= 0])
    win_rate = (wins / total_trades) * 100
    total_profit = trades_df['net_profit'].sum()

    print("\n📊 BACKTEST RESULT")
    print("Initial Balance:", 100000)
    print("Final Balance:", round(100000 + total_profit, 2))
    print("Total Net Profit:", round(total_profit, 2))
    print("Total Trades:", total_trades)
    print("Wins:", wins)
    print("Losses:", losses)
    print("Win Rate:", round(win_rate, 2), "%")

    print("\nExit Reasons:")
    print(trades_df['exit_reason'].value_counts())

    print("\nAverage Net Profit Per Trade:", round(trades_df['net_profit'].mean(), 2))
    print("Average Gross Profit Per Trade:", round(trades_df['gross_profit'].mean(), 2))
    print("Average Brokerage Per Trade:", round(trades_df['brokerage'].mean(), 2))