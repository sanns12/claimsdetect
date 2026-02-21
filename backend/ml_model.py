"""
ML Model for Fraud Detection
This file handles loading the trained XGBoost model and making predictions.
"""

import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any

# Path to the trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "xgboost_fraud_model.pkl")

# Global model instance
_model = None

def load_model():
    """Load the trained XGBoost model"""
    global _model
    try:
        if os.path.exists(MODEL_PATH):
            _model = joblib.load(MODEL_PATH)
            print("✅ XGBoost model loaded successfully")
        else:
            print(f"⚠️ Model not found at {MODEL_PATH}. Using fallback prediction.")
            _model = None
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        _model = None

def train_model():
    """
    Train the XGBoost model (to be used by ML teammate)
    This function should only be called when training the model,
    not during normal API operation.
    """
    print("Loading dataset...")
    
    # Try multiple possible paths for the dataset
    possible_paths = [
        "backend/data/unified_claims_v1.csv",
        "data/unified_claims_v1.csv",
        "../data/unified_claims_v1.csv"
    ]
    
    df = None
    for path in possible_paths:
        if os.path.exists(path):
            df = pd.read_csv(path, low_memory=False)
            print(f"✅ Dataset loaded from {path}")
            break
    
    if df is None:
        raise FileNotFoundError("Dataset not found. Please ensure unified_claims_v1.csv is in the data directory.")
    
    print("Initial dataset shape:", df.shape)

    # Clean claimed_amount
    df["claimed_amount"] = df["claimed_amount"].astype(str).str.replace(",", "", regex=False)
    df["claimed_amount"] = pd.to_numeric(df["claimed_amount"], errors="coerce")

    # Convert required columns to numeric
    df["patient_age"] = pd.to_numeric(df["patient_age"], errors="coerce")
    df["is_fraud"] = pd.to_numeric(df["is_fraud"], errors="coerce")

    # Feature columns - you can expand this later
    feature_columns = [
        "patient_age",
        "claimed_amount"
    ]

    target_column = "is_fraud"

    # Drop rows with missing values only in these columns
    df = df.dropna(subset=feature_columns + [target_column])

    print("Dataset shape after cleaning:", df.shape)

    if len(df) == 0:
        raise ValueError("Dataset still empty after cleaning.")

    X = df[feature_columns]
    y = df[target_column]

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    from xgboost import XGBClassifier
    model = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        eval_metric="logloss",
        random_state=42
    )

    model.fit(X_train, y_train)

    # Evaluate
    from sklearn.metrics import classification_report, accuracy_score
    y_pred = model.predict(X_test)

    print("\nModel Performance:")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred))

    # Save model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"\n✅ Model saved to {MODEL_PATH}")
    return model

def predict_fraud(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict fraud probability for a claim
    
    Input: claim_data as dict with at least:
        - patient_age: int
        - claimed_amount: float
    
    Output example:
    {
        "fraud_probability": 0.12,
        "prediction": 0,  # 0 = genuine, 1 = fraud
        "risk_level": "low"
    }
    """
    global _model
    
    # Load model if not loaded
    if _model is None:
        load_model()
    
    # Extract features
    try:
        age = float(claim_data.get("patient_age", claim_data.get("age", 35)))
        amount = float(claim_data.get("claimed_amount", claim_data.get("amount", 5000)))
    except (ValueError, TypeError):
        # Fallback values if conversion fails
        age = 35
        amount = 5000
    
    # Create feature array
    features = np.array([[age, amount]])
    
    # Make prediction
    if _model is not None:
        try:
            fraud_probability = float(_model.predict_proba(features)[0][1])
            prediction = int(_model.predict(features)[0])
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            # Fallback to rule-based
            fraud_probability = min(amount / 100000, 0.5)  # Simple rule: higher amount = higher risk
            prediction = 1 if fraud_probability > 0.5 else 0
    else:
        # Rule-based fallback
        fraud_probability = min(amount / 100000, 0.5)
        prediction = 1 if fraud_probability > 0.5 else 0
    
    # Determine risk level
    if fraud_probability > 0.7:
        risk_level = "high"
    elif fraud_probability > 0.3:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return {
        "fraud_probability": round(fraud_probability, 4),
        "prediction": prediction,
        "risk_level": risk_level,
        "model_loaded": _model is not None
    }

def batch_predict(claims_data: list) -> list:
    """
    Predict fraud for multiple claims
    """
    results = []
    for claim in claims_data:
        results.append(predict_fraud(claim))
    return results

# Load model when module is imported
load_model()

# For testing
if __name__ == "__main__":
    # Test the model
    test_claim = {
        "patient_age": 45,
        "claimed_amount": 25000
    }
    result = predict_fraud(test_claim)
    print("Test prediction:", result)