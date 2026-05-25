import pandas as pd
import numpy as np

# ======================
# CONFIG
# ======================
CONFIDENCE_THRESHOLD = 0.35  # lower for testing
STOP_LOSS_PCT = 0.0025
TARGET_PCT = 0.007
HOLD_CANDLES = 45
CAPITAL_PER_TRADE = 100000
BROKERAGE_PCT = 0.00005

# ======================
# LOAD DATA
# ======================
features = pd.read_csv('data/processed/features.csv')
preds = pd.read_csv('results/model_predictions.csv')

# Ensure datetime
features['date'] = pd.to_datetime(features['date'])
preds['date'] = pd.to_datetime(preds['date'])

# Add 'stock' to preds if missing
if 'stock' not in preds.columns:
    preds['stock'] = features['stock'].iloc[:len(preds)]

# ======================
# MERGE FEATURES + OHLC + MARKET REGIME
# ======================
merge_cols = ['date', 'stock', 'open', 'high', 'low', 'close', 'market_regime']
df_test = pd.merge(
    preds,
    features[merge_cols],
    on=['date', 'stock'],
    how='left',
    validate='m:1'
)

# Fill missing OHLC from features
for col in ['open', 'high', 'low', 'close']:
    if col not in df_test.columns:
        df_test[col] = np.nan
    # Fill NaN from features if present
    if col in features.columns:
        df_test[col] = df_test[col].combine_first(
            features[col].iloc[:len(df_test)]
        )
    # Forward-fill remaining NaNs
    df_test[col] = df_test[col].ffill()

# Fill market regime safely
if 'market_regime' not in df_test.columns:
    df_test['market_regime'] = 0
else:
    df_test['market_regime'] = df_test['market_regime'].fillna(0)

# ======================
# BACKTEST LOOP
# ======================
trades = []

for i in range(len(df_test) - HOLD_CANDLES):
    row = df_test.iloc[i]

    # Skip invalid close
    if pd.isna(row['close']) or row['close'] <= 0:
        continue

    # Check confidence + market regime
    if row['confidence'] >= CONFIDENCE_THRESHOLD and row['market_regime'] == 1:
        entry_price = row['close']
        quantity = int(CAPITAL_PER_TRADE / entry_price)
        if quantity <= 0:
            continue

        stop_loss_price = entry_price * (1 - STOP_LOSS_PCT)
        target_price = entry_price * (1 + TARGET_PCT)

        exit_price = None
        exit_reason = "time_exit"

        future_rows = df_test.iloc[i+1:i+HOLD_CANDLES+1]
        for _, future in future_rows.iterrows():
            if pd.isna(future['low']) or pd.isna(future['high']):
                continue
            if future['low'] <= stop_loss_price:
                exit_price = stop_loss_price
                exit_reason = "stop_loss"
                break
            if future['high'] >= target_price:
                exit_price = target_price
                exit_reason = "target"
                break

        if exit_price is None:
            exit_price = future_rows['close'].ffill().iloc[-1]

        buy_value = entry_price * quantity
        sell_value = exit_price * quantity
        gross_profit = sell_value - buy_value
        brokerage = (buy_value + sell_value) * BROKERAGE_PCT
        net_profit = gross_profit - brokerage

        trades.append({
            "date": row['date'],
            "stock": row['stock'],
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
trades_df.to_csv('trade_logs/full_backtest_trades.csv', index=False)

print(f"\n✅ Total Trades: {len(trades_df)}")
if len(trades_df) > 0:
    print(f"Net Profit: {trades_df['net_profit'].sum():.2f}")
    print("Exit Reasons:")
    print(trades_df['exit_reason'].value_counts())
    print("\n✅ Sample Trades:")
    print(trades_df.head(10))
else:
    print("No trades executed. Consider lowering confidence threshold for testing.")

print("\n✅ Trade logs saved to trade_logs/full_backtest_trades.csv")