from seeall.scoring import compute_score, severity_breakdown, format_breakdown


def test_compute_score_unchanged_behaviour():
    issues = [{"severity": "critical"}, {"severity": "minor"}]
    assert compute_score(issues) == 100 - 15 - 3


def test_severity_breakdown_counts_each_bucket():
    issues = [
        {"severity": "critical"}, {"severity": "critical"},
        {"severity": "serious"},
        {"severity": "minor"},
    ]
    assert severity_breakdown(issues) == {"critical": 2, "serious": 1, "minor": 1}


def test_severity_breakdown_empty():
    assert severity_breakdown([]) == {"critical": 0, "serious": 0, "minor": 0}


def test_format_breakdown_skips_zero_counts():
    counts = {"critical": 1, "serious": 0, "minor": 2}
    assert format_breakdown(counts) == "1 critical, 2 minor"


def test_format_breakdown_all_zero():
    counts = {"critical": 0, "serious": 0, "minor": 0}
    assert format_breakdown(counts) == "No issues"
