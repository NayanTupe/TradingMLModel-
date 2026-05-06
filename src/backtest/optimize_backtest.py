import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from itertools import product

# ======================
# LOAD DATA
# ======================
df = pd.read_csv('data/processed/features.csv')
df = df.tail(50000)

leakage_cols = ['future_close', 'future_high', 'future_low']

for col in leakage_cols:
    if col in df.columns:
        df = df.drop(columns=[col])

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

X = df[features]
y = df['target']

split_index = int(len(df) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]

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

proba = model.predict_proba(X_test)
df_test['confidence'] = proba[:, 1]

# ======================
# BACKTEST FUNCTION
# ======================
def run_backtest(confidence_threshold, stop_loss_pct, target_pct, hold_candles):
    initial_balance = 100000
    balance = initial_balance

    capital_per_trade = 100000
    brokerage_pct = 0.00005

    trades = []

    for i in range(len(df_test) - hold_candles):
        row = df_test.iloc[i]

        if row['confidence'] >= confidence_threshold:
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

            balance += net_profit

            trades.append({
                "net_profit": net_profit,
                "exit_reason": exit_reason
            })

    total_trades = len(trades)

    if total_trades == 0:
        return None

    trades_df = pd.DataFrame(trades)

    wins = len(trades_df[trades_df['net_profit'] > 0])
    losses = len(trades_df[trades_df['net_profit'] <= 0])

    win_rate = (wins / total_trades) * 100
    total_profit = trades_df['net_profit'].sum()
    avg_profit = trades_df['net_profit'].mean()

    target_hits = len(trades_df[trades_df['exit_reason'] == 'target'])
    stop_losses = len(trades_df[trades_df['exit_reason'] == 'stop_loss'])

    return {
        "confidence": confidence_threshold,
        "stop_loss_pct": stop_loss_pct,
        "target_pct": target_pct,
        "hold_candles": hold_candles,
        "final_balance": round(balance, 2),
        "total_profit": round(total_profit, 2),
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": round(win_rate, 2),
        "avg_profit": round(avg_profit, 2),
        "target_hits": target_hits,
        "stop_losses": stop_losses
    }

# ======================
# PARAMETER GRID
# ======================
confidence_values = [0.55, 0.58, 0.60, 0.62]
stop_loss_values = [0.0015, 0.002, 0.0025]
target_values = [0.003, 0.005, 0.007]
hold_values = [15, 30, 45]

results = []

for confidence, stop_loss, target, hold in product(
    confidence_values,
    stop_loss_values,
    target_values,
    hold_values
):
    result = run_backtest(confidence, stop_loss, target, hold)

    if result:
        results.append(result)

# ======================
# RESULTS
# ======================
results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by=['total_profit', 'total_trades'],
    ascending=False
)

print("\n🏆 TOP 10 BACKTEST SETTINGS")
print(results_df.head(10).to_string(index=False))

results_df.to_csv('data/processed/backtest_optimization_results.csv', index=False)

print("\n✅ Optimization complete")
print("Saved results to data/processed/backtest_optimization_results.csv")