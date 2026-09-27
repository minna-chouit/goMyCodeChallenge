from seeall.filter_issues import filter_groups


def _g(severity="critical", source="measured"):
    return {"severity": severity, "source": source}


def test_all_returns_everything():
    groups = [_g("critical"), _g("minor", source="ai")]
    assert filter_groups(groups, "all") == groups


def test_critical_only_filters_by_severity():
    groups = [_g("critical"), _g("minor")]
    result = filter_groups(groups, "critical")
    assert len(result) == 1 and result[0]["severity"] == "critical"


def test_measured_only_filters_by_source():
    groups = [_g(source="measured"), _g(source="ai")]
    result = filter_groups(groups, "measured")
    assert len(result) == 1 and result[0]["source"] == "measured"


def test_ai_only_filters_by_source():
    groups = [_g(source="measured"), _g(source="ai"), _g(source="ai+measured")]
    result = filter_groups(groups, "ai")
    assert all("ai" in g["source"] for g in result)
    assert len(result) == 2


def test_unknown_mode_returns_all():
    groups = [_g()]
    assert filter_groups(groups, "nonsense") == groups
