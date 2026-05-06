import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# ======================
# LOAD DATA
# ======================
df = pd.read_csv('data/processed/features.csv')
df = df.tail(50000)

# Remove leakage
if 'future_close' in df.columns:
    df = df.drop(columns=['future_close'])

# ======================
# FEATURES
# ======================
features = ['ma_10', 'ma_20', 'rsi', 'price_change', 'volatility', 'momentum']

X = df[features]
y = df['target']

# ======================
# TIME SPLIT
# ======================
split_index = int(len(df) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

df_test = df.iloc[split_index:].copy()

# ======================
# MODEL
# ======================
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_leaf=10,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# ======================
# PREDICT WITH CONFIDENCE 🔥
# ======================
proba = model.predict_proba(X_test)

df_test['confidence'] = proba[:, 1]

# Only strong signals
df_test['prediction'] = (df_test['confidence'] > 0.6).astype(int)

# ======================
# BACKTEST LOGIC
# ======================
initial_balance = 100000
balance = initial_balance

trades = []

for i in range(len(df_test) - 5):  # hold 5 minutes
    row = df_test.iloc[i]

    # 🔥 Only trade strong signals
    if row['prediction'] == 1 and row['confidence'] > 0.6:
        entry_price = row['close']
        exit_price = df_test.iloc[i + 5]['close']

        profit = exit_price - entry_price

        balance += profit
        trades.append(profit)

# ======================
# RESULTS
# ======================
total_trades = len(trades)
wins = len([t for t in trades if t > 0])
losses = len([t for t in trades if t <= 0])

win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
total_profit = sum(trades)

print("\n📊 BACKTEST RESULT")
print("Initial Balance:", initial_balance)
print("Final Balance:", round(balance, 2))
print("Total Profit:", round(total_profit, 2))
print("Total Trades:", total_trades)
print("Win Rate:", round(win_rate, 2), "%")