"""
Adapter between the existing Document Intelligence engine
and the independent fraud-intelligence pipeline.

This adapter does not implement document analysis itself.
It exposes the structured evidence already produced by
document_engine.main.run().
"""

from typing import Dict, Any, List, Optional

from . import main as document_main


def analyze(
    claim_id: str,
    document_paths: Optional[List[str]] = None,
    claim_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run the existing Document Intelligence engine and expose
    structured evidence for the fraud pipeline.

    Returns deterministic document evidence without making
    a final fraud decision.
    """

    document_paths = document_paths or []
    claim_metadata = claim_metadata or {}

    # No documents supplied
    if not document_paths:
        return {
            "ocr_confidence": 0.0,
            "document_similarity": 0.0,
            "duplicate_probability": 0.0,
            "field_mismatch_score": 1.0,
            "alteration_indicator": 0.0,
            "missing_information_indicator": 1.0,
            "document_consistency_score": 0.0,
            "mismatch_flags": ["no_document_data"],
        }

    result = document_main.run(
        claim_id=claim_id,
        document_paths=document_paths,
        claim_metadata=claim_metadata,
    )

    # Read values actually produced by the existing document engine.
    ocr_confidence = float(result.get("ocr_confidence", 0.0))
    document_similarity = float(result.get("document_similarity", 0.0))
    field_mismatch_score = float(result.get("field_mismatch_score", 0.0))
    document_consistency_score = float(
        result.get("document_consistency_score", 0.0)
    )

    mismatch_flags = result.get("mismatch_flags", [])
    if not isinstance(mismatch_flags, list):
        mismatch_flags = list(mismatch_flags) if mismatch_flags else []

    # These are not currently calculated by the existing document engine.
    # Keep them at neutral values rather than inventing evidence.
    duplicate_probability = float(
        claim_metadata.get("duplicate_probability", 0.0)
    )

    alteration_indicator = float(
        claim_metadata.get("alteration_indicator", 0.0)
    )

    missing_information_indicator = float(
        result.get("missing_information_indicator", 0.0)
    )

    return {
        "ocr_confidence": ocr_confidence,
        "document_similarity": document_similarity,
        "duplicate_probability": duplicate_probability,
        "field_mismatch_score": field_mismatch_score,
        "alteration_indicator": alteration_indicator,
        "missing_information_indicator": missing_information_indicator,
        "document_consistency_score": document_consistency_score,
        "mismatch_flags": mismatch_flags,
    }