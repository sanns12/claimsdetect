"""
Fraud Stub - Returns fixed output when model unavailable
"""

def run_stub(claim_data):
    """
    Stub mode for testing - returns fixed output
    
    Args:
        claim_data: dict with claim information (not used in stub)
        
    Returns:
        dict with fixed fraud_risk_score, risk_band, top_risk_factors
    """
    return {
        "fraud_risk_score": 0.15,
        "risk_band": "low",
        "top_risk_factors": ["Stub mode - model not loaded"]
    }
