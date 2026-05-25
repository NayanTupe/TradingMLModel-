import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# ======================
# LOAD DATA
# ======================
df = pd.read_csv('data/processed/features.csv')
df = df.tail(50000).reset_index(drop=True)

# ======================
# CLEAN DATA
# ======================
df = df.replace([np.inf, -np.inf], 0)
df = df.fillna(0)

# ======================
# REMOVE LEAKAGE
# ======================
leakage_cols = ['future_close', 'future_high', 'future_low']
for col in leakage_cols:
    if col in df.columns:
        df = df.drop(columns=[col])

# ======================
# FEATURES & TARGET
# ======================
features = [
    'ma_10', 'ma_20', 'rsi', 'price_change', 'volatility', 'momentum',
    'vwap', 'atr', 'volume_spike', 'candle_body_pct', 'trend_strength',
    'near_prev_day_high', 'near_prev_day_low', 'orb_breakout', 'orb_breakdown',
    'atr_pct', 'above_vwap', 'high_volume', 'uptrend', 'market_regime'
]

X = df[features]
y = df['target']

# ======================
# TIME-BASED SPLIT
# ======================
split_index = int(len(df) * 0.8)
X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]
y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]
df_test = df.iloc[split_index:].copy().reset_index(drop=True)

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

# ======================
# TRAIN
# ======================
print("\n🚀 Training Random Forest Model...")
model.fit(X_train, y_train)

# ======================
# PREDICT
# ======================
pred = model.predict(X_test)
proba = model.predict_proba(X_test)[:, 1]

# ======================
# SAVE PREDICTIONS with date, stock, close for backtest pipeline
# ======================
df_preds = pd.DataFrame({
    'date': df_test['date'],
    'stock': df_test['stock'],
    'close': df_test['close'],
    'actual': df_test['target'],
    'prediction': pred,
    'confidence': proba
})
df_preds.to_csv('results/model_predictions.csv', index=False)

# ======================
# VALIDATION
# ======================
print("\n🔍 Prediction Distribution:")
print(pd.Series(pred).value_counts())

print("\n🔍 Actual Target Distribution:")
print(y_test.value_counts())

print("\n📊 Classification Report:")
print(classification_report(y_test, pred))

# ======================
# RESULT
# ======================
train_accuracy = model.score(X_train, y_train)
test_accuracy = accuracy_score(y_test, pred)
print("\n✅ Model Trained Successfully")
print("Train Accuracy:", round(train_accuracy, 4))
print("Test Accuracy:", round(test_accuracy, 4))

# ======================
# SAVE MODEL
# ======================
model_path = 'saved_models/random_forest_model.pkl'
joblib.dump(model, model_path)
print("\n✅ Saved Model:")
print(model_path)

# ======================
# SAVE FEATURE LIST
# ======================
features_path = 'saved_models/model_features.txt'
with open(features_path, 'w') as f:
    for feature in features:
        f.write(feature + '\n')
print("\n✅ Saved Features:")
print(features_path)