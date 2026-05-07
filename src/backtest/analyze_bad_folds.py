import pandas as pd

# ======================
# LOAD WALK-FORWARD RESULTS
# ======================
df = pd.read_csv('data/processed/walk_forward_results.csv')

# ======================
# BASIC SUMMARY
# ======================
total_folds = len(df)
profitable_folds = len(df[df['total_profit'] > 0])
losing_folds = len(df[df['total_profit'] <= 0])

profitable_fold_pct = (profitable_folds / total_folds) * 100 if total_folds > 0 else 0

total_profit = df['total_profit'].sum()
avg_profit = df['total_profit'].mean()
max_profit = df['total_profit'].max()
max_loss = df['total_profit'].min()

avg_win_rate = df['win_rate'].mean()
avg_trades = df['total_trades'].mean()

# ======================
# BAD / WEAK / BEST FOLDS
# ======================
bad_folds = df[df['total_profit'] <= 0].sort_values(by='total_profit')

weak_folds = df[
    (df['total_profit'] > 0) &
    (df['win_rate'] < 50)
].sort_values(by='win_rate')

best_folds = df.sort_values(by='total_profit', ascending=False).head(10)

worst_folds = df.sort_values(by='total_profit').head(10)

# ======================
# SAVE FILES
# ======================
bad_folds.to_csv('data/processed/bad_folds.csv', index=False)
weak_folds.to_csv('data/processed/weak_folds.csv', index=False)
best_folds.to_csv('data/processed/best_folds.csv', index=False)
worst_folds.to_csv('data/processed/worst_folds.csv', index=False)

# ======================
# PRINT RESULTS
# ======================
print("\n📊 WALK-FORWARD BAD FOLD ANALYSIS")

print("\nOverall Summary:")
print("Total Folds:", total_folds)
print("Profitable Folds:", profitable_folds)
print("Losing Folds:", losing_folds)
print("Profitable Fold %:", round(profitable_fold_pct, 2), "%")
print("Total Profit:", round(total_profit, 2))
print("Average Profit Per Fold:", round(avg_profit, 2))
print("Max Profit Fold:", round(max_profit, 2))
print("Max Loss Fold:", round(max_loss, 2))
print("Average Win Rate:", round(avg_win_rate, 2), "%")
print("Average Trades Per Fold:", round(avg_trades, 2))

print("\n❌ Worst 10 Folds:")
print(worst_folds[
    [
        'fold',
        'test_start',
        'test_end',
        'total_profit',
        'total_trades',
        'win_rate',
        'avg_profit',
        'target_hits',
        'stop_losses',
        'time_exits'
    ]
].to_string(index=False))

print("\n✅ Best 10 Folds:")
print(best_folds[
    [
        'fold',
        'test_start',
        'test_end',
        'total_profit',
        'total_trades',
        'win_rate',
        'avg_profit',
        'target_hits',
        'stop_losses',
        'time_exits'
    ]
].to_string(index=False))

print("\n📁 Saved:")
print("data/processed/bad_folds.csv")
print("data/processed/weak_folds.csv")
print("data/processed/best_folds.csv")
print("data/processed/worst_folds.csv")