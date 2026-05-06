import pandas as pd
import matplotlib.pyplot as plt

# Load optimization results
df = pd.read_csv('data/processed/backtest_optimization_results.csv')

# Top 10
top = df.head(10)

# Plot
plt.figure(figsize=(10, 6))

plt.bar(
    range(len(top)),
    top['total_profit']
)

plt.xticks(
    range(len(top)),
    [f"{x:.2f}" for x in top['confidence']],
    rotation=45
)

plt.xlabel("Confidence Threshold")
plt.ylabel("Total Profit")
plt.title("Top Backtest Profits")

plt.tight_layout()

# Save chart
plt.savefig('results/backtest_profit_chart.png')

print("✅ Chart saved to results/backtest_profit_chart.png")