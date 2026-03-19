# backend/ml/explainability.py

import shap
import pandas as pd
from typing import List, Dict

_explainer = None


def initialize_explainer(model):
    global _explainer
    if _explainer is None:
        _explainer = shap.TreeExplainer(model)


def explain_prediction(model, features_df: pd.DataFrame) -> List[Dict]:
    """
    Generate top 5 SHAP explanation factors.
    """

    initialize_explainer(model)

    shap_values = _explainer.shap_values(features_df)

    # Binary classification compatibility
    if isinstance(shap_values, list):
        shap_values = shap_values[1]

    feature_names = list(features_df.columns)

    explanation = []

    for i, value in enumerate(shap_values[0]):
        explanation.append({
            "name": feature_names[i],
            "impact": round(float(value), 4),
            "description": f"Feature contribution: {feature_names[i]}",
            "color": determine_color(value)
        })

    # Sort by absolute importance
    explanation.sort(
        key=lambda x: abs(x["impact"]),
        reverse=True
    )

    return explanation[:5]


def determine_color(value: float) -> str:
    """
    Assign visual severity color based on SHAP impact.
    """
    abs_val = abs(value)

    if abs_val > 0.3:
        return "high"
    elif abs_val > 0.1:
        return "medium"
    else:
        return "low"