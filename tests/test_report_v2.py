from seeall.report import top_fixes, verdict_sentence, group_by_principle, CANNOT_CHECK, build_html_report


def _group(severity="minor", n=1, principle="Perceivable", plain_title="Issue"):
    return {
        "severity": severity, "principle": principle, "plain_title": plain_title,
        "wcag_id": "1.4.3", "wcag_name": "Contrast (Minimum)", "level": "AA",
        "who_is_affected": "Some users", "why_it_matters": "It matters",
        "fix": "Fix it", "type": "contrast",
        "instances": [{"box_px": (0, 0, 10, 10), "confidence": 1.0} for _ in range(n)],
    }


def test_top_fixes_ranks_critical_above_minor():
    groups = [_group("minor"), _group("critical")]
    top = top_fixes(groups, n=3)
    assert top[0]["severity"] == "critical"


def test_top_fixes_respects_n():
    groups = [_group("critical"), _group("serious"), _group("minor"), _group("minor")]
    assert len(top_fixes(groups, n=3)) == 3


def test_top_fixes_many_instances_outranks_single_instance_same_severity():
    groups = [_group("serious", n=1), _group("serious", n=10)]
    top = top_fixes(groups, n=1)
    assert len(top[0]["instances"]) == 10


def test_verdict_sentence_has_content_for_each_grade():
    for grade in ("Excellent", "Good", "Needs work", "Poor"):
        assert verdict_sentence(90, grade)


def test_group_by_principle_buckets_and_orders():
    groups = [_group(principle="Operable"), _group(principle="Perceivable")]
    buckets = group_by_principle(groups)
    assert list(buckets.keys()) == ["Perceivable", "Operable"]


def test_group_by_principle_omits_empty_buckets():
    groups = [_group(principle="Perceivable")]
    buckets = group_by_principle(groups)
    assert "Operable" not in buckets


def test_cannot_check_list_is_nonempty():
    assert len(CANNOT_CHECK) >= 3


def test_html_report_contains_summary_and_top_3():
    groups = [_group("critical", plain_title="Big problem"), _group("minor", plain_title="Small problem")]
    html = build_html_report(72, groups, "NVIDIA Build", 5.0)
    assert "72" in html
    assert "Big problem" in html
    assert "Fix these" in html
    assert "cannot check" in html.lower()


def test_html_report_is_self_contained_html():
    html = build_html_report(100, [], "MOCK", 0.0)
    assert html.strip().startswith("<!DOCTYPE html>") or html.strip().startswith("<html")
    assert "<style" in html
