"""Confidence badge text for AI-found issues (deterministic issues are always 100%)."""

_NEEDS_HUMAN_CHECK_THRESHOLD = 0.5


def confidence_badge(confidence):
    pct = round(confidence * 100)
    if confidence < _NEEDS_HUMAN_CHECK_THRESHOLD:
        return f"\U0001F7E1 Needs human check ({pct}% confidence)"
    return f"\U0001F7E2 {pct}% confidence"
