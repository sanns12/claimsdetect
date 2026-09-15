"""Independent behavioral intelligence for claims.

The engine produces evidence features only. It does not make a fraud decision.
It accepts the existing claim dictionary plus an optional historical DataFrame.
Unknown/unsupported fields are treated as unavailable rather than fabricated.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, Optional
import math
import numpy as np
import pandas as pd


def _first(d: dict, *keys: str, default=None):
    for key in keys:
        if key in d and d[key] is not None:
            return d[key]
    return default


def _amount_column(df: pd.DataFrame) -> Optional[str]:
    for c in ("claimed_amount", "claim_amount", "amount"):
        if c in df.columns:
            return c
    return None


def _date_column(df: pd.DataFrame) -> Optional[str]:
    for c in ("admission_date", "claim_date", "date", "created_at", "submitted_at"):
        if c in df.columns:
            return c
    return None


def _id_column(df: pd.DataFrame, names: Iterable[str]) -> Optional[str]:
    for c in names:
        if c in df.columns:
            return c
    return None


def _numeric(series, default=0.0):
    out = pd.to_numeric(series, errors="coerce")
    return out if len(out) else pd.Series(dtype=float)


def _safe_rate(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def _history_frame(claim: dict, historical_df: Optional[pd.DataFrame]) -> pd.DataFrame:
    if historical_df is None:
        return pd.DataFrame()
    df = historical_df.copy()
    claim_id = _first(claim, "claim_id", "id", "claim_number")
    if claim_id is not None:
        for c in ("claim_id", "id", "claim_number"):
            if c in df.columns:
                df = df[df[c].astype(str) != str(claim_id)]
                break
    return df.reset_index(drop=True)


def _procedure_values(value) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, (list, tuple, set)):
        return {str(v) for v in value if v is not None and str(v).strip()}
    text = str(value)
    return {v.strip() for v in text.replace("|", ",").split(",") if v.strip()}


def _is_surgery(value) -> bool:
    text = " ".join(_procedure_values(value)).lower()
    if not text:
        return False
    return any(token in text for token in ("surg", "operation", "cpt_33", "cpt33"))


def analyze(claim: dict, historical_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """Return deterministic behavioral evidence for one claim."""
    claim = claim or {}
    hist = _history_frame(claim, historical_df)
    has_history = len(hist) > 0
    amount = float(_first(claim, "claim_amount", "claimed_amount", "amount", default=0) or 0)

    result: Dict[str, Any] = {
        "patient_claim_frequency": 0,
        "patient_avg_claim_amount": 0.0,
        "patient_hospitalization_frequency": 0,
        "patient_distinct_hospital_count": 0,
        "patient_procedure_frequency": 0,
        "patient_days_since_previous_claim": None,
        "patient_historical_high_value_claim_rate": 0.0,
        "patient_history_available": False,
        "provider_claim_frequency": 0,
        "provider_avg_claim_amount": 0.0,
        "provider_avg_length_of_stay": 0.0,
        "provider_surgery_rate": 0.0,
        "provider_rejection_rate": 0.0,
        "provider_high_value_claim_rate": 0.0,
        "provider_monthly_claim_growth": 0.0,
        "provider_deviation_from_baseline": 0.0,
        "provider_history_available": False,
        "doctor_claim_frequency": 0,
        "doctor_avg_claim_amount": 0.0,
        "doctor_procedure_frequency": 0,
        "doctor_referral_frequency": 0,
        "doctor_rejection_rate": 0.0,
        "doctor_high_cost_rate": 0.0,
        "doctor_history_available": False,
    }

    if not has_history:
        return result

    amount_col = _amount_column(hist)
    if amount_col:
        hist[amount_col] = pd.to_numeric(hist[amount_col], errors="coerce")
        hist = hist[hist[amount_col].notna()].copy()

    patient_id = _first(claim, "patient_id", "user_id", "member_id")
    patient_col = _id_column(hist, ("patient_id", "user_id", "member_id"))
    if patient_id is not None and patient_col:
        ph = hist[hist[patient_col].astype(str) == str(patient_id)].copy()
        if len(ph):
            result["patient_history_available"] = True
            result["patient_claim_frequency"] = int(len(ph))
            if amount_col:
                result["patient_avg_claim_amount"] = float(ph[amount_col].mean())
                cutoff = float(hist[amount_col].quantile(0.90)) if len(hist) >= 5 else None
                result["patient_historical_high_value_claim_rate"] = (
                    float((ph[amount_col] >= cutoff).mean()) if cutoff is not None else 0.0
                )
            date_col = _date_column(ph)
            if date_col:
                dates = pd.to_datetime(ph[date_col], errors="coerce").dropna().sort_values()
                result["patient_hospitalization_frequency"] = int(len(dates))
                current_date = pd.to_datetime(_first(claim, date_col, "admission_date", "claim_date"), errors="coerce")
                if pd.notna(current_date) and len(dates):
                    result["patient_days_since_previous_claim"] = int((current_date - dates.iloc[-1]).days)
            hospital_col = _id_column(ph, ("hospital_id", "hospital_name", "provider_id"))
            if hospital_col:
                result["patient_distinct_hospital_count"] = int(ph[hospital_col].nunique(dropna=True))
            proc_col = _id_column(ph, ("procedure_code", "procedure", "procedure_codes"))
            if proc_col:
                current_procs = _procedure_values(_first(claim, "procedure_code", "procedure", "procedure_codes"))
                result["patient_procedure_frequency"] = int(
                    sum(bool(_procedure_values(v) & current_procs) for v in ph[proc_col])
                )

    provider_id = _first(claim, "hospital_id", "provider_id", "hospital_name", "provider_name")
    provider_col = _id_column(hist, ("hospital_id", "provider_id", "hospital_name", "provider_name"))
    if provider_id is not None and provider_col:
        vh = hist[hist[provider_col].astype(str) == str(provider_id)].copy()
        if len(vh):
            result["provider_history_available"] = True
            result["provider_claim_frequency"] = int(len(vh))
            if amount_col:
                result["provider_avg_claim_amount"] = float(vh[amount_col].mean())
                cutoff = float(hist[amount_col].quantile(0.90)) if len(hist) >= 5 else None
                result["provider_high_value_claim_rate"] = (
                    float((vh[amount_col] >= cutoff).mean()) if cutoff is not None else 0.0
                )
                baseline = float(hist[amount_col].median())
                result["provider_deviation_from_baseline"] = (
                    float((amount - baseline) / baseline) if baseline > 0 else 0.0
                )
            if "length_of_stay" in vh.columns:
                los = pd.to_numeric(vh["length_of_stay"], errors="coerce").dropna()
                result["provider_avg_length_of_stay"] = float(los.mean()) if len(los) else 0.0
            elif "admission_date" in vh.columns and "discharge_date" in vh.columns:
                a = pd.to_datetime(vh["admission_date"], errors="coerce")
                d = pd.to_datetime(vh["discharge_date"], errors="coerce")
                los = (d - a).dt.days.dropna()
                result["provider_avg_length_of_stay"] = float(los.mean()) if len(los) else 0.0
            proc_col = _id_column(vh, ("procedure_code", "procedure", "procedure_codes"))
            if proc_col:
                result["provider_surgery_rate"] = float(vh[proc_col].map(_is_surgery).mean())
            status_col = _id_column(vh, ("status", "claim_status", "outcome"))
            if status_col:
                result["provider_rejection_rate"] = float(
                    vh[status_col].astype(str).str.lower().isin({"rejected", "denied"}).mean()
                )
            date_col = _date_column(vh)
            if date_col and len(vh) >= 2:
                dates = pd.to_datetime(vh[date_col], errors="coerce").dropna()
                if len(dates):
                    monthly = dates.dt.to_period("M").value_counts().sort_index()
                    if len(monthly) >= 2 and monthly.iloc[-2] > 0:
                        result["provider_monthly_claim_growth"] = float(
                            (monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2]
                        )

    doctor_id = _first(claim, "doctor_id", "physician_id", "doctor_name", "physician_name")
    doctor_col = _id_column(hist, ("doctor_id", "physician_id", "doctor_name", "physician_name"))
    if doctor_id is not None and doctor_col:
        dh = hist[hist[doctor_col].astype(str) == str(doctor_id)].copy()
        if len(dh):
            result["doctor_history_available"] = True
            result["doctor_claim_frequency"] = int(len(dh))
            if amount_col:
                result["doctor_avg_claim_amount"] = float(dh[amount_col].mean())
                cutoff = float(hist[amount_col].quantile(0.90)) if len(hist) >= 5 else None
                result["doctor_high_cost_rate"] = (
                    float((dh[amount_col] >= cutoff).mean()) if cutoff is not None else 0.0
                )
            proc_col = _id_column(dh, ("procedure_code", "procedure", "procedure_codes"))
            if proc_col:
                current_procs = _procedure_values(_first(claim, "procedure_code", "procedure", "procedure_codes"))
                result["doctor_procedure_frequency"] = int(
                    sum(bool(_procedure_values(v) & current_procs) for v in dh[proc_col])
                )
            referral_col = _id_column(dh, ("referral_id", "referred_to", "referral"))
            if referral_col:
                result["doctor_referral_frequency"] = int(dh[referral_col].notna().sum())
            status_col = _id_column(dh, ("status", "claim_status", "outcome"))
            if status_col:
                result["doctor_rejection_rate"] = float(
                    dh[status_col].astype(str).str.lower().isin({"rejected", "denied"}).mean()
                )

    return result
