from seeall.link_purpose import is_vague_link_text, find_vague_links, vague_link_issues


def test_exact_click_here():
    assert is_vague_link_text("Click here") is True


def test_ocr_merged_text_with_click_here_substring():
    assert is_vague_link_text("Have a coupon?Clickhere") is True


def test_standalone_here_is_vague():
    assert is_vague_link_text("here") is True


def test_standalone_more_is_vague():
    assert is_vague_link_text("More") is True


def test_here_as_substring_of_real_word_is_not_flagged():
    assert is_vague_link_text("Adhere to policy") is False


def test_more_as_substring_of_real_word_is_not_flagged():
    assert is_vague_link_text("Moreover, read the terms") is False


def test_learn_more_is_vague():
    assert is_vague_link_text("Learn More") is True


def test_french_phrases_are_vague():
    assert is_vague_link_text("En savoir plus") is True
    assert is_vague_link_text("Cliquez ici") is True


def test_arabic_phrases_are_vague():
    assert is_vague_link_text("اضغط هنا") is True
    assert is_vague_link_text("اقرأ المزيد") is True


def test_descriptive_link_text_is_not_vague():
    assert is_vague_link_text("Return to cart") is False
    assert is_vague_link_text("View shipping policy") is False


def test_find_vague_links_filters_findings():
    findings = [{"text": "Return to cart"}, {"text": "Click here"}]
    result = find_vague_links(findings)
    assert len(result) == 1
    assert result[0]["text"] == "Click here"


def test_vague_link_issues_builds_schema():
    findings = [{"text": "Click here", "box_px": (10, 10, 60, 30)}]
    issues = vague_link_issues(findings, (100, 100))
    assert len(issues) == 1
    issue = issues[0]
    assert issue["type"] == "link_purpose"
    assert issue["severity"] == "serious"
    assert issue["source"] == "measured"
    assert issue["box"] == [0.1, 0.1, 0.6, 0.3]


def test_vague_link_issues_skips_descriptive_text():
    findings = [{"text": "Return to cart", "box_px": (10, 10, 60, 30)}]
    assert vague_link_issues(findings, (100, 100)) == []
