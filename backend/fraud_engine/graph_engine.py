"""Lightweight NetworkX-based graph intelligence.

The graph describes relationships; it does not label relationships as fraudulent.
"""
from __future__ import annotations
from typing import Any, Dict, Optional
import pandas as pd

try:
    import networkx as nx
except ImportError:  # graceful degradation if optional dependency is absent
    nx = None


def analyze(claim: dict, historical_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    claim = claim or {}
    df = historical_df.copy() if historical_df is not None else pd.DataFrame()
    result = {
        "patient_hospital_claim_count": 0,
        "doctor_hospital_relationship_count": 0,
        "shared_patient_count": 0,
        "provider_network_density": 0.0,
        "number_connected_providers": 0,
        "repeated_patient_doctor_hospital_count": 0,
        "provider_patient_concentration": 0.0,
        "referral_frequency": 0,
        "network_risk_score": 0.0,
        "graph_available": bool(nx is not None and not df.empty),
    }
    if df.empty or nx is None:
        return result

    patient = claim.get("patient_id", claim.get("user_id", claim.get("member_id")))
    hospital = claim.get("hospital_id", claim.get("provider_id", claim.get("hospital_name")))
    doctor = claim.get("doctor_id", claim.get("physician_id", claim.get("doctor_name")))

    pcol = next((c for c in ("patient_id", "user_id", "member_id") if c in df.columns), None)
    hcol = next((c for c in ("hospital_id", "provider_id", "hospital_name", "provider_name") if c in df.columns), None)
    dcol = next((c for c in ("doctor_id", "physician_id", "doctor_name", "physician_name") if c in df.columns), None)

    G = nx.Graph()
    if pcol and hcol:
        for _, row in df[[pcol, hcol]].dropna().iterrows():
            G.add_edge(f"patient:{row[pcol]}", f"provider:{row[hcol]}")
    if pcol and dcol:
        for _, row in df[[pcol, dcol]].dropna().iterrows():
            G.add_edge(f"patient:{row[pcol]}", f"doctor:{row[dcol]}")
    if dcol and hcol:
        for _, row in df[[dcol, hcol]].dropna().iterrows():
            G.add_edge(f"doctor:{row[dcol]}", f"provider:{row[hcol]}")

    if patient is not None and hospital is not None and pcol and hcol:
        patient_values = df[pcol].astype(str).str.strip()
        hospital_values = df[hcol].astype(str).str.strip()

        patient_match = patient_values == str(patient).strip()
        hospital_match = hospital_values == str(hospital).strip()

        result["patient_hospital_claim_count"] = int(
            (patient_match & hospital_match).sum()
        )

    if doctor is not None and hospital is not None and dcol and hcol:
        mask = (df[dcol].astype(str) == str(doctor)) & (df[hcol].astype(str) == str(hospital))
        result["doctor_hospital_relationship_count"] = int(mask.sum())

    if patient is not None and hcol:
        providers = df.loc[df[pcol].astype(str) == str(patient), hcol].dropna().astype(str).unique() if pcol else []
        result["number_connected_providers"] = int(len(providers))

    if hcol and pcol and hospital is not None:
        provider_rows = df[df[hcol].astype(str) == str(hospital)]
        unique_patients = provider_rows[pcol].nunique()
        result["provider_patient_concentration"] = (
            float(1 / unique_patients) if unique_patients else 0.0
        )
        if patient is not None:
            shared = set(provider_rows[pcol].astype(str))
            result["shared_patient_count"] = int(
                sum(
                    1 for provider in df[hcol].dropna().astype(str).unique()
                    if provider != str(hospital)
                    and patient is not None
                    and str(patient) in set(df.loc[df[hcol].astype(str) == provider, pcol].dropna().astype(str))
                )
            )

    if pcol and dcol and hcol:
        tuples = df[[pcol, dcol, hcol]].dropna().astype(str).value_counts()
        if patient is not None and doctor is not None and hospital is not None:
            result["repeated_patient_doctor_hospital_count"] = int(
                tuples.get((str(patient), str(doctor), str(hospital)), 0)
            )

    if "referral_id" in df.columns:
        result["referral_frequency"] = int(df["referral_id"].notna().sum())

    if len(G) > 1:
        result["provider_network_density"] = float(nx.density(G))

    # Evidence-only heuristic.
    # With limited network history, avoid treating ordinary relationships
    # as strong network evidence.
    provider_total_claims = (
        int((df[hcol].astype(str) == str(hospital)).sum())
        if hcol and hospital is not None
        else 0
    )

    triad_total = (
        int(len(tuples))
        if pcol and dcol and hcol
        else 0
    )

    if provider_total_claims > 0 and triad_total > 0:
        provider_concentration = result["provider_patient_concentration"]

        repeated_ratio = min(
            result["repeated_patient_doctor_hospital_count"] / triad_total,
            1.0
        )

        result["network_risk_score"] = float(
            (provider_concentration + repeated_ratio) / 2.0
        )
    else:
        result["network_risk_score"] = 0.0
    return result
