"""WCAG 2.2 criterion catalog for issue types SeeAll can find."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Criterion:
    id: str
    name: str
    level: str
    principle: str
    description: str


CATALOG = {
    "1.4.3": Criterion("1.4.3", "Contrast (Minimum)", "AA", "Perceivable",
        "Text needs enough contrast with its background to be readable."),
    "1.1.1": Criterion("1.1.1", "Non-text Content", "A", "Perceivable",
        "Images and icons need a text alternative that conveys the same meaning."),
    "1.4.1": Criterion("1.4.1", "Use of Color", "A", "Perceivable",
        "Colour alone must not be the only way to convey information."),
    "1.3.1": Criterion("1.3.1", "Info and Relationships", "A", "Perceivable",
        "Structure and grouping shown visually must also be available to assistive tech."),
    "3.3.2": Criterion("3.3.2", "Labels or Instructions", "A", "Understandable",
        "Form fields need a clear, persistent label, not just a hint that disappears."),
    "2.5.8": Criterion("2.5.8", "Target Size (Minimum)", "AA", "Operable",
        "Interactive targets need to be at least 24x24 CSS pixels."),
    "4.1.2": Criterion("4.1.2", "Name, Role, Value", "A", "Robust",
        "Interactive elements need a programmatic name assistive tech can read."),
}

TYPE_TO_WCAG = {
    "contrast": "1.4.3",
    "small_target": "2.5.8",
    "color_only": "1.4.1",
    "icon_unclear": "1.1.1",
    "missing_label": "3.3.2",
    "layout": "1.3.1",
    "alt_text": "1.1.1",
    "other": "4.1.2",
}

_FALLBACK_WCAG_ID = "4.1.2"


def criterion_for_type(issue_type):
    wcag_id = TYPE_TO_WCAG.get(issue_type, _FALLBACK_WCAG_ID)
    return CATALOG[wcag_id]
