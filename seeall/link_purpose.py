"""WCAG 2.4.4 Link Purpose: flag vague link/button text that doesn't say
where it goes or what it does, out of context."""
import re

VAGUE_LINK_PHRASES = [
    "click here", "read more", "here", "more", "learn more",
    "en savoir plus", "cliquez ici", "اضغط هنا", "اقرأ المزيد",
]

_SHORT_PHRASE_MAX_LEN = 4


def _compact(text):
    return re.sub(r"[^\w]", "", text.lower())


def is_vague_link_text(text):
    compact = _compact(text)
    for phrase in VAGUE_LINK_PHRASES:
        phrase_compact = _compact(phrase)
        if len(phrase_compact) <= _SHORT_PHRASE_MAX_LEN:
            if compact == phrase_compact:
                return True
        elif phrase_compact in compact:
            return True
    return False


def find_vague_links(ocr_findings):
    return [f for f in ocr_findings if is_vague_link_text(f["text"])]


def vague_link_issues(ocr_findings, image_size):
    w, h = image_size
    issues = []
    for f in find_vague_links(ocr_findings):
        x0, y0, x1, y1 = f["box_px"]
        issues.append({
            "type": "link_purpose",
            "severity": "serious",
            "box": [x0 / w, y0 / h, x1 / w, y1 / h],
            "box_px": f["box_px"],
            "description": f"Link/button text \"{f['text']}\" doesn't say where it goes or what it does.",
            "affected_users": "Screen reader users navigating by link list, and anyone scanning quickly.",
            "fix": "Use descriptive text, e.g. 'Read the shipping policy' instead of 'Click here'.",
            "confidence": 1.0,
            "source": "measured",
        })
    return issues
