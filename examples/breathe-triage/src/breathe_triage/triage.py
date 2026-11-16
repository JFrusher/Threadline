"""Classification logic. Thresholds: WHO Bulletin 2003 (scielosp.org/pdf/bwho/2003.v81n4/298-300/en)."""

from dataclasses import dataclass

DANGER_SIGNS = ("unable_to_drink", "vomits_everything", "convulsions", "lethargic_or_unconscious", "stridor")
COUNT_SECONDS = 60.0

ACTIONS = {
    "REFER_URGENTLY": "Danger sign. Refer to the health facility now.",
    "FAST_BREATHING": "Fast breathing. Treat per your local protocol and follow up.",
    "NO_FAST_BREATHING": "No fast breathing. Advise home care and return if worse.",
}


class OutOfScope(ValueError):
    """Child outside 2–59 months: not for this device, refer."""


class ImplausibleRate(ValueError):
    """Respiratory rate outside 10–120: recount."""


class IncompleteCount(ValueError):
    """Count shorter than 60 seconds: recount."""


@dataclass(frozen=True)
class Count:
    taps: list[float]  # seconds since start, one per breath
    duration: float  # seconds the count ran

    def rate(self) -> int:
        if self.duration < COUNT_SECONDS:
            raise IncompleteCount(f"count ran {self.duration:.1f}s, need {COUNT_SECONDS:.0f}s")
        return sum(1 for t in self.taps if 0 <= t < COUNT_SECONDS)


def classify(age_months: int, respiratory_rate: int, danger_signs: dict[str, bool]) -> str:
    if not 2 <= age_months < 60:
        raise OutOfScope(f"age {age_months} months is outside 2–59 months")
    if set(danger_signs) != set(DANGER_SIGNS):
        raise ValueError(f"danger_signs must answer exactly {DANGER_SIGNS}")
    if not 10 <= respiratory_rate <= 120:
        raise ImplausibleRate(f"rate {respiratory_rate} is implausible")
    if any(danger_signs.values()):
        return "REFER_URGENTLY"
    threshold = 50 if age_months < 12 else 40
    return "FAST_BREATHING" if respiratory_rate >= threshold else "NO_FAST_BREATHING"
