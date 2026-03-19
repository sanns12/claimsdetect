import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
from pathlib import Path
from app.ml.feature_engineering import engineer_features

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