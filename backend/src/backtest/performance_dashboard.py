import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ======================
# LOAD TRADE LOGS
# ======================
log_path = 'trade_logs/trade_logs.csv'
if not os.path.exists(log_path):
    raise FileNotFoundError(f"Trade logs not found at {log_path}. Run export_trade_logs.py first.")

df = pd.read_csv(log_path)

# ======================
# DATE COLUMN
# ======================
df['date'] = pd.to_datetime(df['date'])

# ======================
# SUMMARY METRICS
# ======================
total_trades = len(df)
total_net_profit = df['net_profit'].sum()
average_profit = df['net_profit'].mean()
winning_trades = len(df[df['net_profit'] > 0])
losing_trades = len(df[df['net_profit'] <= 0])
win_rate = (winning_trades / total_trades) * 100
best_trade = df['net_profit'].max()
worst_trade = df['net_profit'].min()

print("\n📊 TRADE LOGS SUMMARY")
print("Total Trades:", total_trades)
print("Total Net Profit:", round(total_net_profit, 2))
print("Average Profit:", round(average_profit, 2))
print("Winning Trades:", winning_trades)
print("Losing Trades:", losing_trades)
print("Win Rate:", round(win_rate, 2), "%")
print("Best Trade:", round(best_trade, 2))
print("Worst Trade:", round(worst_trade, 2))

# ======================
# EQUITY CURVE
# ======================
df['equity_curve'] = df['net_profit'].cumsum()
final_equity = df['equity_curve'].iloc[-1]
df['running_max'] = df['equity_curve'].cummax()
df['drawdown'] = df['equity_curve'] - df['running_max']
max_drawdown = df['drawdown'].min()

print("\nFinal Equity:", round(final_equity, 2))
print("Maximum Drawdown:", round(max_drawdown, 2))

# ======================
# CREATE RESULTS FOLDER
# ======================
os.makedirs('results', exist_ok=True)

# ======================
# EQUITY CURVE CHART
# ======================
plt.figure(figsize=(12, 6))
plt.plot(df['equity_curve'], label='Equity Curve')
plt.title('Equity Curve')
plt.xlabel('Trades')
plt.ylabel('Profit')
plt.grid(True)
plt.legend()
plt.savefig('results/performance_equity_curve.png')
plt.close()
print("\n✅ Saved equity curve chart: results/performance_equity_curve.png")

# ======================
# MONTHLY PERFORMANCE
# ======================
df['month'] = df['date'].dt.to_period('M')
monthly_profit = df.groupby('month')['net_profit'].sum()
print("\n📅 Monthly Profit:")
print(monthly_profit)

plt.figure(figsize=(12, 6))
monthly_profit.plot(kind='bar')
plt.title('Monthly Profit')
plt.xlabel('Month')
plt.ylabel('Net Profit')
plt.grid(True)
plt.savefig('results/monthly_profit_chart.png')
plt.close()
print("✅ Saved monthly profit chart: results/monthly_profit_chart.png")

# ======================
# PROFIT DISTRIBUTION
# ======================
plt.figure(figsize=(12, 6))
plt.hist(df['net_profit'], bins=30)
plt.title('Profit Distribution')
plt.xlabel('Net Profit')
plt.ylabel('Frequency')
plt.grid(True)
plt.savefig('results/profit_distribution.png')
plt.close()
print("✅ Saved profit distribution chart: results/profit_distribution.png")

# ======================
# SHARPE RATIO
# ======================
mean_return = df['net_profit'].mean()
std_return = df['net_profit'].std()
sharpe_ratio = mean_return / std_return if std_return != 0 else 0
print("\nSharpe Ratio:", round(sharpe_ratio, 4))

# ======================
# RISK REWARD RATIO
# ======================
avg_win = df[df['net_profit'] > 0]['net_profit'].mean() or 0
avg_loss = abs(df[df['net_profit'] <= 0]['net_profit'].mean()) or 1  # prevent division by zero
risk_reward_ratio = avg_win / avg_loss
print("Risk Reward Ratio:", round(risk_reward_ratio, 2))