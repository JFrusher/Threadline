# Threadline — Product Requirements Document

**Version:** 0.2 (draft) · **Date:** 2026-11-16 · **Owner:** Jacob

> Threadline is QMS-as-code for Software as a Medical Device (SaMD). Regulatory artifacts live as one-YAML-file-per-item in git. A CLI and GitHub Action prove the "digital thread" — user need → requirement → risk control → passing test → signed release — and compile an audit-ready technical file.
>
> **Disclaimer (ships in README):** Threadline is not a certified QMS and does not make a device compliant. It is tooling that a manufacturer's QMS may adopt and must validate for its own intended use.

---

## 1. Problem

Small SaMD teams keep regulatory evidence in Word, Excel and Confluence. Traceability rots between audits. Risk controls lose their tests. SOUP lists drift from real dependencies. The technical file is assembled by hand, late, by one tired person.

Developers already have the right primitives: git history, code review, CI, signed commits. Nobody wires them to the clauses.

## 2. Users

| User | Needs |
|---|---|
| SaMD startup engineer | Fails fast in CI when traceability breaks; no Word docs. |
| QA/RA lead | Every clause mapped to a record; approvals that hold up to audit. |
| Founder / consultant | Fork, fill in, ship a technical file for UK and African markets. |
| Auditor / Notified Body / Approved Body | Readable PDF; evidence tied to an exact release. |

## 3. Goals and non-goals

**Goals (v1)**
1. Real, installable tool: `pip install threadline` + GitHub Action + `threadline init` scaffold.
2. Full worked example device whose DHF passes every rule.
3. Markets: **UK (MHRA)** and **Africa (AU Model Law on Medical Products Regulation / WHO GMRF baseline)**.
4. Full IEC 62366-1 usability file in v1.
5. AI/ML data-lifecycle hooks in v1.
6. IEC 62304 lifecycle profile toggle: Ed1 (A/B/C) and Ed2 draft (PRL I/II).
7. Part 11-grade electronic signatures.

**Non-goals (v1)**
- eQMS web UI. Git + PDF only.
- FDA or EU MDR profiles (schema allows them later).
- IVD-specific rules (performance evaluation, specimen handling). Model Law covers IVD; deferred for scope only.
- Hosting, SaaS, multi-tenant anything.
- Language-specific dependency parsers (SBOM comes from Syft for all ecosystems).

## 4. Standards and regulations mapped

| Source | What Threadline covers |
|---|---|
| ISO 13485:2016 | SOP set, document control, records, CAPA, complaints, management review, supplier (SOUP) control, clause→artifact map, §4.1.6 tool validation. |
| IEC 62304:2006+A1:2015 | SDP, SRS, SAD, detailed design (class-dependent), SOUP (cl. 5.3.3/5.3.4/7.1.2/8), problem resolution, maintenance. |
| IEC 62304 Ed2 (draft, CD2) | Optional PRL I / PRL II profile. **Labelled draft.** Not published; IEC forecast Oct 2028. |
| ISO 14971:2019 + ISO/TR 24971:2020 | Hazard → sequence of events → hazardous situation → harm; P1×P2; configurable acceptability; risk controls; residual & overall residual risk; benefit-risk. |
| IEC 62366-1:2015+A1:2020 | Use specification, user interface characteristics, hazard-related use scenarios, UI specification, formative evaluations, summative protocol + report. |
| IEC 81001-5-1:2021 | Threat model, security risk, security requirements, vulnerability handling, SBOM. |
| IEC 82304-1:2016 | Health software product requirements (SaMD product-level). |
| BS/AAMI 34971:2023 | ML-specific hazards (data quality, bias, over-trust, drift) as risk presets. |
| UK MDR 2002 (as amended) + MHRA guidance | UK regulatory profile; essential requirements checklist; PMS records. |
| DCB0129 (NHS England) | Clinical risk management export: hazard log, safety case, Clinical Safety Officer sign-off. |
| AU Model Law on Medical Products Regulation (2016) | Africa profile baseline, domesticated per country. |
| WHO Global Model Regulatory Framework (MD incl. IVD) | Risk classes A–D, essential principles; basis of AMDF harmonisation. |
| IMDRF SaMD documents | SaMD risk categorisation (I–IV), clinical evaluation. |
| 21 CFR Part 11 (as design benchmark) | E-signature design target (§11.50, §11.70, §11.100, §11.200). Not legally required in UK/Africa; used as the strictest common benchmark. |

## 5. Core concepts

### 5.1 Items
Everything is an **item**: one YAML file, filename = ID.

