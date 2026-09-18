"""
Train the fraud model on backend/data/unified_claims_v1.csv.

Run from the backend directory:

    python train_model.py

What this script does
---------------------
1. Loads the historical claims and prints a label audit per data segment.
2. Selects the rows the model is trained on (see TRAINING SCOPE below).
3. Builds the canonical feature matrix through fraud_engine.feature_builder,
   i.e. exactly the code path used at inference time.
4. Validates with duplicate-aware cross-validation and compares
   Logistic Regression, Random Forest and XGBoost.
5. Fits the final XGBoost model and writes ONE model bundle
   (models/fraud_model.pkl) containing the model, feature order, vocabulary,
   threshold and the full training/validation record.

TRAINING SCOPE - why the model is not trained on every row
----------------------------------------------------------
The CSV is a concatenation of differently-sourced files:

  * Rows without an age (~95 %) carry almost no positive labels (0.06 %).
  * Rows with an age AND a spelled-out gender ("Male"/"Female") carry ZERO
    positive labels.  A source with no positives says nothing about fraud.
  * Rows with an age AND a single-letter gender ("M"/"F") are the only rows
    with a meaningful number of positives.

Across the full file, "is age missing?" alone predicts the label with a
ROC-AUC of about 0.95 - a data-source artefact, not fraud behaviour.  A model
trained on the full file therefore looks excellent and learns nothing useful.
The model is trained on the label-bearing segment only.  This is a data-driven
heuristic and is recorded in the bundle; it should be replaced by proper
source/label provenance when that becomes available.

Known limits (also stored in the bundle)
----------------------------------------
* Labels are noisy: many identical claims appear with conflicting labels.
* The training prevalence (~35 %) is NOT the real-world fraud rate, so the
  output is a model score, not a calibrated probability of fraud.
* The dataset contains no behavioral, anomaly, network or document evidence;
  those contract features are NaN in training and therefore unused by the
  model until historical evidence is available for retraining.
"""

import os
import sys
import time
from typing import Dict, List

import numpy as np
import pandas as pd
import sklearn
import xgboost
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from fraud_engine.feature_builder import (  # noqa: E402
    CONTRACT_VERSION,
    FEATURE_ORDER,
    build_feature_matrix,
    fit_vocabulary,
    parse_dates,
)
from fraud_engine.model_loader import DEFAULT_MODEL_PATH, save_model  # noqa: E402

DATA_PATH = os.path.join(HERE, "data", "unified_claims_v1.csv")
LABEL = "is_fraud"
RANDOM_STATE = 42
THRESHOLD = 0.5          # standard decision boundary for predicted_class
N_SPLITS = 5

XGB_PARAMS = dict(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=5,
    eval_metric="logloss",
    random_state=RANDOM_STATE,
    n_jobs=4,
)

# Columns that identify "the same claim" for duplicate-aware validation.
DEDUP_COLUMNS = [
    "patient_age", "gender", "diagnosis_code",
    "claimed_amount", "admission_date", "discharge_date",
]


# ---------------------------------------------------------------------------
# Data selection
# ---------------------------------------------------------------------------

def label_audit(df: pd.DataFrame) -> None:
    """Print positives per segment so the scope decision is reproducible."""
    gender_raw = df["gender"].astype("string").str.strip()
    single_letter = gender_raw.str.upper().isin(["M", "F"])
    spelled_out = gender_raw.str.upper().isin(["MALE", "FEMALE"])
    has_age = df["patient_age"].notna()
    segments = {
        "no age": ~has_age,
        "age + spelled-out gender": has_age & spelled_out,
        "age + single-letter gender": has_age & single_letter,
        "age + other/missing gender": has_age & ~single_letter & ~spelled_out,
    }
    print("\nLabel audit by data segment")
    print(f"  {'segment':32s} {'rows':>9s} {'fraud':>7s} {'rate':>7s}")
    for name, mask in segments.items():
        n, pos = int(mask.sum()), int(df.loc[mask, LABEL].sum())
        rate = pos / n if n else float("nan")
        print(f"  {name:32s} {n:9d} {pos:7d} {rate:7.3f}")


def select_training_scope(df: pd.DataFrame) -> pd.DataFrame:
    """Rows with an age and a single-letter gender (the label-bearing segment)."""
    gender = df["gender"].astype("string").str.strip().str.upper()
    return df[df["patient_age"].notna() & gender.isin(["M", "F"])].reset_index(drop=True)


