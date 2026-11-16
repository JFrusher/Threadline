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


# Result colours (foreground, background) as sRGB hex; SRS-013 requires contrast >= 7:1 in sunlight.
RESULT_COLOURS = {
    "REFER_URGENTLY": ("#FFFFFF", "#8B0000"),
    "FAST_BREATHING": ("#000000", "#FFD700"),
    "NO_FAST_BREATHING": ("#FFFFFF", "#004D00"),
}


def contrast_ratio(fg: str, bg: str) -> float:
    """WCAG 2.x contrast ratio between two sRGB hex colours."""

    def luminance(hex_: str) -> float:
        rgb = [int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

    hi, lo = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def age_readback(age_months: int) -> str:
    years, months = divmod(age_months, 12)
    return f"{years} years {months} months"
