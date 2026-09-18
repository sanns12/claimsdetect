"""
Fraud Predictor - ML inference only.

Responsibility: turn the feature contract into a fraud probability with the
trained model bundle.  It does NOT compute document similarity, graph
relationships or behavioral statistics - those arrive as upstream features
(see feature_builder) - and it does NOT decide the final risk score (see
evidence_fusion).

The model output is a MODEL SCORE learned from the historical labels.  Its
scale reflects the training prevalence (see ``model_info``), so it is not a
calibrated real-world probability of fraud.
"""

from typing import Any, Dict, Mapping, Optional, Tuple

import pandas as pd

from .feature_builder import CONTRACT_VERSION, build_contract, flatten_contract
from .model_loader import load_model
from .risk_band_mapper import map_risk_band
from .shap_explainer import explain_prediction, top_risk_factor_strings


def model_info(bundle: Mapping[str, Any]) -> Dict[str, Any]:
    """Provenance of the model behind a prediction (safe to expose)."""
    info = bundle.get("training_info", {})
    return {
        "model_type": bundle.get("model_type"),
        "contract_version": bundle.get("contract_version"),
        "contract_version_matches": bundle.get("contract_version") == CONTRACT_VERSION,
        "trained_at": info.get("trained_at"),
        "training_rows": info.get("training_rows"),
        "training_prevalence": info.get("training_prevalence"),
        "features_without_training_data": info.get("features_without_training_data", []),
        "probability_calibrated": False,
        "limitations": info.get("limitations", []),
    }


def score_contract(
    contract: Mapping[str, Mapping[str, Optional[float]]],
    bundle: Mapping[str, Any],
) -> Tuple[Dict[str, Any], pd.DataFrame]:
    """
    Run the model on a feature contract.

    Returns (ml_result, feature_row).  ``feature_row`` is the exact one-row
    matrix given to the model, so the SHAP explanation can be computed on it.
    """
    row = flatten_contract(contract, bundle["feature_names"])
    probability = float(bundle["model"].predict_proba(row)[0, 1])
    threshold = float(bundle["threshold"])
    result = {
        "available": True,
        "fraud_probability": probability,
        "predicted_class": int(probability >= threshold),
        "threshold": threshold,
        "model_info": model_info(bundle),
    }
    return result, row


def unavailable(reason: str) -> Dict[str, Any]:
    return {
        "available": False,
        "fraud_probability": None,
        "predicted_class": None,
        "reason": reason,
    }


def run_ml(
    claim_data: Mapping[str, Any],
    behavior_features: Optional[Mapping[str, Any]] = None,
    anomaly_features: Optional[Mapping[str, Any]] = None,
    network_features: Optional[Mapping[str, Any]] = None,
    document_features: Optional[Mapping[str, Any]] = None,
    model_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Contract -> ML prediction -> SHAP explanation.

    Returns {"contract": ..., "ml": ..., "shap": ...}.  When the model cannot
    be loaded, "ml" reports ``available: False`` and the claim features are
    still returned so the other evidence remains usable.
    """
    bundle = load_model(model_path)
    vocabulary = bundle["vocabulary"] if bundle else {}
    contract = build_contract(
        claim_data, vocabulary,
        behavior_features, anomaly_features, network_features, document_features,
    )
    if bundle is None:
        return {
            "contract": contract,
            "ml": unavailable("Trained model bundle could not be loaded."),
            "shap": {"available": False, "reason": "No model available."},
        }
    try:
        ml, row = score_contract(contract, bundle)
    except Exception as exc:
        return {
            "contract": contract,
            "ml": unavailable(f"Model inference failed: {exc}"),
            "shap": {"available": False, "reason": "No prediction to explain."},
        }
    return {"contract": contract, "ml": ml, "shap": explain_prediction(bundle["model"], row)}


def run_fraud_engine(claim_data: Mapping[str, Any], model_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Backward-compatible ML-only entry point (previous return shape).

    Returns ``fraud_risk_score`` / ``risk_band`` / ``top_risk_factors``.  When
    the model is unavailable the score is None - no placeholder probability is
    invented.  The full pipeline (evidence fusion) is ``risk_engine.assess_claim``.
    """
    outcome = run_ml(claim_data, model_path=model_path)
    ml = outcome["ml"]
    if not ml["available"]:
        return {
            "fraud_risk_score": None,
            "risk_band": "unknown",
            "top_risk_factors": [ml["reason"]],
        }
    probability = ml["fraud_probability"]
    return {
        "fraud_risk_score": probability,
        "risk_band": map_risk_band(probability),
        "top_risk_factors": top_risk_factor_strings(outcome["shap"]),
    }
