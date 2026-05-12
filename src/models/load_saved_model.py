import pandas as pd
import numpy as np
import joblib

# ======================
# LOAD SAVED MODEL
# ======================
model = joblib.load(
    'saved_models/random_forest_model.pkl'
)

print("\n✅ Saved model loaded")

# ======================
# LOAD FEATURES LIST
# ======================
with open(
    'saved_models/model_features.txt',
    'r'
) as f:

    features = [
        line.strip()
        for line in f.readlines()
    ]

print("\n✅ Loaded features:")
print(features)

# ======================
# LOAD DATA
# ======================
df = pd.read_csv(
    'data/processed/features.csv'
)

# Recent rows only
df = df.tail(1000).reset_index(drop=True)

# Clean values
df = df.replace([np.inf, -np.inf], 0)
df = df.fillna(0)

# ======================
# REMOVE LEAKAGE
# ======================
leakage_cols = [
    'future_close',
    'future_high',
    'future_low'
]

for col in leakage_cols:
    if col in df.columns:
        df = df.drop(columns=[col])

# ======================
# PREPARE INPUT
# ======================
X = df[features]

# ======================
# PREDICT
# ======================
predictions = model.predict(X)

probabilities = model.predict_proba(X)

df['prediction'] = predictions

df['confidence'] = probabilities[:, 1]

# ======================
# OUTPUT
# ======================
print("\n📊 Latest Predictions")

print(
    df[
        [
            'date',
            'stock',
            'close',
            'prediction',
            'confidence'
        ]
    ].tail(20)
)

# ======================
# SAVE
# ======================
df.to_csv(
    'results/model_predictions.csv',
    index=False
)

print("\n✅ Saved predictions")
print("results/model_predictions.csv")