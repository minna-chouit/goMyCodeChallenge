"""WCAG 1.4.6 Contrast (Enhanced): informational only, no score deduction —
report which already-passing text also clears the AAA bar."""
from .contrast import required_ratio_aaa


def aaa_passes(findings):
    result = []
    for f in findings:
        if not f.get("contrast_passes"):
            continue
        aaa_threshold = required_ratio_aaa(f["font_size_css"])
        if f["contrast_ratio"] >= aaa_threshold:
            result.append(f)
    return result
