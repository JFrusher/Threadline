"""Generate the SYNTHETIC tap dataset (DS-001). Deterministic: seed 2026."""

import csv
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from breathe_triage.quality import features  # noqa: E402

rng = random.Random(2026)


def sample(band: str, irregular: bool) -> list[float]:
    rate = rng.uniform(30, 70) if band == "infant" else rng.uniform(20, 50)
    period, jitter = 60 / rate, 0.05
    taps, t = [], 0.0
    while t < 60:
        step = period * rng.gauss(1, jitter)
        if irregular and rng.random() < 0.15:
            step *= rng.choice([0.3, 2.0])  # double tap or missed breath
        t += max(step, 0.05)
        taps.append(round(t, 3))
    return taps


def write(path: Path, n: int):
    with open(path, "w", newline="") as f:
        out = csv.writer(f)
        out.writerow(["age_band", "cv", "gap_ratio", "irregular"])
        for i in range(n):
            band, irregular = ("infant", "child")[i % 2], (i // 2) % 2 == 1
            cv, ratio = features(sample(band, irregular))
            out.writerow([band, f"{cv:.6f}", f"{ratio:.6f}", int(irregular)])


if __name__ == "__main__":
    root = Path(__file__).parents[1] / "data"
    write(root / "taps-train.csv", 400)
    write(root / "taps-test.csv", 200)
