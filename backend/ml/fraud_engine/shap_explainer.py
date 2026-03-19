"""
SHAP Explainer - Provides explanations for fraud predictions
"""

import shap
import numpy as np

def get_top_risk_factors(df, model, feature_columns, n_factors=3):
    """
    Get top risk factors using SHAP
    
    Args:
        df: Single row DataFrame with features
        model: Trained XGBoost model
        feature_columns: List of feature names
        n_factors: Number of top factors to return
    
    Returns:
        List of factor descriptions
    """
    try:
        # Create SHAP explainer
        explainer = shap.TreeExplainer(model)
        
        # Get SHAP values
        X = df[feature_columns].values
        shap_values = explainer.shap_values(X)
        
        # Get top features by absolute SHAP value
        feature_impacts = list(zip(feature_columns, shap_values[0]))
        feature_impacts.sort(key=lambda x: abs(x[1]), reverse=True)
        
        # Format as readable factors
        factors = []
        for feature, impact in feature_impacts[:n_factors]:
            # Clean up feature name
            clean_name = feature.replace('_', ' ').title()
            direction = "increases" if impact > 0 else "decreases"
            factors.append(f"{clean_name} {direction} fraud probability")
        
        return factors
    except Exception as e:
        print(f"SHAP error: {e}")
        return ["SHAP explanation unavailable - using rule-based fallback"]
