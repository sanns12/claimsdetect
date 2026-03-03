"""
Risk Band Mapper - Converts fraud score to low/medium/high
"""

def map_risk_band(score):
    """
    Convert 0-1 fraud probability score to risk band
    
    Args:
        score: float between 0 and 1
        
    Returns:
        string: 'low', 'medium', or 'high'
    """
    if score < 0.3:
        return "low"
    elif score < 0.6:
        return "medium"
    else:
        return "high"
