"""Per-simulation-view analysis: what breaks for these users, and how to fix it."""
from PIL import Image

from .contrast import contrast_ratio
from .simulate import simulate

_NEAR_THRESHOLD_MARGIN = 1.3  # a "barely passing" ratio this close to the floor is at-risk under low vision


def _simulate_color(rgb, kind):
    tiny = Image.new("RGB", (1, 1), tuple(int(c) for c in rgb))
    simulated = simulate(tiny, kind)
    return simulated.getpixel((0, 0))


def contrast_failures_in_view(findings, kind):
    """Findings (OCR raw findings with text_rgb/bg_rgb/contrast_passes/
    required_ratio/contrast_ratio) that fail contrast specifically in this
    simulated view, i.e. they passed in the original but not here."""
    failures = []
    for f in findings:
        if not f.get("contrast_passes"):
            continue  # already failing originally, not "only in this view"

        if kind == "low_vision":
            if f["contrast_ratio"] < f["required_ratio"] * _NEAR_THRESHOLD_MARGIN:
                failures.append(f)
            continue

        sim_text = _simulate_color(f["text_rgb"], kind)
        sim_bg = _simulate_color(f["bg_rgb"], kind)
        sim_ratio = contrast_ratio(sim_text, sim_bg)
        if sim_ratio < f["required_ratio"]:
            failures.append(f)
    return failures


def color_only_relevant_issues(ai_issues, kind):
    """color_only (1.4.1) findings are relevant to every colour-vision-affecting
    view, but not to low_vision (which is about acuity/blur, not colour)."""
    if kind == "low_vision":
        return []
    return [i for i in ai_issues if i.get("type") == "color_only"]


def simulation_panel_text(kind, contrast_failures, color_only_issues):
    label = kind.replace("_", " ")
    sentences = []
    if contrast_failures:
        n = len(contrast_failures)
        sentences.append(f"{n} more text element{'s' if n != 1 else ''} become hard to read for people with {label}.")
    if color_only_issues:
        n = len(color_only_issues)
        verb = "rely" if n != 1 else "relies"
        sentences.append(f"{n} finding{'s' if n != 1 else ''} {verb} on colour alone, which is a problem for {label}.")

    if not sentences:
        return "No extra problems for these users.", "No changes needed here."

    analysis = " ".join(sentences)
    fix = (
        "Add an icon or text label alongside colour, underline links, and "
        "increase contrast for the elements above — don't rely on red/green alone."
    )
    return analysis, fix
