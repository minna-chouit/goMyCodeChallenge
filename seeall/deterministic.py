"""Turn raw OCR/contrast findings into the shared issue schema used by
both deterministic checks and the AI vision pass."""


def to_issues(findings, image_size):
    w, h = image_size
    issues = []
    for f in findings:
        x0, y0, x1, y1 = f["box_px"]
        box = [x0 / w, y0 / h, x1 / w, y1 / h]

        if not f["contrast_passes"]:
            fix = "Needs manual color check."
            if "suggested_hex" in f:
                fix = f"Change text color to {f['suggested_hex']} -> {f['suggested_ratio']}:1"
            issues.append({
                "type": "contrast",
                "severity": "critical" if f["contrast_ratio"] < f["required_ratio"] * 0.7 else "serious",
                "box": box,
                "box_px": f["box_px"],
                "description": (
                    f"Text \"{f['text']}\" has contrast ratio {f['contrast_ratio']}:1, "
                    f"below the required {f['required_ratio']}:1."
                ),
                "affected_users": "Users with low vision or color vision deficiencies.",
                "fix": fix,
                "confidence": 1.0,
                "source": "measured",
            })

        if f["small_text"]:
            issues.append({
                "type": "small_target",
                "severity": "minor",
                "box": box,
                "box_px": f["box_px"],
                "description": (
                    f"Text \"{f['text']}\" is estimated at {f['font_size_css']}px, "
                    "below the 12px readability floor."
                ),
                "affected_users": "Users with low vision, older users, and anyone at arm's length from a phone.",
                "fix": "Increase font size to at least 12-14 CSS px.",
                "confidence": 1.0,
                "source": "measured",
            })
    return issues
