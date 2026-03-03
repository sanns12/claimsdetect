import numpy as np
from datetime import datetime
from typing import Dict, List
import joblib
import os

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
    
    # Rule-based risk factors
    risk_factors = []
    flags = []
    
    # Amount-based risk
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
    
    # Age-based risk
    if age > 70:
        risk_factors.append({"name": "Patient Age", "impact": 25, "description": "Patient age > 70"})
    elif age < 18:
        risk_factors.append({"name": "Patient Age", "impact": 20, "description": "Patient age < 18"})
    else:
        risk_factors.append({"name": "Patient Age", "impact": 15, "description": "Patient age within normal range"})
    
    # Diagnosis-based risk (mock)
    high_risk_diagnoses = ["Cardiovascular", "Oncology", "Neurological"]
    if diagnosis in high_risk_diagnoses:
        risk_factors.append({"name": "Diagnosis", "impact": 30, "description": f"{diagnosis} requires enhanced verification"})
        flags.append({"type": "High Risk Diagnosis", "severity": "medium", "description": f"{diagnosis} has higher fraud probability"})
    
    # Calculate total risk score
    total_impact = sum(f["impact"] for f in risk_factors)
    risk_score = min(total_impact, 95)  # Cap at 95
    
    # Calculate fraud probability using ML model if available
    fraud_probability = 0.0
    
    if model:
        try:
            # Prepare features for model
            features = np.array([[age, amount, len(diagnosis), 1 if diagnosis in high_risk_diagnoses else 0]])
            fraud_probability = float(model.predict_proba(features)[0][1])
        except:
            # Fallback to rule-based
            fraud_probability = risk_score / 100
    else:
        # Rule-based fallback
        fraud_probability = risk_score / 100
    
    return {
        "risk_score": risk_score,
        "fraud_probability": fraud_probability,
        "factors": risk_factors,
        "flags": flags,
        "model_confidence": 0.85 if model else 0.70
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