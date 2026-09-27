from seeall.vision_analysis import (
    contrast_failures_in_view, color_only_relevant_issues, simulation_panel_text,
)


def _finding(text_rgb=(0, 0, 0), bg_rgb=(255, 255, 255), passes=True, required=4.5, ratio=10.0):
    return {
        "text_rgb": text_rgb, "bg_rgb": bg_rgb, "contrast_passes": passes,
        "required_ratio": required, "contrast_ratio": ratio,
    }


def test_contrast_failures_in_view_detects_new_failure(monkeypatch):
    import seeall.vision_analysis as va
    # simulate_color collapses everything to mid-grey -> ratio drops below required
    monkeypatch.setattr(va, "_simulate_color", lambda rgb, kind: (128, 128, 128))
    findings = [_finding(passes=True)]
    result = contrast_failures_in_view(findings, "deuteranopia")
    assert len(result) == 1


def test_contrast_failures_in_view_no_new_failures_when_still_passing(monkeypatch):
    import seeall.vision_analysis as va
    monkeypatch.setattr(va, "_simulate_color", lambda rgb, kind: rgb)  # no change
    findings = [_finding(passes=True)]
    result = contrast_failures_in_view(findings, "deuteranopia")
    assert result == []


def test_contrast_failures_in_view_skips_already_failing():
    findings = [_finding(passes=False)]
    result = contrast_failures_in_view(findings, "deuteranopia")
    assert result == []  # already failing in the original view, not "only in this view"


def test_low_vision_flags_near_threshold_passes():
    findings = [_finding(passes=True, ratio=5.0, required=4.5)]  # barely passes
    result = contrast_failures_in_view(findings, "low_vision")
    assert len(result) == 1


def test_color_only_relevant_for_color_views():
    issues = [{"type": "color_only"}, {"type": "contrast"}]
    assert len(color_only_relevant_issues(issues, "protanopia")) == 1


def test_color_only_not_relevant_for_low_vision():
    issues = [{"type": "color_only"}]
    assert color_only_relevant_issues(issues, "low_vision") == []


def test_panel_text_no_extra_problems():
    analysis, fix = simulation_panel_text("tritanopia", [], [])
    assert "No extra problems" in analysis


def test_panel_text_reports_findings():
    analysis, fix = simulation_panel_text("deuteranopia", [_finding()], [{"type": "color_only"}])
    assert "deuteranopia" in analysis or "1" in analysis
    assert fix


def test_panel_text_singular_grammar():
    analysis, _ = simulation_panel_text("deuteranopia", [], [{"type": "color_only"}])
    assert "1 finding relies" in analysis
