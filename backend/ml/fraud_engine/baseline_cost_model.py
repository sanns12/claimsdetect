"""
Baseline Cost Model - Phase 2
Calculates expected cost per (diagnosis, age group) using legitimate claims
"""

import pandas as pd
import numpy as np

def build_cost_baseline(df):
    """
    Build cost baseline from legitimate claims
    
    Args:
        df: DataFrame with 'diagnosis_code', 'age_group', 'claimed_amount', 'is_fraud'
    
    Returns:
        DataFrame with baseline per diagnosis-age group
    """
    # Filter legitimate claims
    legit_claims = df[df['is_fraud'] == 0]
    
    # Group by diagnosis and age group
    baseline = legit_claims.groupby(['diagnosis_code', 'age_group'])['claimed_amount'].agg(['mean', 'std', 'count']).reset_index()
    baseline.columns = ['diagnosis_code', 'age_group', 'expected_cost', 'cost_std', 'baseline_count']
    
    return baseline

def apply_cost_baseline(df, baseline):
    """
    Apply baseline to dataframe and calculate deviation features
    
    Args:
        df: Original dataframe
        baseline: Baseline dataframe from build_cost_baseline
    
    Returns:
        DataFrame with added baseline features
    """
    # Make a copy to avoid modifying original
    df = df.copy()
    
    # Merge baseline
    df = df.merge(baseline, on=['diagnosis_code', 'age_group'], how='left')
    
    # Fill missing with overall average from legitimate claims
    overall_avg = df[df['is_fraud']==0]['claimed_amount'].mean()
    df['expected_cost'] = df['expected_cost'].fillna(overall_avg)
    df['cost_std'] = df['cost_std'].fillna(df['cost_std'].mean())
    
    # Calculate deviation features
    df['cost_deviation'] = df['claimed_amount'] - df['expected_cost']
    df['deviation_ratio'] = df['claimed_amount'] / df['expected_cost']
    
    # Handle infinite values
    df['deviation_ratio'] = df['deviation_ratio'].replace([np.inf, -np.inf], 10.0)
    
    return df
