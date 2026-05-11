import pandas as pd
import os

# ======================
# LOAD TRADE LOGS
# ======================
df = pd.read_csv('trade_logs/trade_logs.csv')

# Ensure results folder exists
os.makedirs('results', exist_ok=True)

# ======================
# BASIC METRICS
# ======================
total_trades = len(df)

total_profit = round(df['net_profit'].sum(), 2)

avg_profit = round(df['net_profit'].mean(), 2)

winning_trades = df[df['net_profit'] > 0]
losing_trades = df[df['net_profit'] <= 0]

wins = len(winning_trades)
losses = len(losing_trades)

win_rate = round((wins / total_trades) * 100, 2) if total_trades > 0 else 0

best_trade = round(df['net_profit'].max(), 2)

worst_trade = round(df['net_profit'].min(), 2)

# ======================
# EQUITY & DRAWDOWN
# ======================
df['equity_curve'] = df['net_profit'].cumsum()

final_equity = round(df['equity_curve'].iloc[-1], 2)

df['running_max'] = df['equity_curve'].cummax()
df['drawdown'] = df['equity_curve'] - df['running_max']

max_drawdown = round(df['drawdown'].min(), 2)

# ======================
# SHARPE RATIO
# ======================
mean_return = df['net_profit'].mean()
std_return = df['net_profit'].std()

sharpe_ratio = round(mean_return / std_return, 4) if std_return != 0 else 0

# ======================
# RISK REWARD RATIO
# ======================
avg_win = winning_trades['net_profit'].mean()
avg_loss = abs(losing_trades['net_profit'].mean())

risk_reward_ratio = round(avg_win / avg_loss, 2) if avg_loss != 0 else 0

# ======================
# MONTHLY PERFORMANCE
# ======================
df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].dt.to_period('M')

monthly_profit = df.groupby('month')['net_profit'].sum()

# ======================
# REPORT CONTENT
# ======================
report = f"""
# Quant Performance Report

## Strategy Summary

This report summarizes the performance of the machine learning based trading strategy using recent trade logs.

## Key Metrics

- Total Trades: {total_trades}
- Total Net Profit: {total_profit}
- Average Profit Per Trade: {avg_profit}
- Winning Trades: {wins}
- Losing Trades: {losses}
- Win Rate: {win_rate}%
- Best Trade: {best_trade}
- Worst Trade: {worst_trade}
- Final Equity: {final_equity}
- Maximum Drawdown: {max_drawdown}
- Sharpe Ratio: {sharpe_ratio}
- Risk Reward Ratio: {risk_reward_ratio}

## Strategy Interpretation

The strategy is profitable on the recent tested sample. Although the win rate is relatively low, the Risk Reward Ratio shows that average winning trades are larger than average losing trades.

This means the strategy focuses on asymmetric reward-risk behavior instead of relying only on a high win rate.

## Monthly Performance

{monthly_profit.to_string()}

## Charts Generated

- results/performance_equity_curve.png
- results/monthly_profit_chart.png
- results/profit_distribution.png

## Important Note

This report is based on historical backtesting and trade log simulation. It is intended for research, learning, and portfolio purposes only. It should not be considered financial advice or used directly for live trading without paper trading and further validation.
"""

# ======================
# SAVE REPORT
# ======================
report_path = 'results/quant_performance_report.md'

with open(report_path, 'w') as file:
    file.write(report)

# ======================
# PRINT REPORT
# ======================
print("\n📘 QUANT PERFORMANCE REPORT")
print("-" * 40)
print(report)

print("\n✅ Report saved:")
print(report_path)