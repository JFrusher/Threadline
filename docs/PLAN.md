# Threadline — Phased Implementation Plan

Each step = one small PR. Each has a **Done when** check. No step starts before the one it depends on is merged.
Rule of the repo: every validator rule lands with a passing fixture **and** a failing fixture. That suite is the tool validation evidence (PRD §8).

Reference device **Breathe-Triage** grows phase by phase in `examples/breathe-triage/`. CI runs `threadline check` on it from Phase 2 onward.

---

## Phase 0 — Evidence and foundations
| # | Step | Done when |
|---|---|---|
| 0.1 | Close every **Unverified** row in PRD §11 (read primary sources: Model Law text, legislation.gov.uk, NHS DCB0129, WHO IMCI booklet, ISO/TR 24971, MHRA designated standards) | Ledger rows all Verified or Removed, with links |
| 0.2 | Repo skeleton: `pyproject.toml`, `src/threadline/`, ruff, pytest, CI on PR | `pytest` green in CI on empty package |
| 0.3 | Licences (Apache-2.0 code, CC-BY-4.0 `templates/` + `docs/`), README with disclaimer, CONTRIBUTING | Licence files + REUSE-style headers |
| 0.4 | `docs/adr/` + ADR-001 "one YAML per item", ADR-002 "JUnit property is the only test link", ADR-003 "signed approval records" | 3 ADRs merged |

## Phase 1 — Item model
| # | Step | Done when |
|---|---|---|
| 1.1 | Base `Item` model (id, type, title, rev, status) + loader walking `dhf/` | Loads fixture tree; bad YAML → clear error with path |
| 1.2 | TL-S01: schema validation + filename = ID | Pass/fail fixtures |
| 1.3 | Types: user_need, system_requirement, software_requirement, architecture_item | Schemas + fixtures |
| 1.4 | `make schema` (one-liner: Pydantic → JSON Schema); VS Code YAML settings in template | Editor autocompletes a SRS file |
| 1.5 | Breathe-Triage: intended use doc, 5 UN, 8 SYS, 15 SRS (IMCI rules) | Loads clean |

## Phase 2 — Traceability engine
| # | Step | Done when |
|---|---|---|
| 2.1 | Graph build from links; rule runner; rule result format (rule ID, item, clause, message) | Unit tests |
| 2.2 | TL-L01 dangling links | Fixtures |
| 2.3 | TL-L02, TL-L03 upward trace | Fixtures |
| 2.4 | TL-L04 cycles | Fixtures |
| 2.5 | `threadline check` CLI, exit codes, human output | CLI test |
| 2.6 | CI runs `threadline check examples/breathe-triage` | Green; deleting a link → red with rule ID |

## Phase 3 — Test evidence and RTM
| # | Step | Done when |
|---|---|---|
| 3.1 | pytest plugin: `@pytest.mark.verifies(...)` → JUnit `verifies` property | JUnit contains properties |
| 3.2 | JUnit parser (any framework) → evidence map | Parses pytest + a GoogleTest sample file |
| 3.3 | TL-E01, TL-E02 | Fixtures |
| 3.4 | `threadline rtm` → Markdown | Snapshot test |
| 3.5 | Breathe-Triage: reference code + tests for all SRS | Example green with `--junit` |

## Phase 4 — Risk management (ISO 14971)
| # | Step | Done when |
|---|---|---|
| 4.1 | `risk-policy.yaml` schema: severity, P1, P2, matrix, software-P1 rule | Two different policies load; matrix lookup tested |
| 4.2 | Types: hazard (sequence → situation → harm), risk_control (kind: design/protective/information), benefit_risk | Schemas + fixtures |
| 4.3 | TL-R01, TL-R02 | Fixtures |
| 4.4 | TL-R03, TL-R04 (**every RC has passing test**) | Fixtures |
| 4.5 | TL-R05 residual risk + benefit-risk; TL-R06 new-risk check | Fixtures |
| 4.6 | Risk management report section generator (plan, analysis, evaluation, overall residual risk) | Snapshot |
| 4.7 | DCB0129 hazard log export (CSV/MD) | Matches DCB0129 required fields (from 0.1) |
| 4.8 | Breathe-Triage: hazards incl. missed fast breathing, wrong age band, stale result | Example green |

