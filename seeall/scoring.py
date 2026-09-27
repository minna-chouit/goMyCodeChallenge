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


def compute_score_v2(grouped_issues):
    """Per-issue (not per-instance) deduction, capped so a many-instance
    group can't blow out the score: base severity penalty, plus at most
    +50% of that base for extra instances, halved for a purely-AI group
    whose average confidence is below 0.5. Floored at 0."""
    total_penalty = 0.0
    for group in grouped_issues:
        base = _PENALTY.get(group.get("severity", "minor"), 3)
        n = len(group["instances"])
        extra_fraction = min(0.5, (n - 1) * 0.1)
        deduction = base * (1 + extra_fraction)

        if n:
            avg_confidence = sum(i.get("confidence", 1.0) for i in group["instances"]) / n
            if group.get("source") == "ai" and avg_confidence < 0.5:
                deduction *= 0.5

        total_penalty += deduction

    return max(0, round(100 - total_penalty))


def level_counts(grouped_issues):
    counts = {}
    for group in grouped_issues:
        level = group.get("level")
        counts[level] = counts.get(level, 0) + 1
    return counts


def grade_label(score):
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 50:
        return "Needs work"
    return "Poor"
