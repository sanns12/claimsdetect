"""
Feature Builder - All feature engineering functions
Phase 2: Age groups, cost baseline
Phase 3: Hospital memory, patient memory, encoding
"""

import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.preprocessing import LabelEncoder

def fix_dates(df):
    """
    Fix date columns by handling multiple formats
    
    Args:
        df: DataFrame with 'admission_date' and 'discharge_date'
        
    Returns:
        DataFrame with fixed dates
    """
    df = df.copy()
    
    def parse_date(date_val):
        if pd.isna(date_val):
            return pd.NaT
            
        if isinstance(date_val, str):
            date_str = date_val.strip()
            
            # Remove time part if present
            if ' ' in date_str:
                date_str = date_str.split()[0]
            
            # Try different formats
            try:
                # Try dd/mm/yyyy format (common in some datasets)
                if '/' in date_str:
                    parts = date_str.split('/')
                    if len(parts) == 3:
                        if len(parts[2]) == 4:  # Year is 4 digits
                            return pd.to_datetime(date_str, format='%d/%m/%Y', errors='coerce')
                        else:
                            return pd.to_datetime(date_str, format='%d/%m/%y', errors='coerce')
                
                # Try yyyy-mm-dd format
                elif '-' in date_str:
                    return pd.to_datetime(date_str, format='%Y-%m-%d', errors='coerce')
                
                # Let pandas infer as last resort
                else:
                    return pd.to_datetime(date_str, errors='coerce')
                    
            except:
                return pd.NaT
        else:
            return pd.to_datetime(date_val, errors='coerce')
    
    if 'admission_date' in df.columns:
        df['admission_date'] = df['admission_date'].apply(parse_date)
    
    if 'discharge_date' in df.columns:
        df['discharge_date'] = df['discharge_date'].apply(parse_date)
    
    # Drop rows with invalid dates
    original_len = len(df)
    df = df.dropna(subset=['admission_date'])
    if len(df) < original_len:
        print(f"Dropped {original_len - len(df)} rows with invalid admission dates")
    
    return df

def clean_claim_amounts(df):
    """
    Clean and convert claim_amount to numeric
    
    Args:
        df: DataFrame with 'claimed_amount' column
        
    Returns:
        DataFrame with cleaned claimed_amount
    """
    df = df.copy()
    
    if 'claimed_amount' in df.columns:
        # Convert to string first
        df['claimed_amount'] = df['claimed_amount'].astype(str)
        
        # Clean the strings
        df['claimed_amount'] = df['claimed_amount'].str.replace(',', '', regex=False)
        df['claimed_amount'] = df['claimed_amount'].str.replace('"', '', regex=False)
        df['claimed_amount'] = df['claimed_amount'].str.replace(' ', '', regex=False)
        df['claimed_amount'] = df['claimed_amount'].str.strip()
        
        # Convert to numeric, coerce errors to NaN
        df['claimed_amount'] = pd.to_numeric(df['claimed_amount'], errors='coerce')
        
        # Drop rows with invalid amounts
        original_len = len(df)
        df = df.dropna(subset=['claimed_amount'])
        if len(df) < original_len:
            print(f"Dropped {original_len - len(df)} rows with invalid claim amounts")
    
    return df

def create_age_groups(df):
    """
    Create age group buckets from patient_age
    
    Args:
        df: DataFrame with 'patient_age' column
        
    Returns:
        DataFrame with added 'age_group' column
    """
    df = df.copy()
    
    def get_age_group(age):
        if age <= 18:
            return '0-18'
        elif age <= 35:
            return '19-35'
        elif age <= 50:
            return '36-50'
        elif age <= 65:
            return '51-65'
        else:
            return '65+'
    
    df['age_group'] = df['patient_age'].apply(get_age_group)
    
    return df

