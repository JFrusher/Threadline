# Rule reference

`threadline check` runs every rule below and exits 1 if any of them reports a finding. `threadline build`
runs the same rules and refuses to produce a technical file while any finding remains.

A finding is printed as:

```text
TL-R04 [ISO 14971 7.2] RC-004: no passing test verifies this risk control
```

That is the rule ID, the clause it enforces, the item at fault and the reason.

## Rules that need extra input

Some rules cannot run without data that only a flag provides. When the data is absent the rule is skipped,
and the skip is printed, so a green run never hides a rule that did not execute. `build --release` refuses to
run if any rule other than TL-D02 would be skipped.

| Needs | Provided by |
|---|---|
| `evidence` | `--junit <file>` |
| `sbom` | `--sbom <file>` (CycloneDX JSON, for example from Syft) |
| `advisories` | `--sbom <file> --osv` (queries OSV.dev) |
| `base_ref` | `--base <git ref>`, for example `origin/main` |
| `release` | `--release <version>`; the version must have an approved baseline |
| `git_root` | Running inside a git work tree |

## All rules

This table is generated from the rule registry by `threadline.rules.rule_table()`.
`tests/test_readme.py` fails if it is out of date.

| Rule | Clause | Check | Needs |
|---|---|---|---|
| TL-C01 | IEC 62304 (per lifecycle profile) | Every activity the software class requires has its deliverable |  |
| TL-D01 | ISO 13485 4.2.4, 7.3.4; 21 CFR 11.50, 11.70 | Effective documents and baselines carry the required approvals: right role, independent, bound to content |  |
| TL-D02 | ISO 13485 4.2.4 | A content change to an effective document comes with a revision bump | base_ref |
| TL-D03 | 21 CFR 11.70, 11.100; ADR-003 | Every approval was committed once, SSH-signed by its signer with a key registered before that commit | git_root |
| TL-D04 | 21 CFR 11.100, 11.300; ADR-003 | After its first commit, every change to the signer registry is SSH-signed by a QA signer it already trusted | git_root |
| TL-D05 | ISO 13485 7.3.4, 7.3.10; IEC 62304 5.8 | The release has an effective baseline matching the current design file, approved as released | release |
| TL-E01 | IEC 62304 5.7 | Every software requirement has tests and all of them pass | evidence |
| TL-E02 | IEC 62304 5.7.5 | No test claims to verify an unknown item | evidence |
| TL-G01 | ISO 13485 4.2.3; UK MDR 2002 Part II; AU Model Law | Every checklist clause of the active profiles is mapped to evidence or justified as not applicable |  |
| TL-G02 | UK MDR 2002 reg. 7 / Annex IX; WHO GMRF classification | Every classification scheme the active profiles need has a classification item |  |
| TL-L01 | IEC 62304 5.1.1 | Every link points at an existing item of an allowed type |  |
| TL-L02 | IEC 62304 5.2 | Every software requirement traces to a system requirement or risk control |  |
| TL-L03 | ISO 13485 7.3.3 | Every system requirement traces to a user need |  |
| TL-L04 | ISO 13485 7.3.10 | The trace graph has no cycles |  |
| TL-L05 | ISO 13485 4.2.4, 7.3.9 | No live item links to an obsolete item |  |
| TL-M01 | BS/AAMI 34971 (data, bias); IEC 62304 8.1 | Every model records datasets, weights hash, metrics, subgroup metrics and acceptance criteria |  |
| TL-M02 | IEC 62304 8.1.2, 8.2 | Model weights and dataset files match their registered SHA-256 |  |
| TL-P01 | IEC 62304 7.1.2, 8.1.2 | Every SBOM component has an effective SOUP entry for that version | sbom |
| TL-P02 | IEC 62304 8.1.2 | Every SOUP entry matches a component in the SBOM | sbom |
| TL-P03 | IEC 81001-5-1 5.7, 6.1 | Every known advisory against a SOUP has a vulnerability triage record | advisories |
| TL-R01 | ISO 14971 5.4, 5.5 | Every hazard has situation, harm and estimated severity, P1, P2 |  |
| TL-R02 | ISO 14971 7.1 | Every hazard with unacceptable initial risk has a risk control |  |
| TL-R03 | ISO 14971 7.2 | Every design/protective risk control is implemented by a software requirement |  |
| TL-R04 | ISO 14971 7.2 | Every risk control has tests and all of them pass | evidence |
| TL-R05 | ISO 14971 7.3, 7.4 | Residual risk is evaluated and acceptable, or benefit-risk is justified |  |
| TL-R06 | ISO 14971 7.5 | Every risk control is reviewed for new hazards it introduces |  |
| TL-S01 | ISO 13485 4.2.4 | Every item file is valid, its type is known and its filename is its ID |  |
| TL-T01 | IEC 81001-5-1 5.2, 7.2 | Every threat is assessed |  |
| TL-T02 | IEC 81001-5-1 5.2, 7.3 | Every threat has a security risk control |  |
| TL-U01 | IEC 62366-1 5.4, 5.5 | Every hazard-related use scenario names its hazards and user groups |  |
| TL-U02 | IEC 62366-1 5.7.1 | A summative protocol covers every hazard-related use scenario |  |
| TL-U03 | IEC 62366-1 5.7.3 | Every summative protocol has a report with a result for each of its scenarios |  |

## Rule families

| Prefix | Area | Source file |
|---|---|---|
| TL-S, TL-L | File validity and trace links | [`checks/structure.py`](../src/threadline/checks/structure.py) |
| TL-E | Verification evidence | [`checks/evidence.py`](../src/threadline/checks/evidence.py) |
| TL-R | Risk management | [`checks/risk.py`](../src/threadline/checks/risk.py) |
| TL-D | Document control and signatures | [`checks/documents.py`](../src/threadline/checks/documents.py) |
| TL-C | Lifecycle deliverables | [`checks/lifecycle.py`](../src/threadline/checks/lifecycle.py) |
| TL-P | SOUP and vulnerabilities | [`checks/soup.py`](../src/threadline/checks/soup.py) |
| TL-U | Usability | [`checks/usability.py`](../src/threadline/checks/usability.py) |
| TL-T | Security threats | [`checks/security.py`](../src/threadline/checks/security.py) |
| TL-M | AI/ML | [`checks/ml.py`](../src/threadline/checks/ml.py) |
| TL-G | Regulatory profiles | [`checks/regulatory.py`](../src/threadline/checks/regulatory.py) |

## Fixtures

Each rule has a file in [`tests/fixtures`](../tests/fixtures) named after it, holding a `pass` project and a
`fail` project. [`tests/test_rules.py`](../tests/test_rules.py) asserts that the first produces no finding
for that rule and the second produces at least one. This suite is the tool's validation evidence
([intended use and risk assessment](tool-validation/threadline-intended-use-and-risk.md)).
