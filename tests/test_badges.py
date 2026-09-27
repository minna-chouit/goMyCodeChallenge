from seeall.badges import confidence_badge


def test_low_confidence_flags_needs_human_check():
    label = confidence_badge(0.3)
    assert "Needs human check" in label
    assert "30%" in label


def test_boundary_confidence_is_not_flagged():
    label = confidence_badge(0.5)
    assert "Needs human check" not in label
    assert "50%" in label


def test_high_confidence_label():
    label = confidence_badge(0.95)
    assert "Needs human check" not in label
    assert "95%" in label


def test_deterministic_full_confidence():
    label = confidence_badge(1.0)
    assert "100%" in label