def add_hospital_memory_features(df, lookback_days=365):
    """
    Add hospital-level memory features (1-year lookback)
    
    Args:
        df: DataFrame with 'hospital_id', 'admission_date', 'is_fraud', 'cost_deviation'
        lookback_days: Number of days to look back (default 365)
        
    Returns:
        DataFrame with added hospital memory features
    """
    df = df.copy()
    
    # Ensure claimed_amount is numeric
    if 'claimed_amount' in df.columns and df['claimed_amount'].dtype == 'object':
        df = clean_claim_amounts(df)
    
    # Fix dates first
    df = fix_dates(df)
    
    # Ensure we have valid dates
    if df['admission_date'].isna().any():
        print("Warning: Some dates could not be parsed, dropping those rows")
        df = df.dropna(subset=['admission_date'])
    
    # Sort by hospital and date
    df = df.sort_values(['hospital_id', 'admission_date']).reset_index(drop=True)
    
    # Initialize columns
    df['hospital_claims_1yr'] = 0
    df['hospital_fraud_count_1yr'] = 0
    df['hospital_fraud_rate_1yr'] = df['is_fraud'].mean() if 'is_fraud' in df.columns else 0.05
    df['hospital_avg_deviation'] = 0.0
    
    # Process each hospital
    for hospital in df['hospital_id'].unique():
        hospital_mask = df['hospital_id'] == hospital
        hospital_indices = df[hospital_mask].index
        
        for i, idx in enumerate(hospital_indices):
            current_date = df.loc[idx, 'admission_date']
            one_year_back = current_date - timedelta(days=lookback_days)
            
            # Find previous claims from same hospital in last year
            prev_claims = df[(df['hospital_id'] == hospital) & 
                             (df['admission_date'] < current_date) & 
                             (df['admission_date'] >= one_year_back)]
            
            if len(prev_claims) > 0:
                df.loc[idx, 'hospital_claims_1yr'] = len(prev_claims)
                df.loc[idx, 'hospital_fraud_count_1yr'] = prev_claims['is_fraud'].sum() if 'is_fraud' in prev_claims.columns else 0
                df.loc[idx, 'hospital_fraud_rate_1yr'] = prev_claims['is_fraud'].mean() if 'is_fraud' in prev_claims.columns else 0.05
                df.loc[idx, 'hospital_avg_deviation'] = prev_claims['cost_deviation'].mean() if 'cost_deviation' in prev_claims.columns else 0.0
    
    return df

def add_patient_memory_features(df, lookback_days=365):
    """
    Add patient-level memory features (1-year lookback)
    
    Args:
        df: DataFrame with 'patient_id', 'admission_date', 'claimed_amount', 
            'cost_deviation', 'doc_missing_flag'
        lookback_days: Number of days to look back (default 365)
        
    Returns:
        DataFrame with added patient memory features
    """
    df = df.copy()
    
    # Ensure claimed_amount is numeric
    if 'claimed_amount' in df.columns and df['claimed_amount'].dtype == 'object':
        df = clean_claim_amounts(df)
    
    # Create patient_id if not exists (using claim_id prefix)
    if 'patient_id' not in df.columns and 'claim_id' in df.columns:
        df['patient_id'] = df['claim_id'].astype(str).str[:5]
    elif 'patient_id' not in df.columns:
        df['patient_id'] = 'P' + df.index.astype(str)
    
    # Fix dates first
    df = fix_dates(df)
    
    # Sort by patient and date
    df = df.sort_values(['patient_id', 'admission_date']).reset_index(drop=True)
    
    # Initialize columns with defaults
    df['patient_avg_amount'] = 0.0
    df['patient_avg_deviation'] = 0.0
    df['patient_doc_missing_rate'] = 0.0
    
    # Process each patient
    for patient in df['patient_id'].unique():
        patient_mask = df['patient_id'] == patient
        patient_indices = df[patient_mask].index
        
        if len(patient_indices) > 1:
            # Calculate expanding averages
            for i, idx in enumerate(patient_indices):
                if i > 0:  # Skip first claim (no history)
                    prev_indices = patient_indices[:i]
                    if 'claimed_amount' in df.columns:
                        df.loc[idx, 'patient_avg_amount'] = df.loc[prev_indices, 'claimed_amount'].mean()
                    if 'cost_deviation' in df.columns:
                        df.loc[idx, 'patient_avg_deviation'] = df.loc[prev_indices, 'cost_deviation'].mean()
                    if 'doc_missing_flag' in df.columns:
                        df.loc[idx, 'patient_doc_missing_rate'] = df.loc[prev_indices, 'doc_missing_flag'].mean()
    
    # Fill any remaining NaN values
    df['patient_avg_amount'] = df['patient_avg_amount'].fillna(df['claimed_amount'].mean() if 'claimed_amount' in df.columns else 0)
    df['patient_avg_deviation'] = df['patient_avg_deviation'].fillna(0)
    df['patient_doc_missing_rate'] = df['patient_doc_missing_rate'].fillna(df['doc_missing_flag'].mean() if 'doc_missing_flag' in df.columns else 0)
    
    return df

