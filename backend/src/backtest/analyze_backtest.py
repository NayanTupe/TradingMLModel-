import pandas as pd
import matplotlib.pyplot as plt

# ======================
# LOAD TRADE LOGS
# ======================
df = pd.read_csv('trade_logs/full_backtest_trades.csv')

# ======================
# DATE COLUMN
# ======================
df['date'] = pd.to_datetime(df['date'])

# ======================
# SUMMARY
# ======================
print("\n📊 TRADE LOGS SUMMARY")
print("Total Trades:", len(df))
print("Total Net Profit:", round(df['net_profit'].sum(), 2))
print("Average Profit:", round(df['net_profit'].mean(), 2))
print("Winning Trades:", len(df[df['net_profit'] > 0]))
print("Losing Trades:", len(df[df['net_profit'] <= 0]))

# ======================
# WIN RATE
# ======================
win_rate = (len(df[df['net_profit'] > 0]) / len(df)) * 100
print("Win Rate:", round(win_rate, 2), "%")

# ======================
# BEST / WORST TRADE
# ======================
best_trade = df['net_profit'].max()
worst_trade = df['net_profit'].min()
print("Best Trade:", round(best_trade, 2))
print("Worst Trade:", round(worst_trade, 2))

# ======================
# EQUITY CURVE
# ======================
df['equity_curve'] = df['net_profit'].cumsum()
print("\nFinal Equity:", round(df['equity_curve'].iloc[-1], 2))

# ======================
# DRAWDOWN
# ======================
df['running_max'] = df['equity_curve'].cummax()
df['drawdown'] = df['equity_curve'] - df['running_max']
max_drawdown = df['drawdown'].min()
print("Maximum Drawdown:", round(max_drawdown, 2))

# ======================
# EQUITY CURVE CHART
# ======================
plt.figure(figsize=(12, 6))
plt.plot(df['equity_curve'], label='Equity Curve')
plt.title('Equity Curve')
plt.xlabel('Trades')
plt.ylabel('Profit')
plt.legend()
plt.grid(True)
plt.savefig('results/full_backtest_equity_curve.png')
print("\n✅ Saved equity curve chart: results/full_backtest_equity_curve.png")

# ======================
# MONTHLY PERFORMANCE
# ======================
df['month'] = df['date'].dt.to_period('M')
monthly_profit = df.groupby('month')['net_profit'].sum()
print("\n📅 Monthly Profit:")
print(monthly_profit)

# ======================
# MONTHLY PROFIT CHART
# ======================
plt.figure(figsize=(12, 6))
monthly_profit.plot(kind='bar')
plt.title('Monthly Profit')
plt.xlabel('Month')
plt.ylabel('Net Profit')
plt.grid(True)
plt.savefig('results/full_backtest_monthly_profit.png')
print("\n✅ Saved monthly profit chart: results/full_backtest_monthly_profit.png")

# ======================
# PROFIT DISTRIBUTION
# ======================
plt.figure(figsize=(12, 6))
plt.hist(df['net_profit'], bins=30)
plt.title('Profit Distribution')
plt.xlabel('Net Profit')
plt.ylabel('Frequency')
plt.grid(True)
plt.savefig('results/full_backtest_profit_distribution.png')
print("\n✅ Saved profit distribution chart: results/full_backtest_profit_distribution.png")