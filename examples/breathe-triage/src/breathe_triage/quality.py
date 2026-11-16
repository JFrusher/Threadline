"""Tap-quality model (ARCH-003, class B). Can only add a recount prompt; never changes a classification."""

import json
import math
import statistics
from pathlib import Path

WEIGHTS = Path(__file__).parents[2] / "model" / "tap-quality.json"
THRESHOLD = 0.5


def features(taps: list[float]) -> tuple[float, float]:
    """(coefficient of variation of inter-tap intervals, longest interval / median interval)."""
    gaps = [b - a for a, b in zip(taps, taps[1:], strict=False)]
    if len(gaps) < 2:
        raise ValueError("need at least 3 taps")
    return statistics.pstdev(gaps) / statistics.mean(gaps), max(gaps) / statistics.median(gaps)


def irregular_probability(cv: float, ratio: float, weights: list[float]) -> float:
    return 1 / (1 + math.exp(-(weights[0] + weights[1] * cv + weights[2] * ratio)))


def needs_recount(taps: list[float]) -> bool:
    weights = json.loads(WEIGHTS.read_text())["weights"]
    return irregular_probability(*features(taps), weights) >= THRESHOLD
