<<<<<<< HEAD
import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from xgboost import XGBClassifier


def train_model():

    print("Loading dataset...")

    df = pd.read_csv("backend/data/unified_claims_v1.csv", low_memory=False)

    print("Initial dataset shape:", df.shape)

    # Clean claimed_amount
    df["claimed_amount"] = df["claimed_amount"].astype(str).str.replace(",", "", regex=False)
    df["claimed_amount"] = pd.to_numeric(df["claimed_amount"], errors="coerce")

    # Convert required columns to numeric
    df["patient_age"] = pd.to_numeric(df["patient_age"], errors="coerce")
    df["is_fraud"] = pd.to_numeric(df["is_fraud"], errors="coerce")

    # Only use columns that actually contain data
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

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        eval_metric="logloss",
        random_state=42
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("\nModel Performance:")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred))

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/xgboost_fraud_model.pkl")

    print("\nModel saved successfully.")
    return model
=======
"""
ML Model Stub
This file will be implemented by ML teammate.
DO NOT add logic here.
"""

def predict_fraud(claim_data: dict) -> dict:
    """
    Input: claim data as dict
    Output example:
    {
        "fraud_probability": 0.12,
        "prediction": "genuine"
    }
    """
    return {
        "fraud_probability": None,
        "prediction": "unknown"
    }
>>>>>>> 6da8e07e73dcf8da0a590226f0184853142cc9bc
