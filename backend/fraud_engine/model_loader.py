"""
Model Loader - persistence of the trained fraud model.

The model is stored as ONE self-describing "bundle" so that inference can never
drift from training:

    {
        "model":            fitted XGBClassifier,
        "model_type":       "xgboost",
        "contract_version": feature-contract version used for training,
        "feature_names":    exact ordered list of model input columns,
        "vocabulary":       category counts used for frequency encoding,
        "threshold":        probability cut-off used for predicted_class,
        "training_info":    provenance, validation metrics and limitations,
    }

Training itself lives in backend/train_model.py.
"""

import os
from typing import Any, Dict, Optional

import joblib

DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "models", "fraud_model.pkl"
)

_REQUIRED_KEYS = ("model", "feature_names", "vocabulary", "threshold")

# path -> (mtime, bundle).  Avoids re-reading the pickle on every request but
# still picks up a re-trained file.
_CACHE: Dict[str, Any] = {}


def save_model(bundle: Dict[str, Any], path: str = DEFAULT_MODEL_PATH) -> None:
    """Persist a model bundle."""
    missing = [k for k in _REQUIRED_KEYS if k not in bundle]
    if missing:
        raise ValueError(f"Model bundle is missing keys: {missing}")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    joblib.dump(bundle, path)
    _CACHE.pop(os.path.abspath(path), None)
    print(f"[model_loader] model bundle saved to {path}")


def load_model(path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Load the model bundle.

    Returns None (never raises) when the file is missing or invalid, so the
    caller can report "model unavailable" instead of crashing.
    """
    path = os.path.abspath(path or DEFAULT_MODEL_PATH)
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        print(f"[model_loader] model file not found: {path}")
        return None

    cached = _CACHE.get(path)
    if cached and cached[0] == mtime:
        return cached[1]

    try:
        bundle = joblib.load(path)
    except Exception as exc:  # corrupt file, version mismatch, ...
        print(f"[model_loader] could not load model from {path}: {exc}")
        return None

    if not isinstance(bundle, dict) or any(k not in bundle for k in _REQUIRED_KEYS):
        print(f"[model_loader] {path} is not a valid model bundle")
        return None

    _CACHE[path] = (mtime, bundle)
    return bundle
