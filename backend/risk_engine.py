"""
Business Risk Engine
Converts ML probability into business risk tiers.
"""

def calculate_risk(probability: float) -> str:
    """
    Convert fraud probability to business risk tier.
    """

    if probability >= 0.80:
        return "critical"
    elif probability >= 0.60:
        return "high"
    elif probability >= 0.30:
        return "medium"
    else:
        return "low"