```yaml
# dhf/srs/SRS-014.yaml
id: SRS-014
type: software_requirement
title: Classify fast breathing using IMCI age thresholds
rev: 3
status: effective          # draft | in_review | effective | obsolete
derives_from: [SYS-004]
implements: [RC-007]       # risk controls this requirement implements
safety_class: C
text: >
  The system shall flag "fast breathing" when respiratory rate is
  >= 50/min for age 2–11 months and >= 40/min for age 12–59 months.
```

Item types (v1): `user_need, system_requirement, software_requirement, architecture_item, hazard, risk_control, use_scenario, user_group, soup, vulnerability, threat, dataset, model, pccp, capa, complaint, management_review, document`.

### 5.2 Links
Typed, one direction, stored on the child. Graph is built at check time. Rules run on the graph.

### 5.3 Test evidence — one way
A test verifies an item through a JUnit XML `<property name="verifies" value="SRS-014"/>`.
- Python: shipped pytest plugin, `@pytest.mark.verifies("SRS-014")`.
- Any other framework: emit the same JUnit property (e.g. GoogleTest `RecordProperty`).

No docstring parsing, no name conventions. One mechanism.

### 5.4 What counts as verification evidence
- **PR runs gate merges.** They are not records.
- **Release evidence** = the full suite re-run on the exact tagged commit by `release.yml`. The JUnit XML, its SHA-256, tool versions and runner image are embedded in the technical file and attached to the GitHub Release with a build-provenance attestation.

### 5.5 Documents and electronic signatures
Documents (SOPs, plans, reports) are Markdown with YAML frontmatter, versioned **per document** (`rev`), lifecycle `draft → in_review → effective → obsolete`.

An **approval record** is an item:

```yaml
# records/approvals/APR-SOP-01-r4-qa.yaml
id: APR-SOP-01-r4-qa
type: approval
subject: SOP-01
subject_rev: 4
subject_sha256: 9f2c…          # hash of the document content at approval
meaning: approved_as_qa        # authored | reviewed | approved_as_qa | released
signer: jdoe
signed_at: 2026-11-16T10:42:00Z
```

It must arrive in an **SSH-signed commit** by the signer (ADR-003). CI checks:
1. Signature valid against `qms/signers/allowed_signers` (controlled signer registry: key → person → roles → effective dates).
2. Signer holds the role the `meaning` needs.
3. Signer ≠ author for review/approval meanings (independence).
4. `subject_sha256` matches the document at `subject_rev`.
5. An `effective` document has all approvals its type's policy needs.

Part 11 mapping: §11.50 manifestation (name, time, meaning in record and PDF), §11.70 linking (hash binding), §11.100 uniqueness (registry), §11.200 two components (GitHub auth + key passphrase or hardware key). Gap analysis ships as `qms/part11-gap-analysis.md`.

GitHub PR approvals and branch protection are **process controls**, not the signature record.

### 5.6 Risk policy — configurable
`qms/risk-policy.yaml` defines severity levels, P1 (hazardous situation occurs) and P2 (situation leads to harm) levels, the acceptability matrix, and the rule for software P1 (default: assume P1 = 1 unless justified). No RPN.

### 5.7 Lifecycle profile toggle
`threadline.yaml: lifecycle_profile: iec62304-ed1 | iec62304-ed2-draft`. The profile says which activities and deliverables each class / rigour level needs. Validator checks they exist. Ed2 profile prints a "DRAFT STANDARD" banner in every output.

### 5.8 Regulatory profiles
`regulatory_profiles: [uk-mhra, au-model-law]`. A profile adds: classification items, an essential requirements / essential principles checklist (each line linked to evidence items), and required technical file sections.

## 6. Functional requirements

### 6.1 CLI
| Command | Does |
|---|---|
| `threadline init` | Scaffold a new QMS repo from the template. |
| `threadline check` | Load items, validate schemas, run all rules. Non-zero exit on any failure. |
| `threadline check --junit results.xml` | Also run evidence rules. |
| `threadline rtm` | Write RTM (Markdown). |
| `threadline sbom-audit sbom.cdx.json` | Diff SBOM vs SOUP register; query OSV.dev. |
| `threadline build` | Compile technical file PDF (Pandoc + LaTeX). |
| `threadline preset add <name>` | Copy a low-resource preset pack into the DHF. |

### 6.2 Rules (v1)
Each rule has an ID, a clause reference and a passing + failing fixture.

