"""Train MODEL-001: logistic regression by batch gradient descent. Deterministic, stdlib only."""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))
from breathe_triage.quality import THRESHOLD, irregular_probability  # noqa: E402

HYPER = {"learning_rate": 0.5, "epochs": 3000}


def load(path):
    with open(path) as f:
        rows = list(csv.DictReader(f))
    return [(row["age_band"], float(row["cv"]), float(row["gap_ratio"]), int(row["irregular"])) for row in rows]


def predict(w, cv, ratio):
    return irregular_probability(cv, ratio, w)


def train(rows):
    w = [0.0, 0.0, 0.0]
    for _ in range(HYPER["epochs"]):
        g = [0.0, 0.0, 0.0]
        for _, cv, ratio, y in rows:
            err = predict(w, cv, ratio) - y
            g = [g[0] + err, g[1] + err * cv, g[2] + err * ratio]
        w = [wi - HYPER["learning_rate"] * gi / len(rows) for wi, gi in zip(w, g, strict=True)]
    return [round(x, 6) for x in w]


def metrics(w, rows):
    def sens_spec(rs):
        tp = sum(1 for _, c, r, y in rs if y and predict(w, c, r) >= THRESHOLD)
        tn = sum(1 for _, c, r, y in rs if not y and predict(w, c, r) < THRESHOLD)
        pos = sum(1 for *_, y in rs if y)
        return {"sensitivity": round(tp / pos, 3), "specificity": round(tn / (len(rs) - pos), 3)}

    return sens_spec(rows), {b: sens_spec([r for r in rows if r[0] == b]) for b in ("infant", "child")}


if __name__ == "__main__":
    w = train(load(ROOT / "data" / "taps-train.csv"))
    (ROOT / "model" / "tap-quality.json").write_text(json.dumps({"weights": w}) + "\n")
    print(json.dumps(metrics(w, load(ROOT / "data" / "taps-test.csv"))))
