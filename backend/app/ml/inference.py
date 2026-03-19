# backend/ml/inference.py

import os
import joblib
from typing import Dict, Any, List
import pandas as pd
from app.ml.explainability import explain_prediction
from app.ml.feature_engineering import build_feature_vector


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "artifacts",
    "xgboost_fraud_model.pkl"
)

_model = None


def load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}"
            )
        _model = joblib.load(MODEL_PATH)


def predict_fraud(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    global _model

    if _model is None:
        load_model()

    try:
        features_df = build_feature_vector(claim_data)

        fraud_prob = float(_model.predict_proba(features_df)[0][1])
        prediction = int(_model.predict(features_df)[0])
        risk_score = int(fraud_prob * 100)

        explanation = explain_prediction(_model, features_df)

        return {
            "fraud_probability": fraud_prob,
            "prediction": prediction,
            "risk_score": risk_score,
            "factors": explanation,
            "model_used": "xgboost",
            "model_loaded": True
        }

    except Exception:
        return fallback_prediction(claim_data)


# ---------------------------------------
# Fallback Rule-Based Model
# ---------------------------------------

def fallback_prediction(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    amount = claim_data.get("claim_amount", 5000)
    doc_missing = claim_data.get("doc_missing_flag", 0)

    risk_score = 30

    if amount > 50000:
        risk_score += 30
    elif amount > 25000:
        risk_score += 20
    elif amount > 10000:
        risk_score += 10

    if doc_missing:
        risk_score += 30

    risk_score = min(risk_score, 95)
    fraud_prob = risk_score / 100

    return {
        "fraud_probability": fraud_prob,
        "prediction": 1 if fraud_prob > 0.5 else 0,
        "risk_score": risk_score,
        "model_used": "fallback",
        "model_loaded": False
    }

