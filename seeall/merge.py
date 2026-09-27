"""Merge deterministic issues with AI-found issues into one ranked list."""

_SEVERITY_ORDER = {"critical": 0, "serious": 1, "minor": 2}


def ai_issues_to_schema(ai_response, image_size):
    w, h = image_size
    issues = []
    for issue in ai_response.issues:
        x0, y0, x1, y1 = issue.box
        box_px = (int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h))
        item = {
            "type": issue.type,
            "severity": issue.severity,
            "box": issue.box,
            "box_px": box_px,
            "description": issue.description,
            "affected_users": issue.affected_users,
            "fix": issue.fix,
            "confidence": issue.confidence,
            "source": "ai",
        }
        if issue.confidence < 0.5:
            item["needs_human_check"] = True
        issues.append(item)
    return issues


def merge_and_rank(deterministic_issues, ai_issues):
    combined = deterministic_issues + ai_issues
    combined.sort(key=lambda i: _SEVERITY_ORDER.get(i.get("severity", "minor"), 2))
    return combined