## Phase 5 — Document control and e-signatures
| # | Step | Done when |
|---|---|---|
| 5.1 | Markdown documents with frontmatter as items; content hash | Hash stable across line endings (normalised) |
| 5.2 | Signer registry `qms/signers/` (allowed_signers + roles + effective dates) | Schema + fixtures |
| 5.3 | Approval item type; signature verification of the commit that added it (`git verify-commit` / `ssh-keygen -Y verify`) | Valid key passes; unknown key fails |
| 5.4 | TL-D01: role match, independence, hash binding, required approvals per doc type | Fixtures incl. self-approval and stale-hash cases |
| 5.5 | TL-D02: change to effective doc needs rev bump + fresh approvals (diff vs base branch) | Fixtures |
| 5.6 | Part 11 gap analysis doc; branch protection + CODEOWNERS guide for 4 simulated roles | Docs reviewed |

## Phase 6 — Distribution
| # | Step | Done when |
|---|---|---|
| 6.1 | `templates/project/` skeleton + `threadline init` | `init` → `check` fails red with clause-cited messages |
| 6.2 | Composite GitHub Action `action.yml` | Used by example's CI |
| 6.3 | Template workflows: `check.yml`, PR template, CODEOWNERS | Fresh init repo runs CI on GitHub |
| 6.4 | Publish to PyPI (trusted publishing) as 0.1.0 | `pip install threadline` works |

## Phase 7 — QMS (ISO 13485)
| # | Step | Done when |
|---|---|---|
| 7.1 | Clause map item: 13485 clause → artifacts/records; coverage report | Report lists unmapped clauses |
| 7.2 | SOP-01 Document Control, SOP-02 Software Lifecycle (62304), SOP-03 Risk Management | Effective with signed approvals in example |
| 7.3 | SOP-04 CAPA, SOP-05 Complaints & Vigilance (UK + Africa), SOP-06 PMS, SOP-07 Supplier/SOUP, SOP-08 Management Review, SOP-09 Training, SOP-10 Tool Validation | Same |
| 7.4 | Record types: capa, complaint, management_review, training_record (YAML in repo — one way) | Schemas + example records |
| 7.5 | Software Development Plan + SAD templates (Mermaid) | Example SDP, SAD with segregation diagram |

## Phase 8 — SOUP, SBOM, vulnerabilities
| # | Step | Done when |
|---|---|---|
| 8.1 | SOUP item type with all PRD §6.4 fields | Schema + fixtures |
| 8.2 | CycloneDX reader; TL-P01, TL-P02 | Fixtures from a real Syft SBOM |
| 8.3 | OSV.dev client (batch query, cached in test with recorded responses) | Offline tests pass |
| 8.4 | vulnerability item (exploitability, impact, decision); TL-P03 | Fixtures |
| 8.5 | `sbom.yml` workflow: PR + weekly schedule | Example repo shows run |

## Phase 9 — Usability (IEC 62366-1, full)
| # | Step | Done when |
|---|---|---|
| 9.1 | Types: user_group, use_environment, ui_characteristic, use_scenario | Schemas + fixtures |
| 9.2 | Types: formative_evaluation, summative_protocol, summative_report | Schemas + fixtures |
| 9.3 | TL-U01, TL-U02 | Fixtures |
| 9.4 | Usability engineering file generator section | Snapshot |
| 9.5 | Breathe-Triage worked example: CHW user groups, outdoor/low-light environment, 2 formatives, summative protocol + **illustrative** report | Example green; "ILLUSTRATIVE" watermark in PDF |

