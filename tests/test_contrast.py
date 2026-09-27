from seeall.contrast import contrast_ratio, required_ratio, suggest_passing_color, css_snippet, hex_to_rgb


def test_black_white_ratio():
    assert round(contrast_ratio((0, 0, 0), (255, 255, 255)), 1) == 21.0


def test_grey_on_white_ratio():
    ratio = contrast_ratio((0x77, 0x77, 0x77), (255, 255, 255))
    assert abs(ratio - 4.48) < 0.05


def test_required_ratio_thresholds():
    assert required_ratio(16) == 4.5
    assert required_ratio(24) == 3.0
    assert required_ratio(19, bold=True) == 3.0


def test_suggest_passing_color_reaches_target():
    hexcode, ratio = suggest_passing_color((0x9E, 0x9E, 0x9E), (255, 255, 255), 4.5)
    assert ratio >= 4.5
    assert hexcode.startswith("#")


def test_css_snippet_format():
    snippet = css_snippet("#595959", 7.0, (255, 255, 255))
    assert snippet == "color: #595959; /* 7.0:1 on #FFFFFF */"


def test_css_snippet_rounds_ratio_to_one_decimal():
    snippet = css_snippet("#595959", 7.041, (0, 0, 0))
    assert "7.0:1" in snippet
    assert "#000000" in snippet


def test_hex_to_rgb_roundtrip():
    assert hex_to_rgb("#595959") == (0x59, 0x59, 0x59)
    assert hex_to_rgb("000000") == (0, 0, 0)
