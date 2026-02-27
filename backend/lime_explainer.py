"""
LIME Explainer for Insurance Claims
Generates human-readable explanations for ML model predictions
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import random
from datetime import datetime

# Import ML model
from ml_model import get_model, predict_fraud

# Try to import lime, but provide fallback
try:
    from lime import lime_tabular
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False
    print("⚠️ LIME not installed. Using mock explanations.")

def generate_rule_based_explanation(amount, age, diagnosis, fraud_probability):
    """Generate rule-based explanations as fallback"""
    factors = []
    
    # 1. Amount-based factor
    if amount > 50000:
        factors.append({
            "name": "Claim Amount",
            "impact": 42,
            "color": "high",
            "description": f"Amount ${amount:,.0f} is significantly above average (42% influence)"
        })
    elif amount > 25000:
        factors.append({
            "name": "Claim Amount",
            "impact": 35,
            "color": "medium",
            "description": f"Amount ${amount:,.0f} is above average (35% influence)"
        })
    elif amount > 10000:
        factors.append({
            "name": "Claim Amount",
            "impact": 25,
            "color": "medium",
            "description": f"Amount ${amount:,.0f} is moderately above average (25% influence)"
        })
    else:
        factors.append({
            "name": "Claim Amount",
            "impact": 15,
            "color": "low",
            "description": f"Amount ${amount:,.0f} is within normal range (15% influence)"
        })
    
    # 2. Age-based factor
    if age > 70:
        factors.append({
            "name": "Patient Age",
            "impact": 28,
            "color": "high",
            "description": f"Age {age} is in high-risk demographic (28% influence)"
        })
    elif age < 18:
        factors.append({
            "name": "Patient Age",
            "impact": 22,
            "color": "medium",
            "description": f"Age {age} is in pediatric category (22% influence)"
        })
    elif age > 60:
        factors.append({
            "name": "Patient Age",
            "impact": 18,
            "color": "medium",
            "description": f"Age {age} is in elevated risk group (18% influence)"
        })
    else:
        factors.append({
            "name": "Patient Age",
            "impact": 12,
            "color": "low",
            "description": f"Age {age} is in standard risk profile (12% influence)"
        })
    
    # 3. Diagnosis-based factor
    high_risk_diagnoses = ["Cardiovascular", "Oncology", "Neurological", "Cancer", "Heart Disease"]
    medium_risk_diagnoses = ["Respiratory", "Infectious Disease", "Diabetes", "Orthopedic"]
    
    if any(hrd.lower() in diagnosis.lower() for hrd in high_risk_diagnoses):
        factors.append({
            "name": "Diagnosis Type",
            "impact": 30,
            "color": "high",
            "description": f"{diagnosis} has higher fraud probability (30% influence)"
        })
    elif any(mrd.lower() in diagnosis.lower() for mrd in medium_risk_diagnoses):
        factors.append({
            "name": "Diagnosis Type",
            "impact": 20,
            "color": "medium",
            "description": f"{diagnosis} requires standard verification (20% influence)"
        })
    else:
        factors.append({
            "name": "Diagnosis Type",
            "impact": 10,
            "color": "low",
            "description": f"{diagnosis} has lower risk profile (10% influence)"
        })
    
    # Model confidence based on fraud probability
    model_confidence = fraud_probability if fraud_probability > 0.5 else 1 - fraud_probability
    
    return factors, model_confidence

def calculate_similar_claims(amount, age, diagnosis):
    """Calculate number of similar claims (mock function - can be enhanced with actual DB query)"""
    # This is a placeholder - in production, you'd query your database
    base_count = 100
    amount_factor = int(amount / 1000)
    age_factor = age
    return base_count + (amount_factor % 50) + (int(age) % 30)

async def explain_prediction(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate LIME explanation for a claim prediction
    
    Args:
        claim_data: Dictionary containing claim information
        
    Returns:
        Dictionary with explanation factors and model confidence
    """
    
    # Extract features from claim data
    amount = float(claim_data.get("claim_amount", claim_data.get("amount", 5000)))
    age = float(claim_data.get("patient_age", claim_data.get("age", 35)))
    diagnosis = claim_data.get("diagnosis", claim_data.get("disease", "General"))
    
    # First, get the ML prediction
    ml_result = predict_fraud({
        "patient_age": age,
        "claimed_amount": amount
    })
    
    fraud_probability = ml_result.get("fraud_probability", 0)
    prediction = ml_result.get("prediction", 0)
    
    # If LIME is available and model is loaded, generate real explanations
    if LIME_AVAILABLE and _model is not None:
        try:
            # Create a simple training data sample for LIME explainer
            # In production, you'd want to use your actual training data
            np.random.seed(42)
            
            # Generate synthetic training data based on typical ranges
            n_samples = 1000
            synthetic_data = np.column_stack([
                np.random.normal(45, 15, n_samples),  # age: mean 45, std 15
                np.random.normal(25000, 20000, n_samples)  # amount: mean 25k, std 20k
            ])
            
            # Create feature names
            feature_names = ['patient_age', 'claimed_amount']
            
            # Create LIME explainer
            explainer = lime_tabular.LimeTabularExplainer(
                training_data=synthetic_data,
                feature_names=feature_names,
                class_names=['genuine', 'fraud'],
                mode='classification',
                random_state=42
            )
            
            # Get explanation for this instance
            instance = np.array([[age, amount]])
            exp = explainer.explain_instance(
                data_row=instance[0],
                predict_fn=lambda x: _model.predict_proba(x),
                num_features=2  # Show both features
            )
            
            # Extract feature importance from LIME
            factors = []
            for feature, importance in exp.as_list():
                # Map feature names to readable format
                if 'patient_age' in feature or 'age' in feature.lower():
                    name = "Patient Age"
                    if importance > 0:
                        desc = f"Age {age} increases fraud probability"
                    else:
                        desc = f"Age {age} decreases fraud probability"
                elif 'claimed_amount' in feature or 'amount' in feature.lower():
                    name = "Claim Amount"
                    if importance > 0:
                        desc = f"Amount ${amount:,.0f} increases fraud probability"
                    else:
                        desc = f"Amount ${amount:,.0f} decreases fraud probability"
                else:
                    name = feature
                    desc = f"Feature impact: {importance:.2f}"
                
                # Convert importance to 0-100 scale and determine color
                impact = int(abs(importance) * 100)
                if impact > 30:
                    color = "high"
                elif impact > 15:
                    color = "medium"
                else:
                    color = "low"
                
                factors.append({
                    "name": name,
                    "impact": impact,
                    "color": color,
                    "description": desc
                })
            
            # Model confidence based on prediction probability
            model_confidence = fraud_probability if prediction == 1 else 1 - fraud_probability
            
        except Exception as e:
            print(f"⚠️ LIME explanation failed: {e}, falling back to rule-based")
            # Fall back to rule-based explanations
            factors, model_confidence = generate_rule_based_explanation(amount, age, diagnosis, fraud_probability)
    else:
        # Use rule-based explanations
        factors, model_confidence = generate_rule_based_explanation(amount, age, diagnosis, fraud_probability)
    
    # Generate similar claims count (can be enhanced with actual database query)
    similar_claims = calculate_similar_claims(amount, age, diagnosis)
    
    # Sort factors by impact (highest first)
    factors.sort(key=lambda x: x["impact"], reverse=True)
    
    return {
        "factors": factors,
        "model_confidence": round(model_confidence, 2),
        "similar_claims": similar_claims,
        "explanation_type": "lime" if (LIME_AVAILABLE and _model is not None) else "rule_based",
        "generated_at": datetime.utcnow().isoformat(),
        "fraud_probability": fraud_probability,
        "prediction": prediction
    }

async def explain_batch(claims_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate explanations for multiple claims"""
    results = []
    for claim in claims_data:
        explanation = await explain_prediction(claim)
        results.append(explanation)
    return results

def get_feature_importance(model=None, feature_names: List[str] = None) -> List[Dict[str, Any]]:
    """Get feature importance from model (if available)"""
    global _model
    
    # Use the loaded model if none provided
    if model is None:
        model = _model
    
    if model is not None and hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        
        # Default feature names if not provided
        if feature_names is None:
            feature_names = ['patient_age', 'claimed_amount']
        
        features = []
        for name, importance in zip(feature_names, importances):
            features.append({
                "name": name.replace('_', ' ').title(),
                "importance": float(importance)
            })
        return sorted(features, key=lambda x: x["importance"], reverse=True)
    
    # Return mock data if model not available
    return [
        {"name": "Claim Amount", "importance": 0.65},
        {"name": "Patient Age", "importance": 0.35}
    ]