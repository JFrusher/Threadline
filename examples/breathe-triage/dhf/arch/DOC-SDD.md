---
id: DOC-SDD
type: document
doc_type: detailed_design
title: Software Detailed Design
rev: 2
status: effective
---
# Software Detailed Design — class C units

## Unit `classify` (ARCH-001)
Inputs: `age_months: int`, `respiratory_rate: int`, `danger_signs: dict[str, bool]`.
Order of checks (order is safety-relevant):
1. Age in [2, 60) else `OutOfScope` (RC-002).
2. `danger_signs` keys equal `DANGER_SIGNS` exactly else `ValueError` (RC-008).
3. Rate in [10, 120] else `ImplausibleRate` (RC-003).
4. Any danger sign → `REFER_URGENTLY` (RC-004) — evaluated **before** the rate threshold.
5. Threshold 50 if age < 12 else 40; rate ≥ threshold → `FAST_BREATHING` else `NO_FAST_BREATHING` (RC-001).

No state, no I/O, standard library only.

## Unit `Count.rate` (ARCH-002)
Raises `IncompleteCount` if `duration < 60.0` (RC-005); counts taps with `0 <= t < 60`.

## Interfaces
Both units raise exceptions for every refusal; the UI shell must show a recount or refer message for each exception
type and must never display a classification after an exception.
