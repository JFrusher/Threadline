# Threadline

QMS-as-code for Software as a Medical Device (SaMD).

Regulatory artifacts live in git as one YAML file per item. The `threadline` CLI and GitHub Action check the
digital thread — user need → requirement → risk control → passing test → signed release — and compile an
audit-ready technical file.

Target markets: **UK (MHRA)** and **Africa (AU Model Law on Medical Products Regulation / WHO GMRF baseline)**.

> **Disclaimer.** Threadline is not a certified quality management system and does not make any device
> compliant. It is tooling that a manufacturer's QMS may adopt, and the manufacturer must validate it for
> its own intended use (ISO 13485:2016 §4.1.6). The example device in `examples/` is fictional; its
> clinical and usability data are illustrative only.

## Quickstart

```bash
pip install threadline   # or: pip install git+https://github.com/JFrusher/threadline
threadline init my-qms && cd my-qms && git init
pytest --junitxml=junit.xml
threadline check --junit junit.xml          # red until your design file is complete
```

| Command | What it does |
|---|---|
| `threadline init <dir>` | New QMS repo: SOPs, workflows, PR template, CODEOWNERS, editor schema |
| `threadline check [root] --junit J --sbom S --osv --base REF --trust-root C [--release V] [--format github]` | Run every rule; exit 1 on any finding; per-rule summary; inline PR annotations |
| `threadline rtm [root] --junit J` | Print the requirements traceability matrix |
| `threadline build [root] --junit J --sbom S --osv --tool-validation T --release V` | Technical file PDF + DCB0129 hazard log (refuses on findings; `--release` also refuses skipped rules) |
| `threadline approve ID... --meaning M --signer S` | Write approval records and commit them in one SSH-signed commit |
| `threadline baseline V` | Freeze the design file for release V (then `approve BL-V --meaning released`) |
| `threadline preset add <name>` | Add `power-loss`, `offline-queue`, `low-bandwidth-telemetry` or `ml-34971` |
| `threadline hash <file>` | Content hash to sign a document, or SHA-256 of a dataset / weights file |

Releasing: `threadline baseline v1.2.0`, commit, `threadline approve BL-v1.2.0 --meaning released --signer <you>`,
then tag `v1.2.0`. The release workflow rebuilds the evidence on the tag and refuses if anything changed.

Trust: set the repository variable `THREADLINE_TRUST_ROOT` to the commit that created your signer registry. Signer
changes after it must be SSH-signed by an existing QA signer; releases refuse to build without it.

Link tests to items with `@pytest.mark.verifies("SRS-001", "RC-002")` and set `junit_family = xunit1`
(ADR-002). Sign approvals with SSH-signed commits (ADR-003, `docs/guides/branch-protection.md`).

## Rules

Every rule has a passing and a failing fixture in `tests/fixtures/`. That suite is Threadline's tool-validation
evidence and ships with each release.

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

`examples/breathe-triage/` is a fictional IEC 62304 class C SaMD for community health workers: requirements,
risk, usability file, threat model, ML model with dataset hashes, clause maps for ISO 13485 / UK MDR 2002 /
AU Model Law, SOPs with signed approvals. Tag `example-vX` to publish its technical file.

## Status and limits

Pre-1.0. See [docs/PRD.md](docs/PRD.md) §11 for what is verified and what is not, and
[docs/guides/part11-gap-analysis.md](docs/guides/part11-gap-analysis.md) for signature gaps.

## Licences

- Code (`src/threadline/*.py`, `tests/`, workflows): [Apache-2.0](LICENSES/Apache-2.0.txt)
- Templates, SOPs, presets, example DHF and docs (`src/threadline/template/`, `src/threadline/data/`,
  `examples/`, `docs/`): [CC-BY-4.0](LICENSES/CC-BY-4.0.txt)