def duplicate_groups(df: pd.DataFrame) -> np.ndarray:
    """Identical claims share a group so they never span train and test."""
    key = df[DEDUP_COLUMNS].astype(str).agg("|".join, axis=1)
    return pd.factorize(key)[0]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _candidates() -> Dict[str, object]:
    return {
        "logistic_regression": make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(max_iter=1000, class_weight="balanced"),
        ),
        "random_forest": make_pipeline(
            SimpleImputer(strategy="median"),
            RandomForestClassifier(
                n_estimators=200, min_samples_leaf=5, n_jobs=-1,
                random_state=RANDOM_STATE,
            ),
        ),
        "xgboost": XGBClassifier(**XGB_PARAMS),
    }


def _scores(y: np.ndarray, p: np.ndarray) -> Dict[str, float]:
    pred = (p >= THRESHOLD).astype(int)
    return {
        "roc_auc": float(roc_auc_score(y, p)),
        "pr_auc": float(average_precision_score(y, p)),
        "brier": float(brier_score_loss(y, p)),
        "precision@0.5": float(precision_score(y, pred, zero_division=0)),
        "recall@0.5": float(recall_score(y, pred, zero_division=0)),
    }


def cross_validate(X: pd.DataFrame, y: np.ndarray, groups: np.ndarray):
    """
    Grouped K-fold out-of-fold scores for every candidate model.

    Returns (metrics per model, out-of-fold probabilities per model).
    """
    results: Dict[str, Dict[str, float]] = {}
    oof_by_model: Dict[str, np.ndarray] = {}
    cv = GroupKFold(n_splits=N_SPLITS)
    for name, model in _candidates().items():
        oof = np.zeros(len(y))
        for train_idx, test_idx in cv.split(X, y, groups):
            model.fit(X.iloc[train_idx], y[train_idx])
            oof[test_idx] = model.predict_proba(X.iloc[test_idx])[:, 1]
        results[name] = _scores(y, oof)
        oof_by_model[name] = oof
    return results, oof_by_model


def date_segment(df: pd.DataFrame) -> pd.Series:
    """
    Split rows by how admission_date is written.  The three groups behave very
    differently (see segment_report) and must be validated separately.
    """
    text = df["admission_date"].astype("string")
    parsed = parse_dates(df["admission_date"])
    segment = pd.Series("date_only", index=df.index)
    segment[text.str.contains(":", regex=False).fillna(False)] = "timestamp"
    segment[parsed.isna()] = "missing_date"
    return segment


def segment_report(segment: pd.Series, y: np.ndarray, oof: np.ndarray) -> Dict[str, Dict[str, float]]:
    """Out-of-fold ROC-AUC / PR-AUC of the model inside every date segment."""
    report: Dict[str, Dict[str, float]] = {}
    for name in sorted(segment.unique()):
        mask = (segment == name).to_numpy()
        entry = {"rows": int(mask.sum()), "prevalence": float(y[mask].mean())}
        if len(np.unique(y[mask])) == 2:
            entry["roc_auc"] = float(roc_auc_score(y[mask], oof[mask]))
            entry["pr_auc"] = float(average_precision_score(y[mask], oof[mask]))
        report[name] = entry
    return report


def holdout_evaluation(X: pd.DataFrame, y: np.ndarray, groups: np.ndarray) -> Dict[str, object]:
    """20 % group-aware hold-out for the final model configuration."""
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=RANDOM_STATE)
    train_idx, test_idx = next(splitter.split(X, y, groups))
    model = XGBClassifier(**XGB_PARAMS).fit(X.iloc[train_idx], y[train_idx])
    p = model.predict_proba(X.iloc[test_idx])[:, 1]
    out = _scores(y[test_idx], p)
    out["confusion_matrix@0.5"] = confusion_matrix(y[test_idx], (p >= THRESHOLD).astype(int)).tolist()
    out["test_rows"] = int(len(test_idx))
    out["test_prevalence"] = float(y[test_idx].mean())
    return out


