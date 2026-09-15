"""Adapter that exposes existing document intelligence as structured evidence.

This does not replace document_engine.main.run(); it wraps it and preserves the
existing two-key contract for callers that still depend on it.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional


def analyze(claim_id: str, document_paths: List[str], claim_metadata: Optional[dict] = None) -> Dict[str, Any]:
    from .main import run
    result = run(claim_id, document_paths, claim_metadata or {})
    flags = result.get("mismatch_flags", []) or []

    score = float(result.get("document_consistency_score", 0.0))
    return {
        "ocr_confidence": float(claim_metadata.get("ocr_confidence", score) if claim_metadata else score),
        "document_similarity": score,
        "duplicate_probability": float(
            claim_metadata.get("duplicate_probability", 0.0) if claim_metadata else 0.0
        ),
        "field_mismatch_score": min(1.0, len(flags) / 5.0),
        "alteration_indicator": float(
            claim_metadata.get("alteration_indicator", 0.0) if claim_metadata else 0.0
        ),
        "missing_information_indicator": float(
            claim_metadata.get("missing_information_indicator", 0.0) if claim_metadata else 0.0
        ),
        "document_consistency_score": score,
        "mismatch_flags": flags,
    }
