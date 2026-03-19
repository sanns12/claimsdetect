"""
Stub implementation for early integration testing
"""

def run_stub(claim_id: str, document_paths: list) -> dict:
    """
    Stub function that returns fixed output
    """
    return {
        "document_consistency_score": 0.72,
        "mismatch_flags": [
            "amount_mismatch",
            "low_ocr_confidence"
        ]
    }

def fallback_stub(claim_id: str, document_paths: list) -> dict:
    """
    Safe fallback when main pipeline fails
    """
    return {
        "document_consistency_score": 0.5,
        "mismatch_flags": ["system_fallback_triggered"]
    }