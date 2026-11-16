"""Read test evidence from JUnit XML (ADR-002)."""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TestCase:
    name: str
    passed: bool
    verifies: tuple[str, ...]


def parse(path: Path) -> list[TestCase]:
    cases = []
    for tc in ET.parse(path).getroot().iter("testcase"):
        verifies = tuple(
            p.get("value") for p in tc.iter("property") if p.get("name") == "verifies"
        )
        failed = any(tc.find(tag) is not None for tag in ("failure", "error", "skipped"))
        cases.append(TestCase(f"{tc.get('classname', '')}::{tc.get('name')}", not failed, verifies))
    return cases


def by_item(cases: list[TestCase]) -> dict[str, list[TestCase]]:
    out: dict[str, list[TestCase]] = {}
    for c in cases:
        for item_id in c.verifies:
            out.setdefault(item_id, []).append(c)
    return out
