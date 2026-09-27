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
    "2.4.4": Criterion("2.4.4", "Link Purpose (In Context)", "A", "Operable",
        "Link and button text needs to say where it goes or what it does, out of context."),
    "1.4.11": Criterion("1.4.11", "Non-text Contrast", "AA", "Perceivable",
        "Input borders, button edges, and icons need at least 3:1 contrast against their surroundings."),
    "1.4.5": Criterion("1.4.5", "Images of Text", "AA", "Perceivable",
        "Real, selectable text should be used instead of an image showing text."),
    "3.3.1": Criterion("3.3.1", "Error Identification", "A", "Understandable",
        "Errors must be described in text, not only implied by colour, and should suggest a fix."),
    "3.3.8": Criterion("3.3.8", "Accessible Authentication (Minimum)", "AA", "Understandable",
        "Logging in shouldn't require solving a puzzle or memory test with no alternative."),
    "2.5.7": Criterion("2.5.7", "Dragging Movements", "AA", "Operable",
        "Anything done by dragging needs a single-tap or click alternative."),
    "2.4.11": Criterion("2.4.11", "Focus Not Obscured (Minimum)", "AA", "Operable",
        "A sticky header or footer must not fully hide the element that currently has focus."),
    "1.3.4": Criterion("1.3.4", "Orientation", "AA", "Perceivable",
        "Content shouldn't be locked to one screen orientation without a good reason."),
    "1.4.8": Criterion("1.4.8", "Visual Presentation", "AAA", "Perceivable",
        "Justified text and very long lines are harder to read; ragged edges and shorter lines help."),
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
    "link_purpose": "2.4.4",
    "non_text_contrast": "1.4.11",
    "image_of_text": "1.4.5",
    "error_handling": "3.3.1",
    "captcha_or_memory_test": "3.3.8",
    "drag_only": "2.5.7",
    "sticky_obscures_focus": "2.4.11",
    "orientation_lock": "1.3.4",
    "visual_presentation": "1.4.8",
}

_FALLBACK_WCAG_ID = "4.1.2"


def criterion_for_type(issue_type):
    wcag_id = TYPE_TO_WCAG.get(issue_type, _FALLBACK_WCAG_ID)
    return CATALOG[wcag_id]