| Rule | Check | Clause |
|---|---|---|
| TL-S01 | Every file valid against its type schema; filename = ID | 13485 4.2.4 |
| TL-L01 | No dangling links | 62304 5.1.1 |
| TL-L02 | Every SRS traces up to SYS or RC | 62304 5.2 |
| TL-L03 | Every SYS traces to a UN | 13485 7.3.3 |
| TL-L04 | No cycles | — |
| TL-R01 | Every hazard has a hazardous situation, harm, severity, P1, P2 | 14971 5.4–5.5 |
| TL-R02 | Every unacceptable initial risk has ≥1 RC | 14971 7.1 |
| TL-R03 | Every RC is implemented by ≥1 SRS (or is labelling/IFU, typed) | 14971 7.2 |
| TL-R04 | **Every RC verified by ≥1 passing test** (implementation + effectiveness) | 14971 7.2 |
| TL-R05 | Residual risk acceptable per policy, or benefit-risk record exists | 14971 7.4 |
| TL-R06 | Every RC checked for new risks introduced | 14971 7.5 |
| TL-E01 | Every SRS verified by ≥1 passing test | 62304 5.7 |
| TL-E02 | No test references an unknown ID | — |
| TL-U01 | Every hazard-related use scenario links to a hazard | 62366-1 5.5 |
| TL-U02 | Summative evaluation covers every hazard-related use scenario selected | 62366-1 5.7 |
| TL-P01 | Every SBOM component has an approved SOUP entry, version match | 62304 7.1.2, 8.1.2 |
| TL-P02 | No stale SOUP entries | 62304 8.1.2 |
| TL-P03 | Every known vulnerability has a triage record | 81001-5-1 |
| TL-D01 | Effective docs have valid signed approvals (§5.5) | 13485 4.2.4, Part 11 |
| TL-D02 | Content change to an effective doc needs rev bump + new approvals | 13485 4.2.4 |
| TL-M01 | Every model has dataset refs, weights hash, acceptance criteria | 34971 |
| TL-M02 | Released model weights hash matches registered model | 62304 8 |
| TL-C01 | Deliverables required by lifecycle profile + class exist | 62304 / Ed2 |
| TL-G01 | Every essential requirement line has evidence links | UK MDR / WHO GMRF |

### 6.3 GitHub integration
- `uses: threadline/threadline@v1` composite Action wrapping the CLI.
- Workflows in template: `check.yml` (PR), `sbom.yml` (PR + weekly), `release.yml` (tag → re-run tests → SBOM → PDF → attest → release).
- `PULL_REQUEST_TEMPLATE.md`: risk impact, items touched, verification plan, SOUP change.
- `CODEOWNERS` + branch protection guide for simulated roles (dev, QA, CSO, release manager).

### 6.4 SOUP and SBOM
- Syft makes the CycloneDX SBOM (all ecosystems). Threadline only reads CycloneDX.
- SOUP entry fields: name, version, supplier, licence, purpose, safety class, functional & performance requirements (62304 5.3.3), hardware/software needed (5.3.4), published anomaly list URL + review date + result, risk analysis refs, approver.
- OSV.dev queries. New CVE fails `sbom.yml` until a `vulnerability` triage item exists.

### 6.5 Technical file
- Pandoc + LaTeX template; Mermaid diagrams rendered by mermaid-cli.
- Sections per regulatory profile; DCB0129 safety case + hazard log as separate outputs.
- Every page footer: product, release tag, commit SHA, build date, DRAFT banner if any draft profile.
- Hyperlinked IDs. Approval manifestations printed.
- Release attaches PDF, SBOM, JUnit, and attestation.

### 6.6 Usability (full v1)
Item types: `user_group, use_environment, ui_characteristic, use_scenario, formative_evaluation, summative_protocol, summative_report`. Worked example includes all of them for the reference device. Summative data is **clearly marked illustrative/fictional**.

### 6.7 AI/ML
- `dataset`: source, licence, consent/ethics basis, collection sites, demographics, splits, SHA-256 per split.
- `model`: training code commit, dataset refs, hyperparameters, weights SHA-256, metrics, acceptance criteria, subgroup performance.
- `pccp`: planned changes, modification protocol, impact assessment (MHRA PCCP guidance is still draft — field set kept minimal, revisited).
- Preset hazards from BS/AAMI 34971.

### 6.8 Low-resource presets
Each preset = hazards + RCs + SRS templates + test stubs + **cited evidence**.

