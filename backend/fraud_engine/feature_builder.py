"""
Feature Builder - the canonical feature contract for the fraud pipeline.

This module is the single place that defines:

  * WHICH features exist (five sections, fixed order),
  * HOW claim-level features are derived from raw claim fields,
  * HOW outputs of the independent evidence engines are normalised into
    the contract (behavior / anomaly / network / document),
  * HOW the contract is flattened into the deterministic ML feature vector.

Design rules
------------
* Claim features are computed here.  Behavioral, anomaly, network and document
  features are NOT computed here - they are supplied by their own engines
  (behavior_engine, anomaly_engine, graph_engine, document_engine) and are only
  validated / normalised / ordered by this module.
* Missing information is NaN inside the numeric vector (XGBoost handles NaN
  natively, so no value is invented) and None inside the JSON-safe contract.
* Nothing here scales numbers: the model is tree based, so scaling is not
  required.  Categorical text is frequency-encoded from a vocabulary learned at
  training time; unseen categories map to 0 and missing categories to NaN.
* No identifiers (hospital, doctor, patient, insurer) are model features.
  Identifiers are only needed by the behavior/graph engines to look up
  relationships; they never enter the ML vector.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

import numpy as np
import pandas as pd

CONTRACT_VERSION = "1.0"

# ---------------------------------------------------------------------------
# Section definitions (order matters - it defines the ML feature order)
# ---------------------------------------------------------------------------

CLAIM_FEATURES: Tuple[str, ...] = (
    "claim_amount",
    "claimed_per_day",
    "amount_per_item",
    "patient_age",
    "gender_male",
    "diagnosis_frequency",
    "procedure_frequency",
    "is_inpatient",
    "length_of_stay",
    "discharge_before_admission",
    "is_emergency_admission",
    "billed_items_count",
    "num_procedures",
    "num_tests",
    "num_medications",
    "preauthorization_obtained",
    "previous_claims_count",
    "previous_rejection",
    "doc_missing_flag",
    "admission_month",
    "admission_dayofweek",
)

# Supplied by behavior_engine.  Names follow the patient_/provider_/doctor_
# convention of the behavior engine specification.  Keys the engine does not
# return stay None/NaN.
BEHAVIOR_FEATURES: Tuple[str, ...] = (
    "patient_claim_frequency",
    "patient_avg_claim_amount",
    "patient_hospitalization_frequency",
    "patient_distinct_hospitals",
    "patient_procedure_frequency",
    "patient_avg_days_between_claims",
    "patient_high_value_claim_rate",
    "patient_history_available",
    "provider_claim_frequency",
    "provider_avg_claim_amount",
    "provider_avg_length_of_stay",
    "provider_surgery_rate",
    "provider_rejection_rate",
    "provider_high_value_claim_pct",
    "provider_monthly_claim_growth",
    "provider_baseline_deviation",
    "provider_history_available",
    "doctor_claim_frequency",
    "doctor_avg_claim_amount",
    "doctor_procedure_frequency",
    "doctor_referral_frequency",
    "doctor_rejection_rate",
    "doctor_high_cost_rate",
    "doctor_history_available",
    # Optional summary score (0-1, higher = more unusual history).  Evidence
    # fusion can only use behavior as a component when the engine supplies it.
    "behavior_risk_score",
)

# Supplied by anomaly_engine.
ANOMALY_FEATURES: Tuple[str, ...] = (
    "amount_anomaly_score",
    "frequency_anomaly_score",
    "procedure_anomaly_score",
    "los_anomaly_score",
    "temporal_anomaly_score",
    "provider_deviation_score",
    "overall_anomaly_score",
)

# Supplied by graph_engine.
NETWORK_FEATURES: Tuple[str, ...] = (
    "patient_hospital_claim_count",
    "doctor_hospital_relationship_count",
    "shared_patient_count",
    "provider_network_density",
    "network_risk_score",
)

# Supplied by document_engine.
DOCUMENT_FEATURES: Tuple[str, ...] = (
    "ocr_confidence",
    "document_similarity",
    "duplicate_probability",
    "field_mismatch_score",
    "alteration_indicator",
    "missing_information_indicator",
    # Output of the existing document engine (1 = consistent, 0 = inconsistent).
    "document_consistency_score",
)

SECTION_FEATURES: Dict[str, Tuple[str, ...]] = {
    "claim_features": CLAIM_FEATURES,
    "behavior_features": BEHAVIOR_FEATURES,
    "anomaly_features": ANOMALY_FEATURES,
    "network_features": NETWORK_FEATURES,
    "document_features": DOCUMENT_FEATURES,
}

FEATURE_ORDER: Tuple[str, ...] = tuple(
    name for section in SECTION_FEATURES.values() for name in section
)

if len(set(FEATURE_ORDER)) != len(FEATURE_ORDER):  # pragma: no cover - guard
    raise RuntimeError("Feature names must be unique across contract sections")

# Categorical claim fields that are frequency-encoded.
CATEGORICAL_FIELDS: Tuple[str, ...] = ("diagnosis_code", "procedure_code")

# Accepted spellings of raw claim inputs (the first one is canonical).
_INPUT_ALIASES: Dict[str, Tuple[str, ...]] = {
    "claim_amount": ("claim_amount", "claimed_amount"),
    "patient_age": ("patient_age", "age"),
    "gender": ("gender",),
    "diagnosis_code": ("diagnosis_code",),
    "procedure_code": ("procedure_code",),
    "admission_date": ("admission_date",),
    "discharge_date": ("discharge_date",),
    "is_inpatient": ("is_inpatient",),
    "is_emergency_admission": ("is_emergency_admission",),
    "billed_items_count": ("billed_items_count",),
    "num_procedures": ("num_procedures",),
    "num_tests": ("num_tests",),
    "num_medications": ("num_medications",),
    "preauthorization_obtained": ("preauthorization_obtained",),
    "previous_claims_count": ("previous_claims_count",),
    "previous_rejection": ("previous_rejection",),
    "doc_missing_flag": ("doc_missing_flag",),
}

_TRUE_TOKENS = {"1", "true", "t", "yes", "y", "inpatient", "emergency"}
_FALSE_TOKENS = {"0", "false", "f", "no", "n", "outpatient", "planned", "elective"}
_MISSING_TOKENS = {"", "nan", "none", "null", "nat", "n/a", "na"}


# ---------------------------------------------------------------------------
# Low level parsers (vectorised, tolerant, never raise on bad data)
# ---------------------------------------------------------------------------

def _clean_str(series: pd.Series) -> pd.Series:
    """Strip text; turn missing tokens into NaN."""
    s = series.astype("string").str.strip()
    return s.mask(s.str.lower().isin(_MISSING_TOKENS))


def parse_amount(series: pd.Series) -> pd.Series:
    """'1,234.50', ' 9,999.99 ' -> float.  Negative or unparsable -> NaN."""
    s = _clean_str(series).str.replace(r"[,\"\s]", "", regex=True)
    out = pd.to_numeric(s, errors="coerce").astype(float)
    return out.mask(out < 0)


def parse_number(series: pd.Series, low: float = 0.0,
                 high: float = float("inf")) -> pd.Series:
    """Numeric parse; values outside [low, high] -> NaN."""
    out = pd.to_numeric(_clean_str(series), errors="coerce").astype(float)
    return out.mask((out < low) | (out > high))


def parse_flag(series: pd.Series) -> pd.Series:
    """True/False-like values -> 1.0 / 0.0.  Anything else -> NaN."""
    s = _clean_str(series).str.lower()
    out = pd.Series(np.nan, index=series.index, dtype=float)
    out[s.isin(_TRUE_TOKENS)] = 1.0
    out[s.isin(_FALSE_TOKENS)] = 0.0
    return out


def parse_dates(series: pd.Series) -> pd.Series:
    """
    ISO dates ('2025-02-11', '2025-02-11 00:00:00') are parsed as ISO.
    Slash dates are parsed day-first, matching the existing project convention
    (dd/mm/yyyy) used by the previous feature builder.  Anything else -> NaT.
    """
    s = _clean_str(series)
    out = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")
    slash = s.str.contains("/", regex=False).fillna(False)
    iso_part = s[~slash].dropna()
    if len(iso_part):
        out.loc[iso_part.index] = pd.to_datetime(
            iso_part.astype(object), errors="coerce", format="ISO8601"
        )
    slash_part = s[slash].dropna()
    if len(slash_part):
        out.loc[slash_part.index] = pd.to_datetime(
            slash_part.astype(object), errors="coerce", dayfirst=True, format="mixed"
        )
    return out


def normalise_category(series: pd.Series) -> pd.Series:
    """Upper-case, single-spaced text; missing tokens -> NaN."""
    s = _clean_str(series).str.upper().str.replace(r"\s+", " ", regex=True)
    return s


def encode_gender(series: pd.Series) -> pd.Series:
    """M/MALE -> 1.0, F/FEMALE -> 0.0.  Every other value (incl. '1', '2',
    'MF') is treated as unknown -> NaN; no code is guessed."""
    s = _clean_str(series).str.upper()
    out = pd.Series(np.nan, index=series.index, dtype=float)
    out[s.isin(["M", "MALE"])] = 1.0
    out[s.isin(["F", "FEMALE"])] = 0.0
    return out


# ---------------------------------------------------------------------------
# Vocabulary (learned at training time, stored in the model bundle)
# ---------------------------------------------------------------------------

def fit_vocabulary(df: pd.DataFrame) -> Dict[str, Dict[str, int]]:
    """Count normalised category values for every categorical claim field."""
    frame = _canonical_inputs(df)
    vocab: Dict[str, Dict[str, int]] = {}
    for field in CATEGORICAL_FIELDS:
        counts = normalise_category(frame[field]).dropna().value_counts()
        vocab[field] = {str(k): int(v) for k, v in counts.items()}
    return vocab


def _frequency_encode(values: pd.Series, counts: Mapping[str, int],
                      exclude_self: bool) -> pd.Series:
    """
    log(1 + training count).  Missing value -> NaN.  Unseen value -> 0.
    If no vocabulary exists for the field (no training data for it) -> NaN.
    With exclude_self=True the row's own occurrence is removed so training
    rows and unseen inference rows share the same scale (unseen == 0).
    """
    out = pd.Series(np.nan, index=values.index, dtype=float)
    if not counts:
        return out
    known = values.notna()
    mapped = values[known].map(lambda v: counts.get(v, 0)).astype(float)
    if exclude_self:
        mapped = (mapped - 1).clip(lower=0)
    out[known] = np.log1p(mapped)
    return out


# ---------------------------------------------------------------------------
# Claim features
# ---------------------------------------------------------------------------

def _canonical_inputs(df: pd.DataFrame) -> pd.DataFrame:
    """Return a frame that has every canonical raw input column (NaN if absent)."""
    out = pd.DataFrame(index=df.index)
    for canonical, aliases in _INPUT_ALIASES.items():
        source = next((a for a in aliases if a in df.columns), None)
        out[canonical] = df[source] if source is not None else np.nan
    for field in CATEGORICAL_FIELDS:
        if field not in out.columns:
            out[field] = np.nan
    return out


def build_claim_features(
    df: pd.DataFrame,
    vocab: Optional[Mapping[str, Mapping[str, int]]] = None,
    exclude_self: bool = False,
) -> pd.DataFrame:
    """
    Build CLAIM_FEATURES for every row of ``df`` (training and inference use
    exactly this code path).

    Values that are absent or invalid stay NaN; nothing is imputed.
    """
    vocab = vocab or {}
    raw = _canonical_inputs(df)
    out = pd.DataFrame(index=df.index)

    amount = parse_amount(raw["claim_amount"])
    admission = parse_dates(raw["admission_date"])
    discharge = parse_dates(raw["discharge_date"])
    los = (discharge.dt.normalize() - admission.dt.normalize()).dt.days.astype(float)
    # Discharge before admission is an invalid stay length (NaN) but is kept as
    # its own explicit flag so the information is not lost or mistaken for
    # "dates missing".  NaN when either date is missing.
    inconsistent = (los < 0).astype(float).where(los.notna())
    los = los.mask(los < 0)
    items = parse_number(raw["billed_items_count"])

    out["claim_amount"] = amount
    out["claimed_per_day"] = amount / los.clip(lower=1)
    out["amount_per_item"] = amount / items.where(items > 0)
    out["patient_age"] = parse_number(raw["patient_age"], 0, 120)
    out["gender_male"] = encode_gender(raw["gender"])
    for field, name in (("diagnosis_code", "diagnosis_frequency"),
                        ("procedure_code", "procedure_frequency")):
        out[name] = _frequency_encode(
            normalise_category(raw[field]), vocab.get(field, {}), exclude_self
        )
    out["is_inpatient"] = parse_flag(raw["is_inpatient"])
    out["length_of_stay"] = los
    out["discharge_before_admission"] = inconsistent
    out["is_emergency_admission"] = parse_flag(raw["is_emergency_admission"])
    out["billed_items_count"] = items
    out["num_procedures"] = parse_number(raw["num_procedures"])
    out["num_tests"] = parse_number(raw["num_tests"])
    out["num_medications"] = parse_number(raw["num_medications"])
    out["preauthorization_obtained"] = parse_flag(raw["preauthorization_obtained"])
    out["previous_claims_count"] = parse_number(raw["previous_claims_count"])
    out["previous_rejection"] = parse_flag(raw["previous_rejection"])
    out["doc_missing_flag"] = parse_flag(raw["doc_missing_flag"])
    out["admission_month"] = admission.dt.month.astype(float)
    out["admission_dayofweek"] = admission.dt.dayofweek.astype(float)

    out = out.replace([np.inf, -np.inf], np.nan)
    return out[list(CLAIM_FEATURES)].astype(float)


def claim_dict_to_frame(claim_data: Mapping[str, Any]) -> pd.DataFrame:
    """
    One claim dict -> one-row DataFrame of raw inputs.

    Values in ``claim_data['metadata']`` (the existing input contract) are used
    only for keys that are not present at top level.
    """
    merged: Dict[str, Any] = {}
    metadata = claim_data.get("metadata")
    if isinstance(metadata, Mapping):
        merged.update(metadata)
    merged.update({k: v for k, v in claim_data.items() if k != "metadata"})
    return pd.DataFrame([merged])


# ---------------------------------------------------------------------------
# Evidence-engine sections
# ---------------------------------------------------------------------------

def _to_float(value: Any) -> float:
    """bool/number -> float; everything else (None, text, inf) -> NaN."""
    if value is None or isinstance(value, str):
        return float("nan")
    try:
        f = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return f if math.isfinite(f) else float("nan")


def _json_safe(value: float) -> Optional[float]:
    return None if value is None or (isinstance(value, float) and math.isnan(value)) else float(value)


def normalize_section(section: str,
                      values: Optional[Mapping[str, Any]]) -> Dict[str, Optional[float]]:
    """
    Project an engine's output onto the contract for ``section``.

    * every contract key is present in the result (None when not supplied),
    * unknown keys are ignored here (the orchestrator keeps the raw output
      in the evidence block so nothing is lost),
    * values are coerced to float (bool -> 0.0/1.0).
    """
    names = SECTION_FEATURES[section]
    values = values if isinstance(values, Mapping) else {}
    return {name: _json_safe(_to_float(values.get(name))) for name in names}


def section_availability(features: Mapping[str, Optional[float]]) -> Dict[str, Any]:
    present = [k for k, v in features.items() if v is not None]
    return {
        "available": bool(present),
        "features_present": len(present),
        "features_total": len(features),
    }


# ---------------------------------------------------------------------------
# Contract assembly and flattening
# ---------------------------------------------------------------------------

def build_contract(
    claim_data: Mapping[str, Any],
    vocab: Optional[Mapping[str, Mapping[str, int]]] = None,
    behavior_features: Optional[Mapping[str, Any]] = None,
    anomaly_features: Optional[Mapping[str, Any]] = None,
    network_features: Optional[Mapping[str, Any]] = None,
    document_features: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Dict[str, Optional[float]]]:
    """
    Build the stable internal representation::

        {"claim_features": {...}, "behavior_features": {...},
         "anomaly_features": {...}, "network_features": {...},
         "document_features": {...}}

    Every section always contains every contract key (None = not available),
    so downstream code never has to guard against missing keys.
    """
    claim_row = build_claim_features(claim_dict_to_frame(claim_data), vocab).iloc[0]
    return {
        "claim_features": {k: _json_safe(float(claim_row[k])) for k in CLAIM_FEATURES},
        "behavior_features": normalize_section("behavior_features", behavior_features),
        "anomaly_features": normalize_section("anomaly_features", anomaly_features),
        "network_features": normalize_section("network_features", network_features),
        "document_features": normalize_section("document_features", document_features),
    }


def flatten_contract(
    contract: Mapping[str, Mapping[str, Optional[float]]],
    feature_names: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """
    Contract -> one-row DataFrame in deterministic feature order.

    ``feature_names`` is the column list stored with the trained model; columns
    the contract does not know are NaN, so an older model keeps working if the
    contract later gains features.
    """
    flat: Dict[str, float] = {}
    for section in SECTION_FEATURES:
        for name, value in (contract.get(section) or {}).items():
            flat[name] = float("nan") if value is None else float(value)
    names: List[str] = list(feature_names) if feature_names is not None else list(FEATURE_ORDER)
    return pd.DataFrame([[flat.get(n, float("nan")) for n in names]], columns=names)


def build_feature_matrix(
    claim_df: pd.DataFrame,
    vocab: Optional[Mapping[str, Mapping[str, int]]] = None,
    exclude_self: bool = False,
) -> pd.DataFrame:
    """
    Batch version used for training: claim features from ``claim_df`` plus NaN
    for every evidence-engine feature (the historical dataset contains no
    behavioral / anomaly / network / document evidence).
    """
    claim = build_claim_features(claim_df, vocab, exclude_self)
    matrix = claim.reindex(columns=list(FEATURE_ORDER))
    return matrix.astype(float)


def get_feature_columns() -> List[str]:
    """Deterministic ML feature order."""
    return list(FEATURE_ORDER)
