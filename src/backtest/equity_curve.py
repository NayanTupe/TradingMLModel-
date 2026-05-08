import pandas as pd
import matplotlib.pyplot as plt

# ======================
# LOAD WALK-FORWARD RESULTS
# ======================
df = pd.read_csv('data/processed/walk_forward_results.csv')

# ======================
# EQUITY CURVE
# ======================
initial_balance = 100000

df['equity'] = initial_balance + df['total_profit'].cumsum()

# ======================
# DRAWDOWN
# ======================
df['rolling_max'] = df['equity'].cummax()

df['drawdown'] = (
    (df['equity'] - df['rolling_max']) /
    df['rolling_max']
) * 100

max_drawdown = df['drawdown'].min()

# ======================
# PRINT SUMMARY
# ======================
print("\n📊 EQUITY CURVE SUMMARY")

print("Initial Balance:", initial_balance)
print("Final Equity:", round(df['equity'].iloc[-1], 2))
print("Maximum Drawdown:", round(max_drawdown, 2), "%")

# ======================
# PLOT EQUITY CURVE
# ======================
plt.figure(figsize=(12, 6))

plt.plot(
    df['fold'],
    df['equity'],
    linewidth=2
)

plt.xlabel("Fold")
plt.ylabel("Equity")
plt.title("Walk-Forward Equity Curve")

plt.grid(True)

plt.tight_layout()

# Save chart
plt.savefig('results/equity_curve.png')

print("\n✅ Saved equity curve chart")
print("results/equity_curve.png")

# ======================
# PLOT DRAWDOWN
# ======================
plt.figure(figsize=(12, 4))

plt.plot(
    df['fold'],
    df['drawdown'],
    linewidth=2
)

plt.xlabel("Fold")
plt.ylabel("Drawdown %")
plt.title("Drawdown Curve")

plt.grid(True)

plt.tight_layout()

plt.savefig('results/drawdown_curve.png')

print("\n✅ Saved drawdown chart")
print("results/drawdown_curve.png")