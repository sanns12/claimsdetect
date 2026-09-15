"""Robust statistical anomaly evidence. No final fraud decision is made here."""
from __future__ import annotations
from typing import Any, Dict, Optional
import numpy as np
import pandas as pd


def _amount_col(df):
    for c in ("claimed_amount", "claim_amount", "amount"):
        if c in df.columns:
            return c
    return None


def _score_from_robust_z(value, series) -> float:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) < 4 or not np.isfinite(value):
        return 0.0
    median = float(s.median())
    mad = float(np.median(np.abs(s - median)))
    if mad > 0:
        robust_z = abs(value - median) / (1.4826 * mad)
    else:
        q1, q3 = np.percentile(s, [25, 75])
        iqr = q3 - q1
        robust_z = abs(value - median) / (iqr / 1.349) if iqr > 0 else 0.0
    return float(min(1.0, max(0.0, robust_z / 5.0)))


def _percentile_score(value, series) -> float:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) < 4:
        return 0.0
    return float((s <= value).mean())


def _frequency_score(count, historical_counts) -> float:
    s = pd.to_numeric(pd.Series(historical_counts), errors="coerce").dropna()
    if len(s) < 4:
        return 0.0
    return _score_from_robust_z(count, s)


def analyze(claim: dict, historical_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """Return six independent anomaly scores plus raw statistics."""
    claim = claim or {}
    df = historical_df.copy() if historical_df is not None else pd.DataFrame()
    amount = float(claim.get("claim_amount", claim.get("claimed_amount", claim.get("amount", 0))) or 0)
    out = {
        "amount_anomaly_score": 0.0,
        "frequency_anomaly_score": 0.0,
        "procedure_anomaly_score": 0.0,
        "los_anomaly_score": 0.0,
        "temporal_anomaly_score": 0.0,
        "provider_deviation_score": 0.0,
        "overall_anomaly_score": 0.0,
        "history_available": len(df) > 0,
        "raw_statistics": {},
    }
    if df.empty:
        return out

    amount_col = _amount_col(df)
    if amount_col:
        df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce")
        amounts = df[amount_col].dropna()
        if len(amounts):
            out["amount_anomaly_score"] = max(
                _score_from_robust_z(amount, amounts),
                max(0.0, _percentile_score(amount, amounts) - 0.90) / 0.10,
            )
            out["raw_statistics"]["amount_median"] = float(amounts.median())
            out["raw_statistics"]["amount_p90"] = float(amounts.quantile(0.90))

    patient_id = claim.get("patient_id", claim.get("user_id", claim.get("member_id")))
    patient_col = next((c for c in ("patient_id", "user_id", "member_id") if c in df.columns), None)
    if patient_id is not None and patient_col:
        ph = df[df[patient_col].astype(str) == str(patient_id)].copy()
        if len(ph):
            dates_col = next((c for c in ("admission_date", "claim_date", "date", "created_at") if c in ph.columns), None)
            if dates_col:
                dates = pd.to_datetime(ph[dates_col], errors="coerce").dropna().sort_values()
                if len(dates):
                    out["frequency_anomaly_score"] = _frequency_score(len(ph), df.groupby(patient_col).size())
                    current_date = pd.to_datetime(claim.get("admission_date", claim.get("claim_date")), errors="coerce")
                    if pd.notna(current_date):
                        gaps = dates.diff().dt.days.dropna()
                        if len(gaps):
                            gap = float((current_date - dates.iloc[-1]).days)
                            out["temporal_anomaly_score"] = _score_from_robust_z(gap, gaps)
            proc_col = next((c for c in ("procedure_code", "procedure", "procedure_codes") if c in ph.columns), None)
            current_proc = str(claim.get("procedure_code", claim.get("procedure", ""))).strip()
            if proc_col and current_proc:
                proc_freq = (ph[proc_col].astype(str) == current_proc).sum()
                out["procedure_anomaly_score"] = min(1.0, proc_freq / max(len(ph), 1))

    if "length_of_stay" in df.columns:
        los = pd.to_numeric(df["length_of_stay"], errors="coerce").dropna()
        current_los = claim.get("length_of_stay")
        if current_los is None:
            a = pd.to_datetime(claim.get("admission_date"), errors="coerce")
            d = pd.to_datetime(claim.get("discharge_date"), errors="coerce")
            current_los = (d - a).days if pd.notna(a) and pd.notna(d) else None
        if current_los is not None and len(los):
            out["los_anomaly_score"] = _score_from_robust_z(float(current_los), los)

    provider_id = claim.get("hospital_id", claim.get("provider_id", claim.get("hospital_name")))
    provider_col = next((c for c in ("hospital_id", "provider_id", "hospital_name", "provider_name") if c in df.columns), None)
    if provider_id is not None and provider_col:
        ph = df[df[provider_col].astype(str) == str(provider_id)].copy()
        if len(ph) and amount_col:
            p_amounts = pd.to_numeric(ph[amount_col], errors="coerce").dropna()
            if len(p_amounts):
                out["provider_deviation_score"] = _score_from_robust_z(amount, p_amounts)

    scores = [
        out["amount_anomaly_score"], out["frequency_anomaly_score"],
        out["procedure_anomaly_score"], out["los_anomaly_score"],
        out["temporal_anomaly_score"], out["provider_deviation_score"],
    ]
    out["overall_anomaly_score"] = float(np.mean(scores))
    return out
