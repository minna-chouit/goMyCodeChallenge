from seeall.scoring import compute_score_v2, level_counts, grade_label


def _group(severity="critical", n=1, source="measured", confidence=1.0, level="AA"):
    return {
        "severity": severity, "level": level,
        "instances": [{"confidence": confidence} for _ in range(n)],
        "source": source,
    }


def test_single_critical_group_deducts_base_15():
    assert compute_score_v2([_group("critical", 1)]) == 85


def test_single_serious_group_deducts_base_8():
    assert compute_score_v2([_group("serious", 1)]) == 92


def test_single_minor_group_deducts_base_3():
    assert compute_score_v2([_group("minor", 1)]) == 97


def test_many_instances_capped_at_50_percent_extra():
    # 13 instances -> extra capped at +50% of base (15 * 1.5 = 22.5)
    score_many = compute_score_v2([_group("critical", 13)])
    score_two = compute_score_v2([_group("critical", 2)])
    assert score_many <= score_two  # more instances never score better
    assert score_many == 100 - round(15 * 1.5)


def test_no_issues_scores_100():
    assert compute_score_v2([]) == 100


def test_low_confidence_pure_ai_group_counts_half():
    full = compute_score_v2([_group("critical", 1, source="ai", confidence=0.9)])
    half = compute_score_v2([_group("critical", 1, source="ai", confidence=0.3)])
    assert half > full


def test_score_never_goes_below_zero():
    groups = [_group("critical", 20) for _ in range(20)]
    assert compute_score_v2(groups) == 0


def test_level_counts_tallies_by_level():
    groups = [_group(level="A"), _group(level="A"), _group(level="AA"), _group(level="AAA")]
    assert level_counts(groups) == {"A": 2, "AA": 1, "AAA": 1}


def test_level_counts_empty():
    assert level_counts([]) == {}


def test_grade_label_thresholds():
    assert grade_label(95) == "Excellent"
    assert grade_label(90) == "Excellent"
    assert grade_label(89) == "Good"
    assert grade_label(75) == "Good"
    assert grade_label(74) == "Needs work"
    assert grade_label(50) == "Needs work"
    assert grade_label(49) == "Poor"
    assert grade_label(0) == "Poor"
