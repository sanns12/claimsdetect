# services/ml_service.py

from datetime import datetime
from app.ml.feature_engineering import build_feature_vector
from app.ml.ml_model import predict_fraud


def evaluate_claim(claim_data: dict) -> dict:
    """
    Runs full ML pipeline:
    - Feature engineering
    - Model inference
    - Risk scoring
    - Status classification
    """

    try:
        # ----------------------------
        # Feature Engineering
        # ----------------------------
        features_df = build_feature_vector(claim_data)

        # ----------------------------
        # ML Prediction
        # ----------------------------
        prediction = predict_fraud(claim_data)

        fraud_probability = prediction.get("fraud_probability", 0.0)
        risk_score = prediction.get(
            "risk_score",
            int(fraud_probability * 100)
        )
        factors = prediction.get("factors", [])

        # ----------------------------
        # Status Classification Logic
        # ----------------------------
        if fraud_probability > 0.8:
            status = "Flagged"
        elif fraud_probability > 0.6:
            status = "AI Processing"
        else:
            status = "Submitted"

        # ----------------------------
        # Duration Calculation
        # ----------------------------
        try:
            adm = datetime.fromisoformat(
                claim_data["admission_date"]
            )
            dis = datetime.fromisoformat(
                claim_data["discharge_date"]
            )
            duration_days = max((dis - adm).days, 0)
        except Exception:
            duration_days = 0

        return {
            "fraud_probability": fraud_probability,
            "risk_score": risk_score,
            "factors": factors,
            "status": status,
            "duration_days": duration_days
        }

    except Exception as e:
        raise Exception(f"ML evaluation failed: {str(e)}")
    