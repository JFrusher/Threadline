# Rules

Threadline has 32 rules. Each cites the clause it enforces, and each has a passing and a failing fixture in
[`tests/fixtures/`](../tests/fixtures), named after the rule. Those fixtures are the clearest specification of
what a rule accepts and rejects.

A finding looks like this:

```text
TL-R04 [ISO 14971 7.2] RC-001: failing verification: tests.test_triage::test_infant_threshold[2-50-FAST_BREATHING]
```

Rule, clause, the item it's about, and what's wrong. Rules marked with an input below are skipped without it; see
[CLI reference](cli.md#shared-options-check-rtm-build).

## Structure and links

| Rule | Clause | What it checks | How to fix |
|---|---|---|---|
| TL-S01 | ISO 13485 4.2.4 | Every item file parses, has a known `type`, only known fields, and its `id` equals its filename. | Read the message: it names the file and the field. Rename the file or fix the `id`. |
| TL-L01 | IEC 62304 5.1.1 | Every link points at an item that exists and has an allowed type. | Fix the ID, or create the missing item. [Item types](items.md) lists allowed targets. |
| TL-L02 | IEC 62304 5.2 | Every software requirement derives from a system requirement or implements a risk control. | Add `derives_from: [SYS-…]` or `implements: [RC-…]`. |
| TL-L03 | ISO 13485 7.3.3 | Every system requirement derives from a user need. | Add `derives_from: [UN-…]`. |
| TL-L04 | ISO 13485 7.3.10 | The trace graph has no cycles. | Remove the link that points back down the chain. |
| TL-L05 | ISO 13485 4.2.4, 7.3.9 | No live item links to an obsolete one. | Relink to the replacement, or make the linking item obsolete too. |

## Verification evidence (needs `--junit`)

| Rule | Clause | What it checks | How to fix |
|---|---|---|---|
| TL-E01 | IEC 62304 5.7 | Every live software requirement has at least one test, and all its tests pass. | Add `@pytest.mark.verifies("SRS-…")` to a test, or fix the failing test. Skipped tests count as not passed. |
| TL-E02 | IEC 62304 5.7.5 | No test claims to verify an ID that doesn't exist. | Fix the ID in the marker, or create the item. |

## Risk management (ISO 14971)

| Rule | Clause | What it checks | How to fix |
|---|---|---|---|
| TL-R01 | 5.4, 5.5 | Every hazard has `hazard`, `hazardous_situation`, `harm`, `severity`, `p1`, `p2`, using levels from your risk policy. | Fill in the missing fields with levels from `threadline.yaml` `risk:`. |
| TL-R02 | 7.1 | A hazard whose initial risk is unacceptable has at least one risk control. | Add `controls: [RC-…]`. |
| TL-R03 | 7.2 | Every design or protective risk control is implemented by a software requirement. (`information_for_safety` controls are exempt.) | Add `implements: [RC-…]` to a software requirement. |
| TL-R04 | 7.2 | Every live risk control has tests, and all of them pass. (Needs `--junit`.) | Add the control's ID to a test's `verifies` marker. |
| TL-R05 | 7.3, 7.4 | A controlled hazard has a `residual` estimate that is acceptable, or a `benefit_risk` justification. | Add `residual: {p1: …, p2: …}` (and `severity` if it changed), or justify with `benefit_risk`. |
| TL-R06 | 7.5 | Every risk control records a review for new hazards it introduces. | Add `new_risk_review:` and, if needed, `new_hazards: [HAZ-…]`. |

## Usability (IEC 62366-1)

| Rule | Clause | What it checks | How to fix |
|---|---|---|---|
| TL-U01 | 5.4, 5.5 | Every hazard-related use scenario names its hazards and user groups. | Add `hazards:` and `user_groups:`, or set `hazard_related: false`. |
| TL-U02 | 5.7.1 | A summative protocol covers every hazard-related use scenario. | List the scenario in a `summative_protocol`'s `scenarios:`. |
| TL-U03 | 5.7.3 | Every summative protocol has a report with a result for each of its scenarios. | Add a `summative_report` whose `results:` include every scenario. |

## Security (IEC 81001-5-1)

| Rule | Clause | What it checks | How to fix |
|---|---|---|---|
| TL-T01 | 5.2, 7.2 | Every threat is assessed. | Add `assessment:`. |
| TL-T02 | 5.2, 7.3 | Every threat has a security risk control. | Add `controls: [RC-…]`. Security controls are risk controls, so TL-R04 verifies them too. |

## SOUP and SBOM

| Rule | Clause | What it checks | How to fix |
|---|---|---|---|
| TL-P01 | IEC 62304 7.1.2, 8.1.2 | Every SBOM component has an effective `soup` entry for that exact version. (Needs `--sbom`.) | Add or update the `soup` item, review it, and make it effective. |
| TL-P02 | IEC 62304 8.1.2 | Every `soup` entry matches a component in the SBOM. (Needs `--sbom`.) | Remove or obsolete the stale entry, or fix its `name`/`version`. |
| TL-P03 | IEC 81001-5-1 5.7, 6.1 | Every known advisory against a SOUP component has a `vulnerability` triage record. (Needs `--sbom --osv`.) | Add a `vulnerability` item with your exploitability, impact and decision. |

## AI/ML

| Rule | Clause | What it checks | How to fix |
|---|---|---|---|
| TL-M01 | BS/AAMI 34971; IEC 62304 8.1 | Every model records datasets, weights path and hash, metrics, subgroup metrics and acceptance criteria. | Fill in the fields the message lists. |
| TL-M02 | IEC 62304 8.1.2, 8.2 | Weights and dataset files exist inside the project and match their registered SHA-256. | Re-hash with `threadline hash <file>` if the change was intended; otherwise restore the file. |

## Documents, signatures and release

| Rule | Clause | What it checks | How to fix |
|---|---|---|---|
| TL-D01 | ISO 13485 4.2.4, 7.3.4; 21 CFR 11.50, 11.70 | Effective documents and baselines have every approval their policy needs, for the current `rev` and content, from signers with the right role; reviews and QA approvals are not by the author. | Sign with `threadline approve`. If content changed, bump `rev` and re-approve. |
| TL-D02 | ISO 13485 4.2.4 | An effective document whose body changed since the base branch has a higher `rev`. (Needs `--base`.) | Bump `rev`; then re-approve. |
| TL-D03 | 21 CFR 11.70, 11.100; ADR-003 | Each approval record was committed once, in a commit SSH-signed by its signer, with a key registered before that commit, and is unchanged since. (Needs a git work tree.) | Commit approvals with `threadline approve`. Never edit a record: write a new one. On CI, check out with `fetch-depth: 0`. |
| TL-D04 | 21 CFR 11.100, 11.300; ADR-003 | Every change to the signer registry after its first commit (or after the trust root) is signed by a previously registered QA signer, and nothing is uncommitted. (Needs a git work tree.) | Have a QA signer make registry changes in a signed commit. Lost the only QA key? See [Releasing](guides/branch-protection.md#trust-root). |
| TL-D05 | ISO 13485 7.3.4, 7.3.10; IEC 62304 5.8 | An effective baseline for this release exists and still matches the design file. (Needs `--release`.) | Run `threadline baseline V`, commit, approve as `released`. If the design file changed after, make a new baseline. |

## Lifecycle and regulatory profiles

| Rule | Clause | What it checks | How to fix |
|---|---|---|---|
| TL-C01 | IEC 62304 (per lifecycle profile) | Every activity your software class requires has its deliverable: an item type, a document type, or a named document. | Create what the message names (for example a document with `doc_type: sdp`). |
| TL-G01 | ISO 13485 4.2.3; UK MDR 2002 Part II; AU Model Law | Every checklist clause of the active profiles has a `requirement` item with evidence, or `applicable: false` with a justification. | Fill `evidence:` in the stub `init` created, or justify non-applicability. |
| TL-G02 | UK MDR 2002 reg. 7 / Annex IX; WHO GMRF | Every classification scheme the active profiles need has a `classification` item. | Add a `classification` with `scheme`, `result`, `rule` and `rationale`. |

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
