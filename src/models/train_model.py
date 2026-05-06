import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# ======================
# LOAD DATA
# ======================
df = pd.read_csv('data/processed/features.csv')

# Use recent data (Mac friendly)
df = df.tail(50000)

# ======================
# REMOVE LEAKAGE
# ======================
if 'future_close' in df.columns:
    df = df.drop(columns=['future_close'])

# ======================
# FEATURES & TARGET
# ======================
X = df[['ma_10', 'ma_20', 'rsi', 'price_change', 'volatility', 'momentum']]
y = df['target']

# ======================
# TIME-BASED SPLIT (VERY IMPORTANT)
# ======================
split_index = int(len(df) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

# ======================
# MODEL (HANDLE IMBALANCE PROPERLY)
# ======================
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_leaf=10,
    class_weight='balanced',   # ✅ correct way
    random_state=42,
    n_jobs=-1
)

# ======================
# TRAIN
# ======================
model.fit(X_train, y_train)

# ======================
# PREDICT
# ======================
pred = model.predict(X_test)

# ======================
# VALIDATION
# ======================
print("\n🔍 Prediction distribution:")
print(pd.Series(pred).value_counts())

print("\n🔍 Actual target distribution:")
print(y_test.value_counts())

print("\n📊 Classification Report:")
print(classification_report(y_test, pred))

# ======================
# RESULT
# ======================
print("\n✅ Model trained")
print("Train Accuracy:", model.score(X_train, y_train))
print("Test Accuracy:", accuracy_score(y_test, pred))