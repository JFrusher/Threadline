---
id: DOC-SDP
type: document
doc_type: sdp
title: Software Development Plan
rev: 2
status: effective
---
# Software Development Plan — Breathe-Triage

| Item | Plan |
|---|---|
| Lifecycle standard | IEC 62304:2006+A1:2015 (`lifecycle_profile: iec62304-ed1`) |
| Software safety class | C (see `CLS-62304`) |
| Process | SOP-02; every change via PR with the PR template |
| Deliverables | Items in `dhf/`, SAD (`DOC-SAD`), RTM, risk management report, technical file per release |
| Verification | pytest, linked with `@pytest.mark.verifies`; boundary-value tests for every threshold |
| Integration | The assessment package is one unit; integration = classification end-to-end tests |
| Configuration management | Git; SOUP via SOP-07 and SBOM |
| Problem resolution | SOP-05 → SOP-04; problem reports as CAPA items |
| Tools | Threadline, pytest, Syft, Pandoc/LaTeX — validated per SOP-10 |
