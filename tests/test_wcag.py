from seeall.wcag import criterion_for_type, CATALOG, TYPE_TO_WCAG


def test_contrast_maps_to_1_4_3():
    c = criterion_for_type("contrast")
    assert c.id == "1.4.3"
    assert c.name == "Contrast (Minimum)"
    assert c.level == "AA"
    assert c.principle == "Perceivable"


def test_small_target_maps_to_2_5_8():
    c = criterion_for_type("small_target")
    assert c.id == "2.5.8"
    assert c.level == "AA"


def test_color_only_maps_to_1_4_1():
    c = criterion_for_type("color_only")
    assert c.id == "1.4.1"


def test_unknown_type_falls_back_to_a_valid_criterion():
    c = criterion_for_type("totally_unknown_type")
    assert c.id in CATALOG


def test_every_mapped_type_resolves_to_catalog_entry():
    for issue_type, wcag_id in TYPE_TO_WCAG.items():
        assert wcag_id in CATALOG
        c = criterion_for_type(issue_type)
        assert c.id == wcag_id
        assert c.level in ("A", "AA", "AAA")
        assert c.principle in ("Perceivable", "Operable", "Understandable", "Robust")
