"""
Risk Engine - orchestration layer.

This file coordinates the fraud pipeline; it contains no fraud calculation of
its own.  Every step lives in its own module:

    1. receive claim
    2. build claim features               fraud_engine.feature_builder
    3. request behavioral features        fraud_engine.behavior_engine.analyze
    4. request anomaly features           fraud_engine.anomaly_engine.analyze
    5. request network features           fraud_engine.graph_engine.analyze
    6. take document features             document evidence supplied by caller
    7. build the ML feature vector        fraud_engine.feature_builder
    8. ML prediction                      fraud_engine.fraud_predictor
    9. SHAP explanation                   fraud_engine.shap_explainer
   10. evidence fusion                    fraud_engine.evidence_fusion
   11. return one structured result

Independent engines
-------------------
behavior_engine, anomaly_engine and graph_engine are developed separately.
Each is expected to expose ``analyze(claim_data: dict) -> dict`` returning a flat
dict of contract feature names (see fraud_engine.feature_builder).  If a module
does not exist yet, or fails, that source is reported as unavailable and the
pipeline continues - a missing engine is never treated as "no risk".  Outputs
can also be injected directly through the ``*_features`` arguments.
"""

import importlib
import math
from typing import Any, Dict, Mapping, Optional, Tuple

from fraud_engine.evidence_fusion import fuse_evidence
from fraud_engine.feature_builder import CONTRACT_VERSION, section_availability
from fraud_engine.fraud_predictor import run_ml
from fraud_engine.shap_explainer import top_risk_factor_strings

ENGINE_MODULES = {
    "behavior": "behavior_engine",
    "anomaly": "anomaly_engine",
    "network": "graph_engine",
}


def _json_safe(value: Any) -> Any:
    """Recursively convert numpy scalars / NaN / unknown objects for JSON."""
    if isinstance(value, Mapping):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]
    if hasattr(value, "item") and not isinstance(value, (str, bytes)):
        try:
            value = value.item()
        except Exception:
            pass
    if isinstance(value, float):
        return None if math.isnan(value) or math.isinf(value) else value
    if value is None or isinstance(value, (bool, int, str)):
        return value
    return str(value)


def request_engine_features(
    source: str, claim_data: Mapping[str, Any]
) -> Tuple[Optional[Mapping[str, Any]], str]:
    """
    Ask an independent engine for its features.

    Returns (features or None, status) where status is one of
    "engine", "not_installed" or "error: <message>".
    """
    module_name = f"fraud_engine.{ENGINE_MODULES[source]}"
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if exc.name == module_name:
            return None, "not_installed"
        return None, f"error: {exc}"
    except Exception as exc:
        return None, f"error: {exc}"

    analyze = getattr(module, "analyze", None)
    if not callable(analyze):
        return None, "error: module has no analyze() function"
    try:
        result = analyze(claim_data)
    except Exception as exc:
        return None, f"error: {exc}"
    if not isinstance(result, Mapping):
        return None, "error: analyze() did not return a dict"
    return result, "engine"


def assess_claim(
    claim_data: Mapping[str, Any],
    behavior_features: Optional[Mapping[str, Any]] = None,
    anomaly_features: Optional[Mapping[str, Any]] = None,
    network_features: Optional[Mapping[str, Any]] = None,
    document_features: Optional[Mapping[str, Any]] = None,
    fusion_config: Optional[Mapping[str, Any]] = None,
    model_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run the full pipeline for one claim.

    Args:
        claim_data:        claim fields (see fraud_engine.feature_builder)
        *_features:        pre-computed engine outputs; when omitted the
                           behavior / anomaly / network engines are asked
        document_features: document evidence (document engine output)
        fusion_config:     overrides for evidence_fusion.DEFAULT_CONFIG

    Returns a dict with (backward compatible keys first):
        risk_score, risk_level, fraud_probability, top_risk_factors, shap,
        final_risk_score, risk_band, recommended_action, component_scores,
        evidence, evidence_summary, evidence_quality, fusion, interpretation,
        feature_contract, engine_status
    """
    raw_outputs: Dict[str, Any] = {}
    engine_status: Dict[str, str] = {}

    provided = {
        "behavior": behavior_features,
        "anomaly": anomaly_features,
        "network": network_features,
    }
    for source, injected in provided.items():
        if injected is not None:
            raw_outputs[source], engine_status[source] = injected, "provided"
        else:
            raw_outputs[source], engine_status[source] = request_engine_features(source, claim_data)
    if document_features is not None:
        raw_outputs["document"], engine_status["document"] = document_features, "provided"
    else:
        raw_outputs["document"], engine_status["document"] = None, "not_provided"

    outcome = run_ml(
        claim_data,
        behavior_features=raw_outputs["behavior"],
        anomaly_features=raw_outputs["anomaly"],
        network_features=raw_outputs["network"],
        document_features=raw_outputs["document"],
        model_path=model_path,
    )
    contract, ml, shap_result = outcome["contract"], outcome["ml"], outcome["shap"]

    fused = fuse_evidence(
        ml,
        behavior_features=contract["behavior_features"],
        anomaly_features=contract["anomaly_features"],
        network_features=contract["network_features"],
        document_features=contract["document_features"],
        config=fusion_config,
    )

    if shap_result.get("available"):
        top_factors = top_risk_factor_strings(shap_result)
    else:
        top_factors = [ml.get("reason") or shap_result.get("reason", "Explanation unavailable")]

    result = {
        # ---- backward-compatible keys ----
        "risk_score": fused["final_risk_score"],
        "risk_level": fused["risk_band"],
        "fraud_probability": fused["fraud_probability"],
        "top_risk_factors": top_factors,
        "shap": shap_result,
        # ---- full structured result ----
        **fused,
        "feature_contract": {
            "version": CONTRACT_VERSION,
            "sections": contract,
            "availability": {
                name: section_availability(values) for name, values in contract.items()
            },
        },
        "engine_status": engine_status,
        "raw_engine_outputs": raw_outputs,
    }
    return _json_safe(result)
