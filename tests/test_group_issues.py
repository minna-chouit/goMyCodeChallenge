from seeall.group_issues import group_issues


def _issue(type_, severity="critical", source="measured", fix="Fix A", confidence=1.0):
    return {
        "type": type_, "severity": severity, "box": [0, 0, 0.1, 0.1], "box_px": (0, 0, 10, 10),
        "description": f"{type_} problem", "affected_users": "Some users", "fix": fix,
        "confidence": confidence, "source": source,
    }


def test_same_type_issues_group_into_one():
    issues = [_issue("contrast"), _issue("contrast"), _issue("contrast")]
    groups = group_issues(issues)
    assert len(groups) == 1
    assert len(groups[0]["instances"]) == 3
    assert groups[0]["wcag_id"] == "1.4.3"
    assert groups[0]["level"] == "AA"


def test_different_types_stay_separate():
    issues = [_issue("contrast"), _issue("small_target")]
    groups = group_issues(issues)
    assert len(groups) == 2


def test_group_severity_is_most_severe_in_group():
    issues = [_issue("contrast", severity="minor"), _issue("contrast", severity="critical")]
    groups = group_issues(issues)
    assert groups[0]["severity"] == "critical"


def test_group_combines_measured_and_ai_sources():
    issues = [_issue("small_target", source="measured"), _issue("small_target", source="ai")]
    groups = group_issues(issues)
    assert groups[0]["source"] == "ai+measured"


def test_group_has_full_display_fields():
    groups = group_issues([_issue("missing_label")])
    g = groups[0]
    for field in ("wcag_id", "wcag_name", "level", "principle", "plain_title",
                  "who_is_affected", "why_it_matters", "fix", "instances", "severity", "type"):
        assert field in g
    assert len(g["instances"]) == 1
    assert "box" in g["instances"][0]


def test_empty_input_gives_empty_output():
    assert group_issues([]) == []