| Preset | Evidence basis |
|---|---|
| `power-loss` | WHO/World Bank/IRENA/SEforALL *Energizing Health* (2023): ~1 billion people served by facilities without reliable electricity; ~half of sub-Saharan facilities have unreliable power. |
| `offline-queue` | GSMA *State of Mobile Internet Connectivity 2025*: 25% mobile internet use in sub-Saharan Africa, 10% coverage gap. |
| `low-bandwidth-telemetry` | Same GSMA source; affordability data. |
| `clock-drift` | **Evidence needed** — devices offline for days without NTP. |
| `shared-device` | **Evidence needed** — CHW device sharing studies. |
| `sunlight-legibility` | **Evidence needed** — outdoor use; link to 62366 use environment. |

Presets marked "evidence needed" do not ship until a source is found.

## 7. Reference device — "Breathe-Triage" (fictional)

- **What:** offline Android-class SaMD (reference implementation in Python) used by community health workers. Counts respiratory rate (ML-assisted tap/video cue) and applies WHO IMCI danger-sign rules for children 2–59 months; outputs refer/treat/home-care.
- **Why this one:** exercises every part — Class C (missed pneumonia → death), ML model, offline queue, power loss, sunlight, low literacy, shared devices.
- **Classification:** IEC 62304 Class C / Ed2 PRL II; IMDRF SaMD category to be justified in the DHF; WHO GMRF class to be justified; UK MDR class to be justified (rule 11-equivalent reasoning under UK MDR 2002 differs from EU MDR — must be checked).
- **Code:** small, real, tested Python package in `examples/breathe-triage/`. The tool's own CI runs `threadline check` on it — dogfood and regression test in one.

## 8. Tool validation (ISO 13485 §4.1.6)
- Intended use statement for Threadline and for GitHub Actions.
- Risk-based approach (ISO/TR 80002-2).
- Evidence: every rule has failing fixtures; the suite is the validation protocol; its JUnit output, rendered by `threadline build`, is the tool validation report per version.
- Template ships `qms/tool-validation.md` for adopters to complete for **their** use.

## 9. Tech choices
| Area | Choice | Why |
|---|---|---|
| Language | Python 3.12 | Ecosystem, user's stack. |
| Schemas | Pydantic v2 → JSON Schema export | One source of truth; editor autocompletion. |
| YAML | ruamel.yaml | Keeps comments and order on rewrite. |
| CLI | argparse | Stdlib. |
| SBOM | Syft (external) → CycloneDX JSON | Every ecosystem, zero parsers. |
| Vulns | OSV.dev API | Free, no key. |
| PDF | Pandoc + LaTeX (TeX Live) + mermaid-cli | User choice; best typesetting. |
| Provenance | `actions/attest-build-provenance` | Signed release evidence. |
| Licences | Apache-2.0 (code), CC-BY-4.0 (templates, SOPs, docs) | |

## 10. Success criteria (v1.0)
1. `threadline init demo && cd demo && make check` fails red on the empty skeleton, with clause-cited messages.
2. Breathe-Triage example passes every rule; removing any one link makes CI fail with the right rule ID.
3. Tag on example → GitHub Release with PDF technical file, SBOM, JUnit, attestation.
4. Approval forged with an unregistered key, or self-approved, fails TL-D01.
5. Tool validation report generated for v1.0.
6. An outside QA/RA reviewer reads the PDF and finds no clause mis-citations. (Ask a former colleague.)

## 11. Evidence ledger — what is verified and what is not

