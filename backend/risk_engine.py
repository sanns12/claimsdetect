import numpy as np
from datetime import datetime
from typing import Dict, List
import joblib
import os

# Import ML model
from ml_model import predict_fraud, get_model

# Load ML model
model_path = os.path.join(os.path.dirname(__file__), "models", "xgboost_fraud_model.pkl")
try:
    model = joblib.load(model_path)
    print("✅ ML Model loaded successfully")
except:
    model = None
    print("⚠️  ML Model not found, using rule-based fallback")

async def calculate_risk_score(claim_data: Dict) -> Dict:
    """Calculate risk score and fraud probability for a claim"""
    
    # Extract features
    age = claim_data.get("age", 35)
    amount = claim_data.get("claim_amount", 5000)
    diagnosis = claim_data.get("diagnosis", "")
    
    # Use ML model for fraud prediction
    ml_result = predict_fraud({
        "patient_age": age,
        "claimed_amount": amount
    })
    
    fraud_probability = ml_result.get("fraud_probability", 0)
    risk_score = int(fraud_probability * 100)  # Convert 0-1 to 0-100
    prediction = ml_result.get("prediction", 0)
    
    # Rule-based risk factors (still useful for explanations)
    risk_factors = []
    flags = []
    
    # Amount-based factor
    if amount > 50000:
        risk_factors.append({"name": "Claim Amount", "impact": 45, "description": "Amount exceeds $50,000"})
        flags.append({"type": "Amount Anomaly", "severity": "high", "description": "Claim amount is very high"})
    elif amount > 25000:
        risk_factors.append({"name": "Claim Amount", "impact": 30, "description": "Amount exceeds $25,000"})
        flags.append({"type": "Amount Anomaly", "severity": "medium", "description": "Claim amount is above average"})
    elif amount > 10000:
        risk_factors.append({"name": "Claim Amount", "impact": 20, "description": "Amount exceeds $10,000"})
    else:
        risk_factors.append({"name": "Claim Amount", "impact": 10, "description": "Amount within normal range"})
    
    # Age-based factor
    if age > 70:
        risk_factors.append({"name": "Patient Age", "impact": 25, "description": "Patient age > 70"})
    elif age < 18:
        risk_factors.append({"name": "Patient Age", "impact": 20, "description": "Patient age < 18"})
    else:
        risk_factors.append({"name": "Patient Age", "impact": 15, "description": "Patient age within normal range"})
    
    # Diagnosis-based risk
    high_risk_diagnoses = ["Cardiovascular", "Oncology", "Neurological"]
    if diagnosis in high_risk_diagnoses:
        risk_factors.append({"name": "Diagnosis", "impact": 30, "description": f"{diagnosis} requires enhanced verification"})
        flags.append({"type": "High Risk Diagnosis", "severity": "medium", "description": f"{diagnosis} has higher fraud probability"})
    
    # Add ML prediction as a factor if high risk
    if prediction == 1:
        flags.append({
            "type": "ML Flagged",
            "severity": "high" if fraud_probability > 0.7 else "medium",
            "description": f"ML model flagged with {fraud_probability:.0%} confidence"
        })
    
    # Add ML confidence to risk factors
    risk_factors.append({
        "name": "ML Model Confidence",
        "impact": int(fraud_probability * 50),  # Scale impact based on probability
        "description": f"XGBoost model predicts {fraud_probability:.0%} fraud probability"
    })
    
    # Calculate model confidence
    model_confidence = fraud_probability if prediction == 1 else 1 - fraud_probability
    
    return {
        "risk_score": risk_score,
        "fraud_probability": fraud_probability,
        "prediction": prediction,
        "factors": risk_factors,
        "flags": flags,
        "model_confidence": round(model_confidence, 2),
        "model_loaded": ml_result.get("model_loaded", False)
    }

async def batch_risk_analysis(claims: List[Dict]) -> List[Dict]:
    """Analyze multiple claims"""
    results = []
    for claim in claims:
        analysis = await calculate_risk_score(claim)
        results.append({
            "claim_id": claim.get("claim_number"),
            **analysis
        })
    return results