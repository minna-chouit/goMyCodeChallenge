from seeall.demo_picker import pick_example_image


def test_prefers_grey_on_white_when_present():
    names = ["clean_1.png", "grey_on_white.png", "tiny_text.png"]
    assert pick_example_image(names) == "grey_on_white.png"


def test_falls_back_to_first_when_preferred_missing():
    names = ["clean_1.png", "clean_2.png"]
    assert pick_example_image(names) == "clean_1.png"


def test_returns_none_for_empty_list():
    assert pick_example_image([]) is None
