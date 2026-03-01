"""
Fraud Intelligence Module for MediSecure
Provides fraud risk scoring with XGBoost, SHAP explanations, and feature engineering
"""

__version__ = "1.0.0"

from .fraud_predictor import run_fraud_engine, run_stub
from .model_loader import train_model, load_model, save_model, train_test_split_stratified
from .feature_builder import get_feature_columns, encode_categorical_features, create_age_groups
from .feature_builder import clean_claim_amounts, add_hospital_memory_features, add_patient_memory_features
from .baseline_cost_model import build_cost_baseline, apply_cost_baseline
from .risk_band_mapper import map_risk_band
from .shap_explainer import get_top_risk_factors

__all__ = [
    'run_fraud_engine',
    'run_stub',
    'train_model',
    'load_model',
    'save_model',
    'train_test_split_stratified',
    'get_feature_columns',
    'encode_categorical_features',
    'create_age_groups',
    'clean_claim_amounts',
    'add_hospital_memory_features',
    'add_patient_memory_features',
    'build_cost_baseline',
    'apply_cost_baseline',
    'map_risk_band',
    'get_top_risk_factors'
]
