import pandas as pd
import matplotlib.pyplot as plt

# ======================
# LOAD TRADE LOGS
# ======================
df = pd.read_csv('trade_logs/trade_logs.csv')

# ======================
# DATE COLUMN
# ======================
df['date'] = pd.to_datetime(df['date'])

# ======================
# SUMMARY
# ======================
print("\n📊 TRADE LOGS SUMMARY")

print("Total Trades:", len(df))

print(
    "Total Net Profit:",
    round(df['net_profit'].sum(), 2)
)

print(
    "Average Profit:",
    round(df['net_profit'].mean(), 2)
)

print(
    "Winning Trades:",
    len(df[df['net_profit'] > 0])
)

print(
    "Losing Trades:",
    len(df[df['net_profit'] <= 0])
)

# ======================
# WIN RATE
# ======================
win_rate = (
    len(df[df['net_profit'] > 0]) /
    len(df)
) * 100

print(
    "Win Rate:",
    round(win_rate, 2),
    "%"
)

# ======================
# BEST / WORST TRADE
# ======================
best_trade = df['net_profit'].max()

worst_trade = df['net_profit'].min()

print(
    "Best Trade:",
    round(best_trade, 2)
)

print(
    "Worst Trade:",
    round(worst_trade, 2)
)

# ======================
# EQUITY CURVE
# ======================
df['equity_curve'] = (
    df['net_profit'].cumsum()
)

print(
    "\nFinal Equity:",
    round(df['equity_curve'].iloc[-1], 2)
)

# ======================
# DRAWDOWN
# ======================
df['running_max'] = (
    df['equity_curve'].cummax()
)

df['drawdown'] = (
    df['equity_curve'] -
    df['running_max']
)

max_drawdown = df['drawdown'].min()

print(
    "Maximum Drawdown:",
    round(max_drawdown, 2)
)

# ======================
# EQUITY CURVE CHART
# ======================
plt.figure(figsize=(12, 6))

plt.plot(
    df['equity_curve'],
    label='Equity Curve'
)

plt.title('Equity Curve')

plt.xlabel('Trades')

plt.ylabel('Profit')

plt.legend()

plt.grid(True)

plt.savefig(
    'results/performance_equity_curve.png'
)

print(
    "\n✅ Saved equity curve chart"
)

print(
    "results/performance_equity_curve.png"
)

# ======================
# MONTHLY PERFORMANCE
# ======================
df['month'] = df['date'].dt.to_period('M')

monthly_profit = (
    df.groupby('month')['net_profit']
    .sum()
)

print("\n📅 Monthly Profit:")

print(monthly_profit)

# ======================
# MONTHLY PROFIT CHART
# ======================
plt.figure(figsize=(12, 6))

monthly_profit.plot(
    kind='bar'
)

plt.title('Monthly Profit')

plt.xlabel('Month')

plt.ylabel('Net Profit')

plt.grid(True)

plt.savefig(
    'results/monthly_profit_chart.png'
)

print(
    "\n✅ Saved monthly profit chart"
)

print(
    "results/monthly_profit_chart.png"
)


# ======================
# PROFIT DISTRIBUTION
# ======================
plt.figure(figsize=(12, 6))

plt.hist(
    df['net_profit'],
    bins=30
)

plt.title('Profit Distribution')

plt.xlabel('Net Profit')

plt.ylabel('Frequency')

plt.grid(True)

plt.savefig(
    'results/profit_distribution.png'
)

print(
    "\n✅ Saved profit distribution chart"
)

print(
    "results/profit_distribution.png"
)


# ======================
# SHARPE RATIO
# ======================
mean_return = df['net_profit'].mean()

std_return = df['net_profit'].std()

if std_return != 0:

    sharpe_ratio = (
        mean_return / std_return
    )

    print(
        "\nSharpe Ratio:",
        round(sharpe_ratio, 4)
    )

else:
    print(
        "\nSharpe Ratio: Cannot calculate"
    )


# ======================
# RISK REWARD RATIO
# ======================
winning_trades = df[
    df['net_profit'] > 0
]

losing_trades = df[
    df['net_profit'] <= 0
]

avg_win = winning_trades[
    'net_profit'
].mean()

avg_loss = abs(
    losing_trades[
        'net_profit'
    ].mean()
)

if avg_loss != 0:

    risk_reward_ratio = (
        avg_win / avg_loss
    )

    print(
        "\nRisk Reward Ratio:",
        round(risk_reward_ratio, 2)
    )

else:
    print(
        "\nRisk Reward Ratio: Cannot calculate"
    )
