"""Group flat issue dicts into WCAG-tagged issues with multiple instances (A2)."""
from .wcag import criterion_for_type

_SEVERITY_RANK = {"critical": 0, "serious": 1, "minor": 2}

PLAIN_TITLES = {
    "contrast": "Text is hard to read",
    "small_target": "Tap target or text is too small",
    "color_only": "Meaning is shown by colour alone",
    "icon_unclear": "Icon meaning is unclear",
    "missing_label": "Missing or unclear label",
    "layout": "Layout may be confusing",
    "alt_text": "Image needs a text alternative",
    "other": "Accessibility issue",
    "link_purpose": "Link text doesn't say where it goes",
    "non_text_contrast": "Input or button boundary is hard to see",
    "image_of_text": "Text shown as an image",
    "error_handling": "Error isn't clearly described",
    "captcha_or_memory_test": "Login requires a puzzle or memory test",
    "drag_only": "Action can only be done by dragging",
    "sticky_obscures_focus": "Sticky bar may hide the focused item",
    "orientation_lock": "Screen may be locked to one orientation",
    "visual_presentation": "Text layout is hard to read",
}


def group_issues(flat_issues):
    """Groups issues sharing the same WCAG criterion + issue type (same kind
    of fix) into one issue with several instances."""
    groups = {}
    order = []

    for issue in flat_issues:
        criterion = criterion_for_type(issue["type"])
        key = (criterion.id, issue["type"])
        if key not in groups:
            groups[key] = {
                "wcag_id": criterion.id,
                "wcag_name": criterion.name,
                "level": criterion.level,
                "principle": criterion.principle,
                "type": issue["type"],
                "plain_title": PLAIN_TITLES.get(issue["type"], issue["type"]),
                "severity": issue["severity"],
                "who_is_affected": issue.get("affected_users", ""),
                "why_it_matters": issue.get("description", ""),
                "fix": issue.get("fix", ""),
                "instances": [],
                "_sources": set(),
            }
            order.append(key)

        group = groups[key]
        group["_sources"].add(issue.get("source", "measured"))
        if _SEVERITY_RANK.get(issue["severity"], 2) < _SEVERITY_RANK.get(group["severity"], 2):
            group["severity"] = issue["severity"]

        group["instances"].append({
            "box": issue.get("box"),
            "box_px": issue.get("box_px"),
            "description": issue.get("description"),
            "confidence": issue.get("confidence", 1.0),
        })

    result = []
    for key in order:
        group = groups[key]
        group["source"] = "+".join(sorted(group.pop("_sources")))
        result.append(group)
    return result
