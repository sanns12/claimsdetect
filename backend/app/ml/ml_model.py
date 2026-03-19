# backend/app/ml/ml_model.py

import os
import joblib
from typing import Dict, Any
import pandas as pd

from app.ml.feature_engineering import build_feature_vector

# -----------------------------
# Model Path
# -----------------------------
BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "models", "xgboost_fraud_model.pkl")

_model = None


# -----------------------------
# Load Model Once
# -----------------------------
def load_model():
    global _model

    if _model is not None:
        return _model

    if not os.path.exists(MODEL_PATH):
        print(f"⚠️ Model not found at {MODEL_PATH}")
        _model = None
        return None

    try:
        _model = joblib.load(MODEL_PATH)
        print("✅ XGBoost model loaded successfully")
        return _model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        _model = None
        return None


# -----------------------------
# Main Prediction Function
# -----------------------------
def predict_fraud(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict fraud probability using trained XGBoost model.
    Falls back to rule-based logic if model unavailable.
    """

    model = load_model()

    # If model not available → fallback
    if model is None:
        return fallback_prediction(claim_data)

    try:
        # Build features
        features_df: pd.DataFrame = build_feature_vector(claim_data)

        # Predict probability
        fraud_prob = float(model.predict_proba(features_df)[0][1])
        prediction = int(model.predict(features_df)[0])
        risk_score = int(fraud_prob * 100)

        return {
            "fraud_probability": fraud_prob,
            "prediction": prediction,
            "risk_score": risk_score,
            "model_used": "xgboost",
            "model_loaded": True,
        }

    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return fallback_prediction(claim_data)


# -----------------------------
# Fallback Logic (Safe Mode)
# -----------------------------
def fallback_prediction(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple rule-based fallback if model fails.
    """

    amount = claim_data.get("claim_amount", 0)
    previous_claims = claim_data.get("previous_claims_count", 0)
    doc_missing = claim_data.get("doc_missing_flag", 0)

    risk_score = 20

    if amount > 50000:
        risk_score += 30
    elif amount > 25000:
        risk_score += 20
    elif amount > 10000:
        risk_score += 10

    if previous_claims > 5:
        risk_score += 15

    if doc_missing:
        risk_score += 25

    risk_score = min(risk_score, 95)
    fraud_prob = risk_score / 100

    return {
        "fraud_probability": fraud_prob,
        "prediction": 1 if fraud_prob > 0.5 else 0,
        "risk_score": risk_score,
        "model_used": "fallback",
        "model_loaded": False,
    }
