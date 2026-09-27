"""Markdown report generation."""
from .badges import confidence_badge


def build_report(score, issues, provider_name=None, elapsed=None):
    lines = [
        "# SeeAll Accessibility Report",
        "",
        f"**Score: {score} / 100**",
        "",
    ]
    if provider_name:
        lines.append(f"_AI provider: {provider_name}" + (f", {elapsed:.1f}s_" if elapsed else "_"))
        lines.append("")

    if not issues:
        lines.append("No issues found.")
    for i, issue in enumerate(issues, start=1):
        badge = confidence_badge(issue.get("confidence", 1.0))
        lines += [
            f"## {i}. [{issue['severity'].upper()}] {issue['type']} — {badge}",
            f"- **Where:** box {issue.get('box_px', issue.get('box'))}",
            f"- **Issue:** {issue['description']}",
            f"- **Affects:** {issue['affected_users']}",
            f"- **Fix:** {issue['fix']}",
            "",
        ]
    return "\n".join(lines)
