import pandas as pd
import numpy as np

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # Clean claimed_amount
    df["claimed_amount"] = df["claimed_amount"].astype(str).str.replace(",", "")
    df["claimed_amount"] = pd.to_numeric(df["claimed_amount"], errors="coerce")

    # Convert numerics safely
    df["patient_age"] = pd.to_numeric(df["patient_age"], errors="coerce")
    df["billed_items_count"] = pd.to_numeric(df["billed_items_count"], errors="coerce")
    df["previous_claims_count"] = pd.to_numeric(df["previous_claims_count"], errors="coerce")
    df["doc_missing_flag"] = pd.to_numeric(df["doc_missing_flag"], errors="coerce")

    # Fill missing numeric values
    df["billed_items_count"] = df["billed_items_count"].fillna(0)
    df["previous_claims_count"] = df["previous_claims_count"].fillna(0)
    df["doc_missing_flag"] = df["doc_missing_flag"].fillna(0)

    # Dates
    df["admission_date"] = pd.to_datetime(df["admission_date"], errors="coerce")
    df["discharge_date"] = pd.to_datetime(df["discharge_date"], errors="coerce")

    df["length_of_stay"] = (
        df["discharge_date"] - df["admission_date"]
    ).dt.days

    df["length_of_stay"] = df["length_of_stay"].fillna(0)

    # Age buckets
    df["age_0_18"] = ((df["patient_age"] <= 18)).astype(int)
    df["age_19_35"] = ((df["patient_age"] > 18) & (df["patient_age"] <= 35)).astype(int)
    df["age_36_50"] = ((df["patient_age"] > 35) & (df["patient_age"] <= 50)).astype(int)
    df["age_51_65"] = ((df["patient_age"] > 50) & (df["patient_age"] <= 65)).astype(int)
    df["age_65_plus"] = ((df["patient_age"] > 65)).astype(int)

    # Gender one-hot
    df["gender_M"] = (df["gender"] == "M").astype(int)
    df["gender_F"] = (df["gender"] == "F").astype(int)

    # Final features
    features = [
        "claimed_amount",
        "billed_items_count",
        "previous_claims_count",
        "doc_missing_flag",
        "length_of_stay",
        "age_0_18",
        "age_19_35",
        "age_36_50",
        "age_51_65",
        "age_65_plus",
        "gender_M",
        "gender_F"
    ]

    features_df = df[features]
    features_df = features_df.fillna(0)

    # 🔒 Force numeric safety
    features_df = features_df.astype(float)

    return features_df
def build_feature_vector(claim_data: dict) -> pd.DataFrame:
    """
    Convert single claim dict into model-ready feature dataframe
    """

    # Convert dict to DataFrame
    df = pd.DataFrame([{
        "claimed_amount": claim_data.get("claim_amount", 0),
        "patient_age": claim_data.get("age", 35),
        "gender": claim_data.get("gender", "M"),
        "admission_date": claim_data.get("admission_date"),
        "discharge_date": claim_data.get("discharge_date"),
        "billed_items_count": claim_data.get("billed_items_count", 0),
        "previous_claims_count": claim_data.get("previous_claims_count", 0),
        "doc_missing_flag": claim_data.get("doc_missing_flag", 0)
    }])

    # Run full feature engineering pipeline
    features_df = engineer_features(df)

    return features_df