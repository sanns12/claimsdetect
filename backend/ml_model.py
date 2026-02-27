"""
XGBoost Fraud Detection Model
Pure ML layer – no business logic.
"""

import os
import joblib
import pandas as pd
from typing import Dict, Any
from feature_engineering import engineer_features

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "xgboost_fraud_model.pkl")

_model = None
_feature_order = None


def load_model():
    global _model, _feature_order

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("XGBoost model not found. Train the model first.")

    _model = joblib.load(MODEL_PATH)
    _feature_order = list(_model.feature_names_in_)

    print("✅ XGBoost model loaded")
    print("Expected features:", _feature_order)


def predict_fraud(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    global _model, _feature_order

    if _model is None:
        load_model()

    # Convert to DataFrame
    df = pd.DataFrame([claim_data])

    # Engineer features
    features_df = engineer_features(df)

    # Ensure correct column order
    features_df = features_df[_feature_order]
    features_df = features_df.fillna(0)

    # Predict
    probability = float(_model.predict_proba(features_df)[0][1])
    prediction = int(_model.predict(features_df)[0])

    return {
    "fraud_probability": round(probability, 4),
    "prediction": prediction,
    "features_df": features_df,
    "model": _model,
    "feature_order": _feature_order
}
