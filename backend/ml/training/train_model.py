import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
from pathlib import Path
# Import feature engineering from fraud_engine module
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from fraud_engine.feature_builder import clean_claim_amounts, create_age_groups

def engineer_features(df):
    """Simple feature engineering for training. Adapt as needed for your dataset."""
    df = df.copy()
    if 'claimed_amount' in df.columns:
        df = clean_claim_amounts(df)
    if 'patient_age' in df.columns or 'age' in df.columns:
        age_col = 'patient_age' if 'patient_age' in df.columns else 'age'
        df[age_col] = pd.to_numeric(df[age_col], errors='coerce')
    return df

def main():

    print("Loading dataset...")
    df = pd.read_csv("data/unified_claims_v1.csv")

    print("Engineering features...")
    X = engineer_features(df)
    y = df["is_fraud"]
    X.to_csv("models/lime_background_data.csv", index=False)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Training XGBoost...")
    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=42
    )

    model.fit(X_train, y_train)

    print("Evaluating...")
    preds = model.predict(X_test)
    print(classification_report(y_test, preds))

    Path("models").mkdir(exist_ok=True)
    joblib.dump(model, "models/xgboost_fraud_model.pkl")

    print("✅ Model saved successfully.")

if __name__ == "__main__":
    main()