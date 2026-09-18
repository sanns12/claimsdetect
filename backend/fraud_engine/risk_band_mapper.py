"""
Risk Band Mapper - Converts a 0-1 score to low / medium / high

The cut-offs (0.3 and 0.6) are the ones already used by this project; they are
exposed as constants so evidence_fusion can reuse the same boundaries for both
the final score and the individual evidence components.
"""

LOW_MAX = 0.3       # score <  0.3  -> low
MEDIUM_MAX = 0.6    # score <  0.6  -> medium, otherwise high


def map_risk_band(score):
    """
    Convert 0-1 score to risk band

    Args:
        score: float between 0 and 1

    Returns:
        string: 'low', 'medium', or 'high'
    """
    if score < LOW_MAX:
        return "low"
    elif score < MEDIUM_MAX:
        return "medium"
    else:
        return "high"
