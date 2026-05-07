import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# ======================
# LOAD DATA
# ======================
df = pd.read_csv('data/processed/features.csv')

df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(by=['date', 'stock']).reset_index(drop=True)

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

# ======================
# CLEAN INF / NAN VALUES
# ======================
df[features] = df[features].replace([np.inf, -np.inf], 0)
df[features] = df[features].fillna(0)

# ======================
# SETTINGS
# ======================
confidence_threshold = 0.58
stop_loss_pct = 0.0025
target_pct = 0.007
capital_per_trade = 100000
brokerage_pct = 0.00005
hold_candles = 30

train_window = 30000
test_window = 10000
step_size = 50000

results = []

# ======================
# WALK-FORWARD LOOP
# ======================
start = 0
fold = 1

while start + train_window + test_window <= len(df):
    train_df = df.iloc[start:start + train_window].copy()
    test_df = df.iloc[
        start + train_window:start + train_window + test_window
    ].copy().reset_index(drop=True)

    X_train = train_df[features]
    y_train = train_df['target']

    X_test = test_df[features]

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=8,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)
    test_df['confidence'] = proba[:, 1]

    balance = 100000
    trades = []

    for i in range(len(test_df) - hold_candles):
        row = test_df.iloc[i]

        if row['confidence'] >= confidence_threshold:
            entry_price = row['close']
            quantity = int(capital_per_trade / entry_price)

            if quantity <= 0:
                continue

            stop_loss_price = entry_price * (1 - stop_loss_pct)
            target_price = entry_price * (1 + target_pct)

            exit_price = None
            exit_reason = "time_exit"

            future_rows = test_df.iloc[i + 1:i + hold_candles + 1]

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
                exit_price = test_df.iloc[i + hold_candles]['close']

            buy_value = entry_price * quantity
            sell_value = exit_price * quantity

            gross_profit = sell_value - buy_value
            brokerage = (buy_value + sell_value) * brokerage_pct
            net_profit = gross_profit - brokerage

            balance += net_profit

            trades.append({
                "net_profit": net_profit,
                "exit_reason": exit_reason
            })

    trades_df = pd.DataFrame(trades)
    total_trades = len(trades_df)

    if total_trades > 0:
        wins = len(trades_df[trades_df['net_profit'] > 0])
        losses = len(trades_df[trades_df['net_profit'] <= 0])
        total_profit = trades_df['net_profit'].sum()
        win_rate = (wins / total_trades) * 100
        avg_profit = trades_df['net_profit'].mean()
        target_hits = len(trades_df[trades_df['exit_reason'] == 'target'])
        stop_losses = len(trades_df[trades_df['exit_reason'] == 'stop_loss'])
        time_exits = len(trades_df[trades_df['exit_reason'] == 'time_exit'])
    else:
        wins = 0
        losses = 0
        total_profit = 0
        win_rate = 0
        avg_profit = 0
        target_hits = 0
        stop_losses = 0
        time_exits = 0

    results.append({
        "fold": fold,
        "train_start": train_df['date'].min(),
        "train_end": train_df['date'].max(),
        "test_start": test_df['date'].min(),
        "test_end": test_df['date'].max(),
        "total_profit": round(total_profit, 2),
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": round(win_rate, 2),
        "avg_profit": round(avg_profit, 2),
        "target_hits": target_hits,
        "stop_losses": stop_losses,
        "time_exits": time_exits
    })

    print(
        f"✅ Fold {fold} completed | "
        f"Profit: {round(total_profit, 2)} | "
        f"Trades: {total_trades}"
    )

    start += step_size
    fold += 1

# ======================
# FINAL RESULTS
# ======================
results_df = pd.DataFrame(results)

print("\n📊 WALK-FORWARD RESULTS")
print(results_df.to_string(index=False))

print("\n🏁 SUMMARY")
print("Total Folds:", len(results_df))
print("Total Profit:", round(results_df['total_profit'].sum(), 2))
print("Total Trades:", int(results_df['total_trades'].sum()))
print("Average Win Rate:", round(results_df['win_rate'].mean(), 2), "%")
print("Average Profit Per Fold:", round(results_df['total_profit'].mean(), 2))

results_df.to_csv('data/processed/walk_forward_results.csv', index=False)

print("\n✅ Saved to data/processed/walk_forward_results.csv")  