def encode_categorical_features(df, encoders=None, fit=True):
    """
    Encode categorical variables to numeric
    
    Args:
        df: DataFrame with categorical columns
        encoders: Dictionary of existing encoders (for transform mode)
        fit: Whether to fit new encoders (True) or use existing (False)
        
    Returns:
        DataFrame with encoded columns, and encoders dictionary
    """
    df = df.copy()
    
    if fit:
        encoders = {}
        
        # Gender
        if 'gender' in df.columns:
            le = LabelEncoder()
            df['gender_encoded'] = le.fit_transform(df['gender'].astype(str))
            encoders['gender'] = le
        else:
            df['gender_encoded'] = 0
        
        # Hospital
        if 'hospital_id' in df.columns:
            le = LabelEncoder()
            df['hospital_encoded'] = le.fit_transform(df['hospital_id'].astype(str))
            encoders['hospital'] = le
        else:
            df['hospital_encoded'] = 0
        
        # Insurer
        if 'insurer_id' in df.columns:
            le = LabelEncoder()
            df['insurer_encoded'] = le.fit_transform(df['insurer_id'].astype(str))
            encoders['insurer'] = le
        else:
            df['insurer_encoded'] = 0
        
        # Age group
        if 'age_group' in df.columns:
            le = LabelEncoder()
            df['age_group_encoded'] = le.fit_transform(df['age_group'].astype(str))
            encoders['age_group'] = le
        else:
            df['age_group_encoded'] = 0
        
        # Diagnosis
        if 'diagnosis_code' in df.columns:
            le = LabelEncoder()
            df['diagnosis_encoded'] = le.fit_transform(df['diagnosis_code'].astype(str))
            encoders['diagnosis'] = le
        else:
            df['diagnosis_encoded'] = 0
        
    else:
        # Use existing encoders
        if 'gender' in df.columns and 'gender' in encoders:
            df['gender_encoded'] = encoders['gender'].transform(df['gender'].astype(str))
        else:
            df['gender_encoded'] = 0
            
        if 'hospital_id' in df.columns and 'hospital' in encoders:
            df['hospital_encoded'] = encoders['hospital'].transform(df['hospital_id'].astype(str))
        else:
            df['hospital_encoded'] = 0
            
        if 'insurer_id' in df.columns and 'insurer' in encoders:
            df['insurer_encoded'] = encoders['insurer'].transform(df['insurer_id'].astype(str))
        else:
            df['insurer_encoded'] = 0
            
        if 'age_group' in df.columns and 'age_group' in encoders:
            df['age_group_encoded'] = encoders['age_group'].transform(df['age_group'].astype(str))
        else:
            df['age_group_encoded'] = 0
            
        if 'diagnosis_code' in df.columns and 'diagnosis' in encoders:
            df['diagnosis_encoded'] = encoders['diagnosis'].transform(df['diagnosis_code'].astype(str))
        else:
            df['diagnosis_encoded'] = 0
    
    return df, encoders

def get_feature_columns():
    """
    Return the list of feature columns in the correct order
    
    Returns:
        List of feature column names
    """
    return [
        'patient_age',
        'gender_encoded',
        'claimed_amount',
        'billed_items_count',
        'previous_claims_count',
        'insurer_encoded',
        'doc_missing_flag',
        'diagnosis_encoded',
        'expected_cost',
        'cost_deviation',
        'deviation_ratio',
        'hospital_claims_1yr',
        'hospital_fraud_count_1yr',
        'hospital_fraud_rate_1yr',
        'hospital_avg_deviation',
        'patient_avg_amount',
        'patient_avg_deviation',
        'patient_doc_missing_rate'
    ]