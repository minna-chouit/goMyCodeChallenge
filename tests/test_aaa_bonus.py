from seeall.contrast import required_ratio_aaa
from seeall.aaa_bonus import aaa_passes


def test_required_ratio_aaa_normal_text():
    assert required_ratio_aaa(16) == 7.0


def test_required_ratio_aaa_large_text():
    assert required_ratio_aaa(24) == 4.5


def test_required_ratio_aaa_bold_large_text():
    assert required_ratio_aaa(19, bold=True) == 4.5


def _finding(ratio, size=16, bold=False, passes=True):
    return {"contrast_ratio": ratio, "font_size_css": size, "contrast_passes": passes, "text": "x"}


def test_aaa_passes_filters_by_aaa_threshold():
    findings = [_finding(7.5), _finding(5.0)]
    result = aaa_passes(findings)
    assert len(result) == 1
    assert result[0]["contrast_ratio"] == 7.5


def test_aaa_passes_uses_large_text_threshold():
    findings = [_finding(5.0, size=24)]  # 5.0 >= 4.5 AAA large-text threshold
    result = aaa_passes(findings)
    assert len(result) == 1


def test_aaa_passes_skips_already_failing_aa():
    findings = [_finding(8.0, passes=False)]  # weird case: shouldn't happen, but be defensive
    result = aaa_passes(findings)
    assert result == []
