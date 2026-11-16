import csv
import json
from pathlib import Path

import pytest
from breathe_triage.quality import WEIGHTS, irregular_probability, needs_recount

ROOT = Path(__file__).parents[1]


@pytest.mark.verifies("SRS-015")
def test_recount_prompted_for_irregular_taps():
    regular = [i * 1.5 for i in range(1, 40)]
    irregular = [1.5, 3.0, 3.3, 6.5, 8.0, 8.2, 12.0, 13.5, 15.0, 15.2, 19.0, 20.5]
    assert needs_recount(regular) is False
    assert needs_recount(irregular) is True


@pytest.mark.verifies("SRS-016", "RC-011")
@pytest.mark.parametrize("band", ["infant", "child"])
def test_subgroup_performance_on_test_split(band):
    weights = json.loads(WEIGHTS.read_text())["weights"]
    with open(ROOT / "data" / "taps-test.csv") as f:
        rows = [r for r in csv.DictReader(f) if r["age_band"] == band]
    pred = [(irregular_probability(float(r["cv"]), float(r["gap_ratio"]), weights) >= 0.5, r["irregular"] == "1")
            for r in rows]
    tp = sum(p and y for p, y in pred)
    tn = sum(not p and not y for p, y in pred)
    pos = sum(y for _, y in pred)
    assert tp / pos >= 0.95
    assert tn / (len(pred) - pos) >= 0.90
