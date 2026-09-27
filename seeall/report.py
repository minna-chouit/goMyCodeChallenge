"""Readable report generation: a designer-facing summary, "fix these 3
first", issues grouped by WCAG principle, and a "cannot check" disclosure.
Markdown and self-contained HTML outputs share the same section logic."""
from .badges import confidence_badge
from .scoring import compute_score_v2

PRINCIPLE_ORDER = ["Perceivable", "Operable", "Understandable", "Robust"]

_VERDICTS = {
    "Excellent": "This screen meets accessibility basics well.",
    "Good": "This screen mostly works, with a few things worth polishing.",
    "Needs work": "Several accessibility issues need fixing before this screen is ready for real users.",
    "Poor": "This screen has serious accessibility problems that will block real users.",
}

CANNOT_CHECK = [
    "Keyboard-only navigation and visible focus order (needs the real, interactive page, not a screenshot).",
    "Screen reader behaviour beyond the announced text we estimate (needs a real device test).",
    "Hover, focus, and error states that only appear on interaction.",
    "Whether animations can be paused, or content has strict time limits.",
    "The actual HTML structure (headings, landmarks, ARIA) — we only see pixels.",
]


def verdict_sentence(score, grade):
    return _VERDICTS.get(grade, "")


def top_fixes(grouped_issues, n=3):
    """Highest-impact issues first, using the same per-group deduction
    magnitude the score itself is built from."""
    def impact(group):
        return 100 - compute_score_v2([group])
    return sorted(grouped_issues, key=impact, reverse=True)[:n]


def group_by_principle(grouped_issues):
    buckets = {}
    for group in grouped_issues:
        buckets.setdefault(group["principle"], []).append(group)
    return {p: buckets[p] for p in PRINCIPLE_ORDER if buckets.get(p)}


def _issue_card_lines(i, group, markdown=True):
    min_confidence = min((inst.get("confidence", 1.0) for inst in group["instances"]), default=1.0)
    badge = confidence_badge(min_confidence)
    count = len(group["instances"])
    instance_note = f" ({count} instances)" if count > 1 else ""
    if markdown:
        return [
            f"### {i}. {group['plain_title']}{instance_note} — WCAG {group['wcag_id']} "
            f"{group['wcag_name']} (Level {group['level']}) — {badge}",
            f"- **Affects:** {group['who_is_affected']}",
            f"- **Why it matters:** {group['why_it_matters']}",
            f"- **Fix:** {group['fix']}",
            "",
        ]
    return [
        f"<h3>{i}. {group['plain_title']}{instance_note}</h3>",
        f"<p class='badge'>WCAG {group['wcag_id']} {group['wcag_name']} "
        f"(Level {group['level']}) &middot; {badge}</p>",
        f"<p><strong>Affects:</strong> {group['who_is_affected']}</p>",
        f"<p><strong>Why it matters:</strong> {group['why_it_matters']}</p>",
        f"<p><strong>Fix:</strong> {group['fix']}</p>",
    ]


def build_report(score, grade, grouped_issues, provider_name=None, elapsed=None):
    """Markdown report: summary, fix-these-3-first, grouped by principle, cannot-check."""
    lines = [
        "# SeeAll Accessibility Report",
        "",
        f"**Score: {score} / 100 — {grade}**",
        "",
        verdict_sentence(score, grade),
        "",
    ]
    if provider_name:
        lines.append(f"_AI provider: {provider_name}" + (f", {elapsed:.1f}s_" if elapsed else "_"))
        lines.append("")

    if not grouped_issues:
        lines.append("No issues found.")
        return "\n".join(lines)

    lines += ["## Fix these 3 first", ""]
    for i, group in enumerate(top_fixes(grouped_issues, 3), start=1):
        lines.append(f"{i}. **{group['plain_title']}** — {group['fix']}")
    lines.append("")

    lines += ["## All issues", ""]
    numbering = {id(g): i for i, g in enumerate(grouped_issues, start=1)}
    for principle, groups in group_by_principle(grouped_issues).items():
        lines.append(f"### {principle}")
        for group in groups:
            lines += _issue_card_lines(numbering[id(group)], group, markdown=True)

    lines += ["## What SeeAll cannot check from a screenshot", ""]
    lines += [f"- {item}" for item in CANNOT_CHECK]

    return "\n".join(lines)


_HTML_STYLE = """
<style>
  body { font-family: -apple-system, Segoe UI, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; }
  h1 { font-size: 1.6rem; } h2 { margin-top: 2rem; border-bottom: 2px solid #eee; padding-bottom: .3rem; }
  .score { font-size: 2.2rem; font-weight: bold; }
  .verdict { font-size: 1.1rem; color: #444; }
  .badge { color: #555; font-size: .9rem; }
  .fix-3 li { margin-bottom: .5rem; }
  .cannot-check li { color: #555; }
  @media print { body { margin: 0; } }
</style>
"""


def build_html_report(score, grouped_issues, provider_name=None, elapsed=None):
    """Self-contained, styled, printable HTML report."""
    from .scoring import grade_label
    grade = grade_label(score)

    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>SeeAll Accessibility Report</title>",
        _HTML_STYLE, "</head><body>",
        "<h1>SeeAll Accessibility Report</h1>",
        f"<p class='score'>{score} / 100 — {grade}</p>",
        f"<p class='verdict'>{verdict_sentence(score, grade)}</p>",
    ]
    if provider_name:
        elapsed_txt = f", {elapsed:.1f}s" if elapsed else ""
        parts.append(f"<p><em>AI provider: {provider_name}{elapsed_txt}</em></p>")

    if not grouped_issues:
        parts.append("<p>No issues found.</p>")
        parts.append("</body></html>")
        return "\n".join(parts)

    parts.append("<h2>Fix these 3 first</h2><ol class='fix-3'>")
    for group in top_fixes(grouped_issues, 3):
        parts.append(f"<li><strong>{group['plain_title']}</strong> — {group['fix']}</li>")
    parts.append("</ol>")

    parts.append("<h2>All issues</h2>")
    numbering = {id(g): i for i, g in enumerate(grouped_issues, start=1)}
    for principle, groups in group_by_principle(grouped_issues).items():
        parts.append(f"<h3 style='margin-top:1.5rem'>{principle}</h3>")
        for group in groups:
            parts += _issue_card_lines(numbering[id(group)], group, markdown=False)

    parts.append("<h2>What SeeAll cannot check from a screenshot</h2><ul class='cannot-check'>")
    parts += [f"<li>{item}</li>" for item in CANNOT_CHECK]
    parts.append("</ul>")

    parts.append("</body></html>")
    return "\n".join(parts)