| Claim | Status | Source |
|---|---|---|
| IEC 62304 Ed2 unpublished; CD2 Aug 2026; forecast Oct 2028; PRL I/II replaces A/B/C | Verified (multiple sources; one outlier claims publication — rejected) | [Jama](https://www.jamasoftware.com/requirements-management-guide/medical-devices/iec-62304/), [MD Regulatory](https://mdregulatory.com/iec-62304/), [VDE](https://www.vde.com/topics-en/health/expertise/iec-62304-edition-2-changes), [QuickBird](https://quickbirdmedical.com/en/news/iec-62304-edition-2-august-2026/) |
| AU Model Law endorsed Jan 2016; domesticated nationally | Verified | [PMC9922692](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9922692/), [Frontiers 2026](https://www.frontiersin.org/journals/medicine/articles/10.3389/fmed.2026.1763261/pdf) |
| AMA operational Oct 2025, HQ Kigali, advisory role | Partly verified (press release + single blog for "advisory") | [APO](https://www.africa-newsroom.com/press/african-medicines-agency-marks-first-year-of-operations-with-new-platforms-to-strengthen-regulation-and-support-manufacturing?lang=en), [ghmap](https://www.ghmap.io/blog/africa-medical-device-regulation-acceleration-2026) |
| AU Model Law device scope excludes IVD | **Refuted** — Art. 4 "medical device" includes in vitro reagents/calibrators and software | [AU Model Law (EN copy)](https://kyokuhp.jihs.go.jp/library/regulation/PDF_JPG/AUmodellaw_e.pdf), [AUDA-NEPAD guidance](https://adphealth.org/upload/resource/au-model-law-guidance-20221011.pdf) |
| AMDF harmonises on WHO GMRF; no AMDF SaMD guidance found | Verified (absence = not found, not proof) | [AMDF](https://www.nepad.org/microsite/africa-medical-devices-forum-amdf), [WHO GMRF](https://www.who.int/publications/i/item/9789241512350) |
| MHRA draft regs: reliance route, PCCP, cyber; adoption ~Dec 2026 | **Unverified — secondary only.** Profile must not cite until made law | [meddeviceguide](https://meddeviceguide.com/blog/uk-mhra-international-reliance-pathway-draft-regulation-2026-guide), [Covington](https://www.insideeulifesciences.com/2026/10/21/uk-medical-device-update-developments-in-ai-and-proposed-gb-licensing-framework/) |
| UK PMS regulations (SI 2024/1368, new Part 4A of UK MDR 2002) in force 16 June 2025 | Verified | [GOV.UK](https://www.gov.uk/government/news/first-major-overhaul-of-medical-device-regulation-comes-into-force-across-great-britain), [BSI](https://compliancenavigator.bsigroup.com/en/medicaldeviceblog/great-britains-updated-post-market-surveillance-requirements-now-in-force-what-manufacturers-need-to-know/) |
| UK serious-incident report: 15 days general; 2-day / 10-day tiers for public health threat / death or serious deterioration | 15 days: multiple secondary sources. **2/10 days: Unverified** (single non-authoritative page) — SOP-05 does not state them | [CMS](https://cms.law/en/gbr/legal-updates/new-post-market-medical-device-surveillance-regulations-take-effect-in-great-britain), [GOV.UK](https://www.gov.uk/government/news/mhra-guidance-on-new-medical-devices-post-market-surveillance-requirements) |
| DCB0129 current (v4.2); national review consultation closed Sep 2026 | Partly verified (NHS standards page active; v4.2 from vendor). Hazard log fields: take from NHS England template | [NHS standards](https://standards.nhs.uk/published-standards/clinical-risk-management-its-application-in-the-manufacture-of-health-it-systems), [NHS Engage](https://www.engage.england.nhs.uk/patient-safety/national-review-of-clinical-risk-management-standa/) |
| UK designated standards (list of 17 Jan 2026): EN ISO 13485:2016+A11:2021, EN ISO 14971:2019+A11:2021, EN 62366-1:2015+A1:2020, **EN 62304:2006 (no A1)** | **Verified — primary** (parsed consolidated ODS) | [GOV.UK list](https://www.gov.uk/government/publications/designated-standards-medical-devices) |
| IEC 81001-5-1 / IEC 82304-1 UK designated | **Refuted** — not on the list. Used as state-of-the-art, not presumption of conformity | Same |
| BS/AAMI 34971:2023 content | Verified | [BSI](https://knowledge.bsigroup.com/articles/how-to-tackle-hazards-in-ai-medical-devices-using-bs-aami-34971) |
| ~50% SSA facilities unreliable power | Verified | [WHO](https://www.who.int/news/item/14-01-2023-close-to-one-billion-people-globally-are-served-by-health-care-facilities-with-no-electricity-access-or-with-unreliable-electricity) |
| SSA 25% mobile internet use, 10% coverage gap | Verified | [GSMA SOMIC 2025](https://www.gsma.com/somic/wp-content/uploads/2025/09/The-State-of-Mobile-Internet-Connectivity-2025-Trends-in-Mobile-Internet-Connectivity.pdf) |
| Fast breathing: ≥50/min (2–11 mo), ≥40/min (12–59 mo), ≥60/min (<2 mo) | Verified via peer-reviewed sources; WHO chart booklet still to read before clinical text ships | [WHO Bulletin 2003](https://scielosp.org/pdf/bwho/2003.v81n4/298-300/en), [BMJ Open Resp Res 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6307622/table/T1) |
| Software P1 = 1 convention | **Not verified.** 62304 A1 classifies on whether failure *can* contribute to a hazardous situation, not likelihood. Policy default stays configurable, cites no clause | [62304 A1 sample](https://cdn.standards.iteh.ai/samples/21252/f7905e39d6514a4da0bb6592596afd44/IEC-62304-2006-AMD1-2015.pdf) |

Rule: nothing **Unverified** or **Refuted** is cited as fact in a template. The UK profile cites UK-designated editions; IEC 62304 A1 is used (state of the art) with a note that only the 2006 edition is designated.
