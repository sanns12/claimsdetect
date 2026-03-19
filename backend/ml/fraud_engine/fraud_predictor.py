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

DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'xgboost.pkl')
DEFAULT_PREPROCESSOR_PATH = os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'preprocessor.pkl')

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
        df_input['length_of_stay'] = 1  # Default value
        
        # Clean claim amounts
        df_input = clean_claim_amounts(df_input)
        
        # Create age groups
        df_input = create_age_groups(df_input)
        
        # Calculate derived features
        df_input['claimed_per_day'] = df_input['claimed_amount'] / df_input['length_of_stay']
        df_input['amount_per_item'] = df_input['claimed_amount'] / df_input['billed_items_count'].replace(0, 1)
        
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
        
        # === FIX: Prepare features exactly as model expects ===
        model_features = [
            'patient_age', 'gender', 'hospital_id', 'diagnosis_code', 'claimed_amount',
            'billed_items_count', 'previous_claims_count', 'insurer_id', 'doc_missing_flag',
            'length_of_stay', 'claimed_per_day', 'amount_per_item'
        ]
        
        # Ensure all features exist - use safe defaults that might be in training data
        for col in model_features:
            if col not in df_input.columns:
                if col == 'gender':
                    df_input[col] = 'M'  # Most common gender
                elif col == 'hospital_id':
                    df_input[col] = 'HOSP001'  # Default hospital
                elif col == 'diagnosis_code':
                    df_input[col] = 'A00'  # Default diagnosis
                elif col == 'insurer_id':
                    df_input[col] = 'INS001'  # Default insurer
                else:
                    df_input[col] = 0
        
        # Select features for model
        X = df_input[model_features].copy()
        
        # Convert categorical columns to string type
        cat_cols = ['gender', 'hospital_id', 'diagnosis_code', 'insurer_id']
        for col in cat_cols:
            if col in X.columns:
                X[col] = X[col].astype(str)
        
        # Load model
        if model_path is None:
            model_path = DEFAULT_MODEL_PATH
        
        model = load_model(model_path)
        if model is None:
            # Fallback to stub
            return run_stub(claim_data)
        
        # === FIX: Apply preprocessor dictionary correctly with unseen label handling ===
        if os.path.exists(DEFAULT_PREPROCESSOR_PATH):
            try:
                preprocessor = joblib.load(DEFAULT_PREPROCESSOR_PATH)
                
                if isinstance(preprocessor, dict):
                    print("✅ Preprocessor dictionary loaded")
                    
                    # Make a copy of X for processing
                    X_processed = X.copy()
                    
                    # Apply label encoders to categorical columns with unseen label handling
                    if 'label_encoders' in preprocessor:
                        for col, encoder in preprocessor['label_encoders'].items():
                            if col in X_processed.columns:
                                # Get the classes the encoder knows
                                known_classes = encoder.classes_.tolist()
                                
                                # Use the first class as default for unseen values
                                default_class = known_classes[0] if known_classes else 'M'
                                
                                # Handle unknown values before encoding
                                X_processed[col] = X_processed[col].apply(
                                    lambda x: x if x in known_classes else default_class
                                )
                                
                                # Now transform
                                X_processed[col] = encoder.transform(X_processed[col])
                    
                    # Apply scaler to numerical columns
                    if 'scaler' in preprocessor:
                        # Get numerical columns (excluding categorical ones)
                        if 'label_encoders' in preprocessor:
                            cat_cols = list(preprocessor['label_encoders'].keys())
                            num_cols = [c for c in X_processed.columns if c not in cat_cols]
                        else:
                            num_cols = X_processed.columns.tolist()
                        
                        if num_cols:
                            # Ensure numerical columns are float type
                            for col in num_cols:
                                X_processed[col] = pd.to_numeric(X_processed[col], errors='coerce').fillna(0)
                            
                            # Apply scaler
                            X_processed[num_cols] = preprocessor['scaler'].transform(X_processed[num_cols])
                    
                    # Make prediction with processed features
                    fraud_probability = float(model.predict_proba(X_processed)[0, 1])
                    
                else:
                    # Regular sklearn pipeline
                    X_processed = preprocessor.transform(X)
                    fraud_probability = float(model.predict_proba(X_processed)[0, 1])
                
                # Get risk factors
                top_factors = get_top_risk_factors(X, model, model_features)
                
            except Exception as e:
                print(f"⚠️ Preprocessor failed, using raw features: {e}")
                # For raw features, we need to encode categoricals for XGBoost
                X_raw = X.copy()
                for col in cat_cols:
                    if col in X_raw.columns:
                        X_raw[col] = pd.Categorical(X_raw[col]).codes
                fraud_probability = float(model.predict_proba(X_raw)[0, 1])
                top_factors = get_top_risk_factors(X_raw, model, model_features)
        else:
            # No preprocessor, use raw features with encoding
            X_raw = X.copy()
            for col in cat_cols:
                if col in X_raw.columns:
                    X_raw[col] = pd.Categorical(X_raw[col]).codes
            fraud_probability = float(model.predict_proba(X_raw)[0, 1])
            top_factors = get_top_risk_factors(X_raw, model, model_features)
        
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