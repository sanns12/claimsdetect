import shap
import pandas as pd

_explainer = None


def initialize_explainer(model):
    global _explainer
    _explainer = shap.TreeExplainer(model)


def explain_prediction(model, features_df: pd.DataFrame):
    global _explainer

    if _explainer is None:
        initialize_explainer(model)

    shap_values = _explainer.shap_values(features_df)

    # For binary classification, shap_values is a list
    if isinstance(shap_values, list):
        shap_values = shap_values[1]

    feature_names = features_df.columns

    explanation = []

    for i, value in enumerate(shap_values[0]):
        explanation.append({
            "feature": feature_names[i],
            "impact": round(float(value), 4)
        })

    # Sort by absolute importance
    explanation = sorted(
        explanation,
        key=lambda x: abs(x["impact"]),
        reverse=True
    )

    return explanation[:5]