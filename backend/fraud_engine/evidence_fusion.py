"""
Evidence Fusion - combines independent evidence sources into a risk signal.

Fraud detection here is evidence aggregation and risk PRIORITISATION.  The
output ranks claims for review; it is not a statement that a claim is fraud.

Sources (each stays visible in the output, nothing is hidden in one number)
--------------------------------------------------------------------------
ml        model fraud score (fraud_predictor)
behavior  ``behavior_risk_score``           supplied by behavior_engine
anomaly   ``overall_anomaly_score``         supplied by anomaly_engine
network   ``network_risk_score``            supplied by graph_engine
document  mean of the available document risk terms:
              1 - document_consistency_score, duplicate_probability,
              field_mismatch_score, alteration_indicator,
              missing_information_indicator
          ``ocr_confidence`` and ``document_similarity`` are reported as
          evidence but not scored: low OCR confidence means poor scan quality,
          not fraud, and similarity has no fixed risk direction.

A source whose score is not available is excluded and the remaining weights are
re-normalised - a missing engine never counts as "zero risk".

Combination method (configurable)
---------------------------------
"weighted_mean" (default)
    final = sum(w_i * s_i) / sum(w_i) over the available components.
    Default weights are EQUAL.  There is no outcome data with which to fit
    weights for the non-ML sources, so equal weighting is the least
    assumption-laden choice; it is a placeholder for weights that should be set
    by review of real outcomes.  Weights are configuration, not constants.
"max"
    final = the highest available component score.  Conservative; use it when
    a single strong source should not be diluted by the others.

Bands reuse the project's existing cut-offs (risk_band_mapper): <0.3 low,
<0.6 medium, otherwise high - for the final score and for each component.
"""

import copy
from typing import Any, Dict, List, Mapping, Optional

from .risk_band_mapper import LOW_MAX, MEDIUM_MAX

SOURCES = ("ml", "behavior", "anomaly", "network", "document")

DEFAULT_CONFIG: Dict[str, Any] = {
    "method": "weighted_mean",                       # or "max"
    "weights": {s: 1.0 for s in SOURCES},
    "band_thresholds": {"low_max": LOW_MAX, "medium_max": MEDIUM_MAX},
}

# Recommended action per band.  These are review-priority actions, not decisions.
ACTIONS = {
    "LOW": "STANDARD_PROCESSING",
    "MEDIUM": "ENHANCED_VERIFICATION",
    "HIGH": "MANUAL_REVIEW",
    "UNKNOWN": "MANUAL_REVIEW",     # nothing could be assessed -> a human looks
}

_DOCUMENT_RISK_FEATURES = (
    "duplicate_probability",
    "field_mismatch_score",
    "alteration_indicator",
    "missing_information_indicator",
)


