from seeall.scale_detect import detect_scale


def test_narrow_phone_width_detected_as_1x():
    d = detect_scale(383)
    assert d.scale == 1
    assert d.confident is True
    assert "phone" in d.label
    assert "383" in d.label


def test_under_500_boundary_is_1x():
    d = detect_scale(499)
    assert d.scale == 1
    assert d.confident is True


def test_common_2x_width_750():
    d = detect_scale(750)
    assert d.scale == 2
    assert d.confident is True


def test_common_2x_width_828():
    d = detect_scale(828)
    assert d.scale == 2
    assert d.confident is True


def test_common_3x_width_1080():
    d = detect_scale(1080)
    assert d.scale == 3
    assert d.confident is True


def test_common_3x_width_1284():
    d = detect_scale(1284)
    assert d.scale == 3
    assert d.confident is True


def test_desktop_width_over_1300_is_1x():
    d = detect_scale(1512)
    assert d.scale == 1
    assert d.confident is True
    assert "desktop" in d.label


def test_boundary_1300_is_desktop_1x():
    d = detect_scale(1301)
    assert d.scale == 1
    assert d.confident is True


def test_unknown_width_in_phone_range_is_uncertain():
    d = detect_scale(900)
    assert d.confident is False
    assert d.scale in (1, 2, 3)


def test_unknown_narrow_gap_width_is_uncertain():
    d = detect_scale(600)
    assert d.confident is False


def test_label_format_matches_plan_example():
    d = detect_scale(383)
    assert d.label == "phone, 383 px"
