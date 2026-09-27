"""Overall accessibility score: 100 minus a severity-weighted penalty per issue."""

_PENALTY = {"critical": 15, "serious": 8, "minor": 3}


def compute_score(issues):
    penalty = sum(_PENALTY.get(i.get("severity", "minor"), 3) for i in issues)
    return max(0, 100 - penalty)
