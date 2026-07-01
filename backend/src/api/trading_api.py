from fastapi import FastAPI
import pandas as pd
import numpy as np
import joblib

# ======================
# APP
# ======================
app = FastAPI()

# ======================
# LOAD MODEL
# ======================
model = joblib.load(
    'saved_models/random_forest_model.pkl'
)

# ======================
# LOAD FEATURES
# ======================
with open(
    'saved_models/model_features.txt',
    'r'
) as f:

    features = [
        line.strip()
        for line in f.readlines()
    ]

print("\n✅ ML Model Loaded")
print("✅ Features Loaded")

# ======================
# HOME ROUTE
# ======================
@app.get("/")
def home():

    return {
        "message": "Trading ML API Running"
    }

# ======================
# PREDICT ROUTE
# ======================
@app.get("/predict")
def predict():

    # ======================
    # LOAD DATA
    # ======================
    df = pd.read_csv(
        'data/processed/features.csv'
    )

    # BEST BALANCE
    # Fast + Stable
    df = df.tail(1000).reset_index(drop=True)

    # ======================
    # CLEAN DATA
    # ======================
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
    # USE LATEST ROW
    # ======================
    latest_row = df.tail(1)

    X = latest_row[features]

    # ======================
    # PREDICT
    # ======================
    prediction = model.predict(X)[0]

    confidence = model.predict_proba(X)[0][1]

    # ======================
    # SIGNAL
    # ======================
    signal = "NO TRADE"

    if (
        prediction == 1 and
        confidence >= 0.50
    ):
        signal = "BUY"

    # ======================
    # RESPONSE
    # ======================
    response = {
        "stock": str(latest_row.iloc[0]['stock']),
        "date": str(latest_row.iloc[0]['date']),
        "close": float(latest_row.iloc[0]['close']),
        "prediction": int(prediction),
        "confidence": round(float(confidence), 4),
        "signal": signal
    }

    return response

# ======================
# HEALTH CHECK
# ======================
@app.get("/health")
def health():

    return {
        "status": "running",
        "model_loaded": True
    }