# services/ml_service.py

from datetime import datetime
from ml.fraud_engine.fraud_predictor import run_fraud_engine


def evaluate_claim(claim_data: dict) -> dict:
    """
    Runs full ML pipeline:
    - Feature engineering
    - Model inference
    - Risk scoring
    - Status classification
    """

    try:
        # Normalize request keys for the fraud engine contract.
        engine_input = dict(claim_data)
        if "patient_age" not in engine_input:
            engine_input["patient_age"] = engine_input.get("age", 0)

        prediction = run_fraud_engine(engine_input)

        fraud_probability = prediction.get("fraud_risk_score", 0.0)
        risk_score = int(fraud_probability * 100)
        factors = prediction.get("top_risk_factors", [])

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
    