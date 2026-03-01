"""
Fraud Predictor - Main entry point for fraud detection
Takes claim data, builds features, and returns fraud score with explanations
"""

import pandas as pd
import numpy as np
import joblib
import os

from .feature_builder import (
    clean_claim_amounts,
    create_age_groups,
    add_hospital_memory_features,
    add_patient_memory_features,
    encode_categorical_features,
    get_feature_columns
)
from .baseline_cost_model import build_cost_baseline, apply_cost_baseline
from .model_loader import load_model
from .risk_band_mapper import map_risk_band
from .shap_explainer import get_top_risk_factors

# Default model path
DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'fraud_test', 'models', 'xgboost_enhanced.pkl')

def run_fraud_engine(claim_data, model_path=None, historical_df=None, encoders=None, baseline=None):
    """
    Main fraud prediction function
    
    Args:
        claim_data: Dict with claim information matching input contract
        model_path: Path to trained model (optional)
        historical_df: Historical claims for feature calculation (required for full features)
        encoders: Pre-fitted encoders (optional)
        baseline: Pre-computed cost baseline (optional)
    
    Returns:
        Dict with fraud_risk_score, risk_band, top_risk_factors
    """
    try:
        # Convert input to DataFrame
        df_input = pd.DataFrame([claim_data])
        
        # Rename fields to match expected column names
        df_input.rename(columns={
            'claim_amount': 'claimed_amount'
        }, inplace=True)
        
        # Add metadata fields
        metadata = claim_data.get('metadata', {})
        for key, value in metadata.items():
            df_input[key] = value
        
        # Ensure all required columns exist
        required_cols = ['patient_age', 'hospital_id', 'diagnosis_code', 'billed_items_count', 
                        'previous_claims_count', 'insurer_id', 'doc_missing_flag']
        for col in required_cols:
            if col not in df_input.columns:
                df_input[col] = 0
        
        # Add placeholder columns that will be filled by feature engineering
        df_input['is_fraud'] = 0  # Placeholder, not used for prediction
        
        # Clean claim amounts
        df_input = clean_claim_amounts(df_input)
        
        # Create age groups
        df_input = create_age_groups(df_input)
        
        # If historical data provided, use it for feature engineering
        if historical_df is not None and len(historical_df) > 0:
            # Combine historical with current claim
            combined = pd.concat([historical_df, df_input], ignore_index=True)
            
            # Apply cost baseline if provided
            if baseline is not None:
                combined = apply_cost_baseline(combined, baseline)
            
            # Add hospital memory features
            combined = add_hospital_memory_features(combined)
            
            # Add patient memory features
            combined = add_patient_memory_features(combined)
            
            # Extract the current claim (last row)
            df_input = combined.iloc[-1:].copy()
            
        else:
            # No history - use default values
            df_input['expected_cost'] = df_input['claimed_amount']
            df_input['cost_deviation'] = 0
            df_input['deviation_ratio'] = 1.0
            df_input['hospital_claims_1yr'] = 0
            df_input['hospital_fraud_count_1yr'] = 0
            df_input['hospital_fraud_rate_1yr'] = 0.05  # Default 5%
            df_input['hospital_avg_deviation'] = 0
            df_input['patient_avg_amount'] = df_input['claimed_amount']
            df_input['patient_avg_deviation'] = 0
            df_input['patient_doc_missing_rate'] = df_input['doc_missing_flag'].fillna(0)
        
        # Encode categorical features
        if encoders is not None:
            df_input, _ = encode_categorical_features(df_input, encoders=encoders, fit=False)
        else:
            # Create temporary encoders (for single prediction)
            df_input, _ = encode_categorical_features(df_input, fit=True)
        
        # Get feature columns in correct order
        feature_cols = get_feature_columns()
        
        # Ensure all feature columns exist
        for col in feature_cols:
            if col not in df_input.columns:
                df_input[col] = 0
        
        # Select features
        X = df_input[feature_cols]
        
        # Load model
        if model_path is None:
            model_path = DEFAULT_MODEL_PATH
        
        model = load_model(model_path)
        if model is None:
            # Fallback to stub
            return run_stub(claim_data)
        
        # Make prediction
        fraud_probability = float(model.predict_proba(X)[0, 1])
        
        # Get risk factors
        top_factors = get_top_risk_factors(df_input[feature_cols], model, feature_cols)
        
        # Determine risk band
        risk_band = map_risk_band(fraud_probability)
        
        return {
            "fraud_risk_score": fraud_probability,
            "risk_band": risk_band,
            "top_risk_factors": top_factors
        }
        
    except Exception as e:
        print(f"Error in fraud engine: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback to stub on error
        return run_stub(claim_data)

def run_stub(claim_data):
    """
    Stub mode for testing - returns fixed output
    
    Args:
        claim_data: dict with claim information (not used in stub)
        
    Returns:
        dict with fixed fraud_risk_score, risk_band, top_risk_factors
    """
    return {
        "fraud_risk_score": 0.15,
        "risk_band": "low",
        "top_risk_factors": ["Stub mode - model not loaded"]
    }