## Phase 10 — Cybersecurity (IEC 81001-5-1)
| # | Step | Done when |
|---|---|---|
| 10.1 | threat item (STRIDE category, asset, entry point) → security risk control → SRS | Schemas + fixtures |
| 10.2 | Rules: every threat assessed; every security RC verified | Fixtures |
| 10.3 | Breathe-Triage threat model (lost/shared phone, sync tampering) | Example green |

## Phase 11 — AI/ML lifecycle
| # | Step | Done when |
|---|---|---|
| 11.1 | dataset, model, pccp item types | Schemas + fixtures |
| 11.2 | `threadline hash` for dataset splits and weights; TL-M01, TL-M02 | Tampered weights → fail |
| 11.3 | BS/AAMI 34971 hazard preset pack | Loads; cites standard sections |
| 11.4 | Breathe-Triage: tiny RR-estimation model trained on **synthetic** data, subgroup metrics | Example green |

## Phase 12 — Lifecycle profiles (62304 Ed1 / Ed2 draft)
| # | Step | Done when |
|---|---|---|
| 12.1 | Profile data files: Ed1 class A/B/C → required activities & deliverables | Data reviewed against standard |
| 12.2 | Ed2 CD2 profile: PRL I/II (from CD2 text, versioned `ed2-cd2`) | Labelled DRAFT everywhere |
| 12.3 | TL-C01 | Same example passes Ed1-C and Ed2-PRL-II |

## Phase 13 — Regulatory profiles
| # | Step | Done when |
|---|---|---|
| 13.1 | Profile engine: required sections + classification item + checklist | Unit tests |
| 13.2 | `uk-mhra`: UK MDR 2002 essential requirements checklist, UKCA, PMS, DCB0129 outputs | Checklist lines link to evidence (TL-G01) |
| 13.3 | `au-model-law`: WHO GMRF class A–D rules, essential principles, country domestication note field | Same |
| 13.4 | Breathe-Triage classification rationale for both | Example green |

## Phase 14 — Technical file build
| # | Step | Done when |
|---|---|---|
| 14.1 | Pandoc + LaTeX template; container image with TeX Live + mermaid-cli pinned | `threadline build` makes PDF locally in container |
| 14.2 | Sections from profiles; hyperlinked IDs; approval manifestations; footer with tag/SHA | Visual check + text extraction test |
| 14.3 | `release.yml`: tag → re-run tests on tag → SBOM → build → attest → GitHub Release | Example tag produces release |
| 14.4 | DCB0129 safety case as separate output | Present in release |

## Phase 15 — Low-resource presets
| # | Step | Done when |
|---|---|---|
| 15.1 | `threadline preset add` mechanism | Copies pack; preset IDs carry a prefix (`PWR-RC-001`) so they never clash |
| 15.2 | `power-loss` (atomic writes, resume, battery-state UI) with WHO 2023 citation | Pack + test stubs |
| 15.3 | `offline-queue` (durable queue, idempotent sync, conflict rule) with GSMA citation | Same |
| 15.4 | `low-bandwidth-telemetry` | Same |
| 15.5 | `clock-drift`, `shared-device`, `sunlight-legibility` — **only once evidence found** | Source cited or step dropped |

## Phase 16 — Tool validation and v1.0
| # | Step | Done when |
|---|---|---|
| 16.1 | Threadline intended use + risk assessment of the tool itself (ISO/TR 80002-2) | Doc effective |
| 16.2 | Tool validation report = JUnit of the fixture suite, rendered by `threadline build` | Report in release |
| 16.3 | README quickstart + rule reference table generated from rule registry | Table in README |
| 16.4 | External QA/RA review of example PDF; fix findings | Review notes closed |
| 16.5 | Tag v1.0.0 | All PRD §10 criteria met |

---

## Dependency spine
```
0 → 1 → 2 → 3 → 4 → 5 → 6 ─┬→ 7
                            ├→ 8
                            ├→ 9
                            ├→ 10
                            ├→ 11
                            └→ 12 → 13 → 14 → 15 → 16
```
Phases 7–11 can run in any order after 6.