def source_artifact_baseline(df: pd.DataFrame) -> float:
    """
    ROC-AUC obtained on the FULL file from missingness flags alone.  Shown to
    document why the full file must not be used for training.
    """
    flags = pd.DataFrame({
        "age_missing": df["patient_age"].isna().astype(float),
        "gender_missing": df["gender"].isna().astype(float),
    })
    y = df[LABEL].to_numpy()
    model = XGBClassifier(n_estimators=50, max_depth=2, random_state=RANDOM_STATE, n_jobs=4)
    idx = np.random.RandomState(RANDOM_STATE).permutation(len(df))[:200_000]
    half = len(idx) // 2
    model.fit(flags.iloc[idx[:half]], y[idx[:half]])
    return float(roc_auc_score(y[idx[half:]], model.predict_proba(flags.iloc[idx[half:]])[:, 1]))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Loading dataset ...")
    df = pd.read_csv(DATA_PATH, low_memory=False)
    print(f"  {len(df):,} rows, overall fraud rate {df[LABEL].mean():.4f}")

    label_audit(df)
    artefact_auc = source_artifact_baseline(df)
    print(f"\nROC-AUC of 'is age/gender missing?' alone on the full file: {artefact_auc:.3f}"
          "  (source artefact - reason for restricting the training scope)")

    scope = select_training_scope(df)
    y = scope[LABEL].to_numpy().astype(int)
    print(f"\nTraining scope: {len(scope):,} rows, {int(y.sum()):,} positive "
          f"(prevalence {y.mean():.3f})")

    vocabulary = fit_vocabulary(scope)
    X = build_feature_matrix(scope, vocabulary, exclude_self=True)
    assert list(X.columns) == list(FEATURE_ORDER)
    groups = duplicate_groups(scope)
    n_groups = len(set(groups))
    print(f"Unique claims (duplicate groups): {n_groups:,} of {len(scope):,} rows")

    coverage = X.notna().mean().round(4).to_dict()
    unused: List[str] = [c for c, v in coverage.items() if v == 0.0]
    print(f"Features with training data: {len(FEATURE_ORDER) - len(unused)} of {len(FEATURE_ORDER)}")

    # Features that are entirely NaN in the training data carry no information;
    # they are left out of the model comparison (LR/RF cannot impute them).
    usable = [c for c in FEATURE_ORDER if c not in unused]

    print("\nGrouped cross-validation (duplicates never split across folds)")
    cv_results, oof = cross_validate(X[usable], y, groups)
    print(f"  {'model':22s} {'ROC-AUC':>8s} {'PR-AUC':>8s} {'Brier':>7s} {'Prec@.5':>8s} {'Rec@.5':>7s}")
    for name, m in cv_results.items():
        print(f"  {name:22s} {m['roc_auc']:8.3f} {m['pr_auc']:8.3f} {m['brier']:7.3f} "
              f"{m['precision@0.5']:8.3f} {m['recall@0.5']:7.3f}")
    print(f"  (no-skill PR-AUC = prevalence = {y.mean():.3f})")

    segments = segment_report(date_segment(scope), y, oof["xgboost"])
    print("\nXGBoost out-of-fold performance per admission-date segment")
    print(f"  {'segment':14s} {'rows':>7s} {'prevalence':>11s} {'ROC-AUC':>8s} {'PR-AUC':>8s}")
    for name, m in segments.items():
        print(f"  {name:14s} {m['rows']:7d} {m['prevalence']:11.3f} "
              f"{m.get('roc_auc', float('nan')):8.3f} {m.get('pr_auc', float('nan')):8.3f}")
    print("  The overall score is dominated by the 'timestamp' segment, whose dates look")
    print("  synthetic (discharge often years before/after admission).  'date_only' is the")
    print("  segment closest to real claims.")

    print("\nGroup-aware 20% hold-out (XGBoost)")
    holdout = holdout_evaluation(X[usable], y, groups)
    for k, v in holdout.items():
        print(f"  {k}: {v}")

    print("\nFitting final model on the full training scope ...")
    model = XGBClassifier(**XGB_PARAMS).fit(X, y)

    bundle = {
        "model": model,
        "model_type": "xgboost",
        "contract_version": CONTRACT_VERSION,
        "feature_names": list(FEATURE_ORDER),
        "vocabulary": vocabulary,
        "threshold": THRESHOLD,
        "training_info": {
            "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source_file": os.path.basename(DATA_PATH),
            "rows_in_file": int(len(df)),
            "training_rows": int(len(scope)),
            "unique_claims": int(n_groups),
            "positives": int(y.sum()),
            "training_prevalence": float(y.mean()),
            "scope_rule": ("patient_age present AND single-letter gender (M/F); "
                           "see train_model.py docstring"),
            "full_file_missingness_only_roc_auc": artefact_auc,
            "xgboost_params": XGB_PARAMS,
            "cross_validation": cv_results,
            "xgboost_cv_by_date_segment": segments,
            "holdout": holdout,
            "feature_coverage": coverage,
            "features_without_training_data": unused,
            "library_versions": {
                "xgboost": xgboost.__version__,
                "scikit-learn": sklearn.__version__,
                "pandas": pd.__version__,
                "numpy": np.__version__,
            },
            "limitations": [
                "Labels are noisy: identical claims appear with conflicting labels.",
                "Training prevalence is not the real-world fraud rate; the output is "
                "a model score, not a calibrated probability of fraud.",
                "No behavioral, anomaly, network or document evidence exists in the "
                "training data; those features are unused by the model.",
                "Training scope was chosen with a data-driven heuristic, not source "
                "provenance.",
                "Overall validation scores are dominated by a 'timestamp' segment with "
                "synthetic-looking dates; see xgboost_cv_by_date_segment for the "
                "per-segment scores.",
            ],
        },
    }
    save_model(bundle, DEFAULT_MODEL_PATH)
    print("Done.")


if __name__ == "__main__":
    main()
