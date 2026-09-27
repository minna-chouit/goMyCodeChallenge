"""Overall accessibility score: 100 minus a severity-weighted penalty per issue."""

_PENALTY = {"critical": 15, "serious": 8, "minor": 3}


def compute_score(issues):
    penalty = sum(_PENALTY.get(i.get("severity", "minor"), 3) for i in issues)
    return max(0, 100 - penalty)


def severity_breakdown(issues):
    counts = {"critical": 0, "serious": 0, "minor": 0}
    for issue in issues:
        severity = issue.get("severity", "minor")
        counts[severity] = counts.get(severity, 0) + 1
    return counts


def format_breakdown(counts):
    parts = [f"{n} {severity}" for severity, n in counts.items() if n]
    return ", ".join(parts) if parts else "No issues"