def _validated_config(config: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    merged = copy.deepcopy(DEFAULT_CONFIG)
    if config:
        for key in ("method",):
            if key in config:
                merged[key] = config[key]
        merged["weights"].update(config.get("weights", {}))
        merged["band_thresholds"].update(config.get("band_thresholds", {}))
    if merged["method"] not in ("weighted_mean", "max"):
        raise ValueError(f"Unknown fusion method: {merged['method']!r}")
    for source, weight in merged["weights"].items():
        if source not in SOURCES:
            raise ValueError(f"Unknown evidence source in weights: {source!r}")
        if weight < 0:
            raise ValueError(f"Weight for {source!r} must be >= 0")
    thresholds = merged["band_thresholds"]
    if not 0.0 <= thresholds["low_max"] < thresholds["medium_max"] <= 1.0:
        raise ValueError("band_thresholds must satisfy 0 <= low_max < medium_max <= 1")
    return merged


def _band(score: float, thresholds: Mapping[str, float]) -> str:
    if score < thresholds["low_max"]:
        return "LOW"
    if score < thresholds["medium_max"]:
        return "MEDIUM"
    return "HIGH"


def _clip01(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    return max(0.0, min(1.0, float(value)))


def _document_score(features: Mapping[str, Optional[float]]) -> Optional[float]:
    terms: List[float] = [
        features[name] for name in _DOCUMENT_RISK_FEATURES if features.get(name) is not None
    ]
    consistency = features.get("document_consistency_score")
    if consistency is not None:
        terms.append(1.0 - _clip01(consistency))
    terms = [_clip01(t) for t in terms]
    return sum(terms) / len(terms) if terms else None


def _history_limited(features: Mapping[str, Optional[float]]) -> Optional[bool]:
    flags = [v for k, v in features.items() if k.endswith("_history_available") and v is not None]
    return None if not flags else any(v == 0.0 for v in flags)


def fuse_evidence(
    ml: Mapping[str, Any],
    behavior_features: Optional[Mapping[str, Optional[float]]] = None,
    anomaly_features: Optional[Mapping[str, Optional[float]]] = None,
    network_features: Optional[Mapping[str, Optional[float]]] = None,
    document_features: Optional[Mapping[str, Optional[float]]] = None,
    config: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Fuse the evidence sources.

    Args:
        ml:                 result of fraud_predictor (``available``,
                            ``fraud_probability`` ...)
        *_features:         contract sections (feature -> float or None), as
                            produced by feature_builder.normalize_section
        config:             optional overrides of DEFAULT_CONFIG

    Returns the structure described in the module docstring: fraud_probability,
    final_risk_score (0-100), risk_band, recommended_action, component_scores,
    evidence per source, evidence_summary and fusion metadata.
    """
    cfg = _validated_config(config)
    thresholds = cfg["band_thresholds"]

    behavior_features = behavior_features or {}
    anomaly_features = anomaly_features or {}
    network_features = network_features or {}
    document_features = document_features or {}

    ml_score = _clip01(ml.get("fraud_probability")) if ml.get("available") else None
    scores: Dict[str, Optional[float]] = {
        "ml": ml_score,
        "behavior": _clip01(behavior_features.get("behavior_risk_score")),
        "anomaly": _clip01(anomaly_features.get("overall_anomaly_score")),
        "network": _clip01(network_features.get("network_risk_score")),
        "document": _document_score(document_features),
    }

    used = [s for s in SOURCES if scores[s] is not None and cfg["weights"].get(s, 0.0) > 0]
    weights_used: Dict[str, float] = {}
    final: Optional[float] = None
    if used:
        total = sum(cfg["weights"][s] for s in used)
        weights_used = {s: cfg["weights"][s] / total for s in used}
        if cfg["method"] == "max":
            final = max(scores[s] for s in used)
        else:
            final = sum(weights_used[s] * scores[s] for s in used)

    if final is None:
        band, score_100 = "UNKNOWN", None
    else:
        band, score_100 = _band(final, thresholds), int(round(final * 100))

    # ---- per-source evidence: keeps every layer visible -------------------
    evidence: Dict[str, Any] = {
        "ml": {
            "available": bool(ml.get("available")),
            "score": ml_score,
            "predicted_class": ml.get("predicted_class"),
            "threshold": ml.get("threshold"),
            "model_info": ml.get("model_info"),
            "reason": ml.get("reason"),
        },
        "behavior": {
            "available": scores["behavior"] is not None,
            "score": scores["behavior"],
            "history_limited": _history_limited(behavior_features),
            "features": dict(behavior_features),
        },
        "anomaly": {
            "available": scores["anomaly"] is not None,
            "score": scores["anomaly"],
            "features": dict(anomaly_features),
        },
        "network": {
            "available": scores["network"] is not None,
            "score": scores["network"],
            "features": dict(network_features),
        },
        "document": {
            "available": scores["document"] is not None,
            "score": scores["document"],
            "ocr_confidence": document_features.get("ocr_confidence"),
            "features": dict(document_features),
        },
    }
    for source in SOURCES:
        s = scores[source]
        evidence[source]["level"] = None if s is None else _band(s, thresholds)
        evidence[source]["used_in_final_score"] = source in used
        evidence[source]["weight"] = weights_used.get(source)

    # ---- structured summary (deterministic, machine readable) -------------
    summary = [
        {"source": s, "available": scores[s] is not None, "score": scores[s],
         "level": evidence[s]["level"], "used_in_final_score": s in used}
        for s in SOURCES
    ]
    elevated = [s for s in used if evidence[s]["level"] in ("MEDIUM", "HIGH")]
    missing = [s for s in SOURCES if scores[s] is None]

    return {
        "fraud_probability": ml_score,
        "final_risk_score": score_100,
        "risk_band": band,
        "recommended_action": ACTIONS[band],
        "component_scores": scores,
        "evidence": evidence,
        "evidence_summary": summary,
        "evidence_quality": {
            "sources_used": used,
            "sources_missing": missing,
            "elevated_sources": elevated,
            "limited": len(used) < 2,
        },
        "fusion": {
            "method": cfg["method"],
            "weights_configured": cfg["weights"],
            "weights_used": weights_used,
            "band_thresholds": thresholds,
        },
        "interpretation": (
            "Risk prioritisation signal for review; not a determination that "
            "the claim is fraudulent."
        ),
    }
