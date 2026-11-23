# Rules

Threadline has 32 rules. Each cites the clause it enforces, and each has a passing and a failing fixture in
[`tests/fixtures/`](../../tests/fixtures), named after the rule. Those fixtures are the clearest specification of
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
| TL-D04 | 21 CFR 11.100, 11.300; ADR-003 | Every change to the signer registry after its first commit (or after the trust root) is signed by a previously registered QA signer, and nothing is uncommitted. (Needs a git work tree.) | Have a QA signer make registry changes in a signed commit. Lost the only QA key? See [Releasing](../guides/releasing.md#lost-keys). |
| TL-D05 | ISO 13485 7.3.4, 7.3.10; IEC 62304 5.8 | An effective baseline for this release exists and still matches the design file. (Needs `--release`.) | Run `threadline baseline V`, commit, approve as `released`. If the design file changed after, make a new baseline. |

## Lifecycle and regulatory profiles

| Rule | Clause | What it checks | How to fix |
|---|---|---|---|
| TL-C01 | IEC 62304 (per lifecycle profile) | Every activity your software class requires has its deliverable: an item type, a document type, or a named document. | Create what the message names (for example a document with `doc_type: sdp`). |
| TL-G01 | ISO 13485 4.2.3; UK MDR 2002 Part II; AU Model Law | Every checklist clause of the active profiles has a `requirement` item with evidence, or `applicable: false` with a justification. | Fill `evidence:` in the stub `init` created, or justify non-applicability. |
| TL-G02 | UK MDR 2002 reg. 7 / Annex IX; WHO GMRF | Every classification scheme the active profiles need has a `classification` item. | Add a `classification` with `scheme`, `result`, `rule` and `rationale`. |

## Adding a rule

A rule is a decorated function in `src/threadline/checks/` that yields `Finding`s. It isn't finished until it has a
passing and a failing fixture in `tests/fixtures/<RULE-ID>.yaml` and the README table is regenerated. See
[CONTRIBUTING.md](../../CONTRIBUTING.md).
