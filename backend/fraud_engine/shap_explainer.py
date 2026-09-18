"""
SHAP Explainer - feature-level explanation of the ML fraud prediction.

The explanation is computed on the SAME one-row feature vector that produced
the prediction, with the SAME fitted model, so it always corresponds to the
actual prediction.  Nothing here is rule based and no text is generated that
claims the model used information it did not use.

SHAP values are expressed in the model's output space (XGBoost log-odds):
    base_value + sum(shap_value) = raw model margin
A positive SHAP value pushes the fraud score up, a negative one pushes it down.
"""

import math
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import shap

# id(model) -> (model, explainer).  Keeping the model reference prevents id reuse.
_EXPLAINERS: Dict[int, Any] = {}


def _get_explainer(model: Any) -> Any:
    cached = _EXPLAINERS.get(id(model))
    if cached is not None and cached[0] is model:
        return cached[1]
    explainer = shap.TreeExplainer(model)
    _EXPLAINERS[id(model)] = (model, explainer)
    return explainer


def _clean(value: float) -> Optional[float]:
    value = float(value)
    return None if math.isnan(value) or math.isinf(value) else value


def explain_prediction(model: Any, feature_row: pd.DataFrame, top_n: int = 10) -> Dict[str, Any]:
    """
    Explain one prediction.

    Args:
        model:       the fitted tree model that produced the prediction
        feature_row: one-row DataFrame in the model's exact feature order
        top_n:       number of features (by absolute contribution) to return

    Returns:
        {
          "available": True,
          "method": "shap.TreeExplainer",
          "output_space": "log_odds",
          "base_value": float,
          "raw_margin": float,
          "features": [
             {"feature", "value", "shap_value", "direction"}, ...   # sorted by |shap|
          ],
        }
        or {"available": False, "reason": str} if SHAP cannot be computed.
    """
    try:
        explainer = _get_explainer(model)
        values = np.asarray(explainer.shap_values(feature_row))
        if values.ndim == 3:            # (rows, features, classes) -> positive class
            values = values[:, :, -1]
        contributions = values[0]

        base_value = float(np.ravel(explainer.expected_value)[-1])
        names = list(feature_row.columns)
        row_values = feature_row.iloc[0].to_numpy(dtype=float)

        entries: List[Dict[str, Any]] = []
        for name, value, shap_value in zip(names, row_values, contributions):
            if shap_value == 0.0:
                continue                # feature had no influence on this prediction
            entries.append({
                "feature": name,
                "value": _clean(value),
                "shap_value": round(float(shap_value), 6),
                "direction": "increases_risk" if shap_value > 0 else "decreases_risk",
            })
        entries.sort(key=lambda e: abs(e["shap_value"]), reverse=True)

        return {
            "available": True,
            "method": "shap.TreeExplainer",
            "output_space": "log_odds",
            "base_value": round(base_value, 6),
            "raw_margin": round(base_value + float(np.sum(contributions)), 6),
            "features": entries[:top_n],
        }
    except Exception as exc:
        return {"available": False, "reason": f"SHAP explanation failed: {exc}"}


def top_risk_factor_strings(explanation: Dict[str, Any], n_factors: int = 3) -> List[str]:
    """
    Backward-compatible ``top_risk_factors`` strings, generated from the real
    SHAP contributions (never from rules).
    """
    if not explanation.get("available"):
        return []
    factors = []
    for entry in explanation["features"][:n_factors]:
        label = entry["feature"].replace("_", " ").title()
        value = entry["value"]
        shown = "value not available" if value is None else f"= {value:g}"
        verb = "increases" if entry["direction"] == "increases_risk" else "decreases"
        factors.append(f"{label} ({shown}) {verb} fraud score")
    return factors
