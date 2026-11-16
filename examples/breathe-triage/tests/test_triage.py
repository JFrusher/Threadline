import ast
import pathlib

import pytest
from breathe_triage.triage import (
    ACTIONS,
    DANGER_SIGNS,
    Count,
    ImplausibleRate,
    IncompleteCount,
    OutOfScope,
    classify,
)

NONE = {s: False for s in DANGER_SIGNS}


@pytest.mark.verifies("SRS-001", "RC-002")
@pytest.mark.parametrize("age", [0, 1, 60, 72])
def test_out_of_scope_ages_refused(age):
    with pytest.raises(OutOfScope):
        classify(age, 30, NONE)


@pytest.mark.verifies("SRS-002", "RC-001")
@pytest.mark.parametrize("age,rate,expected", [
    (2, 49, "NO_FAST_BREATHING"), (2, 50, "FAST_BREATHING"),
    (11, 49, "NO_FAST_BREATHING"), (11, 50, "FAST_BREATHING"),
])
def test_infant_threshold(age, rate, expected):
    assert classify(age, rate, NONE) == expected


@pytest.mark.verifies("SRS-003", "RC-001")
@pytest.mark.parametrize("age,rate,expected", [
    (12, 39, "NO_FAST_BREATHING"), (12, 40, "FAST_BREATHING"),
    (59, 39, "NO_FAST_BREATHING"), (59, 40, "FAST_BREATHING"),
])
def test_child_threshold(age, rate, expected):
    assert classify(age, rate, NONE) == expected


@pytest.mark.verifies("SRS-004", "RC-004")
@pytest.mark.parametrize("sign", DANGER_SIGNS)
def test_danger_sign_overrides(sign):
    assert classify(30, 20, NONE | {sign: True}) == "REFER_URGENTLY"


@pytest.mark.verifies("SRS-005")
def test_danger_sign_list_is_complete():
    assert DANGER_SIGNS == (
        "unable_to_drink", "vomits_everything", "convulsions", "lethargic_or_unconscious", "stridor",
    )
    with pytest.raises(ValueError):
        classify(30, 30, {"convulsions": False})


@pytest.mark.verifies("SRS-006", "RC-003")
@pytest.mark.parametrize("rate,ok", [(9, False), (10, True), (120, True), (121, False)])
def test_plausible_range(rate, ok):
    if ok:
        classify(30, rate, NONE)
    else:
        with pytest.raises(ImplausibleRate):
            classify(30, rate, NONE)


@pytest.mark.verifies("SRS-007", "RC-005")
def test_incomplete_count_rejected():
    with pytest.raises(IncompleteCount):
        Count(taps=[1.0, 2.0], duration=59.9).rate()


@pytest.mark.verifies("SRS-008")
def test_rate_counts_taps_in_window():
    assert Count(taps=[0.0, 30.0, 59.9, 60.0, 61.0], duration=62.0).rate() == 3


@pytest.mark.verifies("SRS-009")
def test_classification_set():
    seen = {classify(a, r, NONE | d) for a in (6, 30) for r in (20, 60) for d in ({}, {"stridor": True})}
    assert seen == set(ACTIONS)


@pytest.mark.verifies("SRS-010")
def test_every_classification_has_action():
    assert all(isinstance(v, str) and v for v in ACTIONS.values())


@pytest.mark.verifies("SRS-011")
def test_no_network_imports():
    banned = {"socket", "http", "urllib", "requests", "httpx", "ssl"}
    for path in pathlib.Path(__file__).parents[1].joinpath("src").rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            names = [a.name for a in getattr(node, "names", [])] + [getattr(node, "module", None) or ""]
            assert not {n.split(".")[0] for n in names} & banned, path


@pytest.mark.verifies("SRS-012", "RC-006")
@pytest.mark.parametrize("age,text", [(3, "0 years 3 months"), (36, "3 years 0 months"), (59, "4 years 11 months")])
def test_age_readback(age, text):
    from breathe_triage.triage import age_readback
    assert age_readback(age) == text


@pytest.mark.verifies("SRS-013", "RC-007")
def test_result_contrast_meets_aaa():
    from breathe_triage.triage import RESULT_COLOURS, contrast_ratio
    assert set(RESULT_COLOURS) == set(ACTIONS)
    assert contrast_ratio("#FFFFFF", "#000000") == pytest.approx(21.0)
    for fg, bg in RESULT_COLOURS.values():
        assert contrast_ratio(fg, bg) >= 7.0, (fg, bg)


@pytest.mark.verifies("RC-008")
@pytest.mark.parametrize("missing", DANGER_SIGNS)
def test_every_danger_sign_must_be_answered(missing):
    answers = {s: False for s in DANGER_SIGNS if s != missing}
    with pytest.raises(ValueError):
        classify(30, 30, answers)
