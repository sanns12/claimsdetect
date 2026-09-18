"""
Fraud Intelligence Module for MediSecure

Core (ML / fusion) layer:
    feature_builder   canonical feature contract + claim feature engineering
    model_loader      model bundle persistence
    fraud_predictor   ML inference (fraud probability, predicted class)
    shap_explainer    SHAP explanation of the actual ML prediction
    evidence_fusion   combines ML + behavior + anomaly + network + document
    risk_band_mapper  probability -> low / medium / high

Independent evidence engines (developed separately, consumed through the
feature contract; each exposes ``analyze(...)`` and returns a flat dict):
    behavior_engine, anomaly_engine, graph_engine

The orchestration entry point is ``backend/risk_engine.py``.
"""

__version__ = "2.0.0"

from .feature_builder import (
    CONTRACT_VERSION,
    FEATURE_ORDER,
    SECTION_FEATURES,
    build_contract,
    flatten_contract,
    get_feature_columns,
)
from .model_loader import load_model, save_model
from .risk_band_mapper import map_risk_band

__all__ = [
    "CONTRACT_VERSION",
    "FEATURE_ORDER",
    "SECTION_FEATURES",
    "build_contract",
    "flatten_contract",
    "get_feature_columns",
    "load_model",
    "save_model",
    "map_risk_band",
]
