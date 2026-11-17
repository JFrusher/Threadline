# Concepts

## Items

Everything Threadline checks is an **item**: one file, whose name is the item's ID
([ADR-001](adr/ADR-001-one-yaml-per-item.md)). Most items are YAML. Documents are Markdown with YAML
frontmatter. Items are read from `dhf/`, `qms/` and `records/` (change with `item_dirs` in `threadline.yaml`).

Every item has these fields:

| Field | Meaning |
|---|---|
| `id` | Letters, digits, `.` and `-`. Must equal the filename without its extension |
| `type` | One of the types below |
| `title` | Short name, shown in the RTM and technical file |
| `rev` | Integer revision, default 1 |
| `status` | `draft`, `in_review`, `effective` or `obsolete`; default `draft` |

Unknown fields are rejected, so a typo in a field name is a TL-S01 finding, not a silently ignored line.

### Item types and their links

Links are typed, one-directional and stored on the child. A link to a missing item, or to an item of the
wrong type, is a TL-L01 finding. Clause numbers are in the [rule reference](rules.md).

| Type | Link fields (target type) | Area |
|---|---|---|
| `user_need` | | ISO 13485 |
| `system_requirement` | `derives_from` (user_need) | ISO 13485 |
| `software_requirement` | `derives_from` (system_requirement), `implements` (risk_control) | IEC 62304 |
| `architecture_item` | `implements` (software_requirement), `uses_soup` (soup) | IEC 62304 |
| `hazard` | `controls` (risk_control) | ISO 14971 |
| `risk_control` | `new_hazards` (hazard) | ISO 14971 |
| `benefit_risk` | | ISO 14971 |
| `user_group`, `use_environment` | | IEC 62366-1 |
| `ui_characteristic` | `related_scenarios` (use_scenario) | IEC 62366-1 |
| `use_scenario` | `user_groups`, `environments`, `hazards` | IEC 62366-1 |
| `formative_evaluation` | `scenarios` (use_scenario) | IEC 62366-1 |
| `summative_protocol` | `scenarios`, `user_groups` | IEC 62366-1 |
| `summative_report` | `protocol` (summative_protocol) | IEC 62366-1 |
| `soup` | `hazards` (hazard) | IEC 62304 |
| `vulnerability` | `soup`, `controls` (risk_control) | IEC 81001-5-1 |
| `threat` | `controls` (risk_control), `hazards` (hazard) | IEC 81001-5-1 |
| `dataset` | | BS/AAMI 34971 |
| `model` | `datasets` (dataset) | BS/AAMI 34971 |
| `pccp` | `models` (model) | Predetermined change control plan |
| `capa` | `sources` (complaint, management_review, vulnerability) | ISO 13485 |
| `complaint`, `management_review`, `training_record` | | ISO 13485 |
| `approval` | `subject` names a document | ISO 13485 |
| `classification` | | IEC 62304; market rules |
| `requirement` | `evidence` (any item) | A clause of a standard or regulation mapped to evidence |
| `document` | | Markdown with frontmatter; has a `doc_type` |

The exact fields of each type are in [`src/threadline/items.py`](../src/threadline/items.py), and in the
JSON Schema that `threadline init` writes to `.vscode/item.schema.json`.

## Test evidence

A test verifies an item when its JUnit XML testcase carries `<property name="verifies" value="SRS-014"/>`.
That is the only mechanism ([ADR-002](adr/ADR-002-junit-property-test-link.md)). Test names, docstrings and
comments are not read.

- With pytest, the bundled plugin provides `@pytest.mark.verifies("SRS-014", "RC-007")`. It requires
  `junit_family = xunit1`.
- With any other framework, write the same property into its JUnit output.

A test counts as passing when its testcase has no `failure`, `error` or `skipped` child. A skipped test is
not evidence.

Runs on pull requests gate merges. The record of verification is the run on the release tag: see
[CI and releases](ci-and-releases.md).

## Documents and approvals

A document is a Markdown file with frontmatter:

```markdown
---
id: SOP-01
type: document
doc_type: sop
title: Document Control
rev: 1
status: effective
---
# SOP-01 Document Control
```

An approval is its own item, committed on its own:

```yaml
id: APR-SOP-01-r1-qa
type: approval
title: SOP-01 rev 1 approved_as_qa
subject: SOP-01
subject_rev: 1
subject_sha256: 99f99fe1c534b980d34f13c99816e027c2d3db14a6dbfea0282e3481db8914f7
meaning: approved_as_qa        # authored | reviewed | approved_as_qa | released
signer: quinn
signed_at: '2026-11-16T12:17:36Z'
```

Three rules make that record a signature ([ADR-003](adr/ADR-003-signed-approval-records.md)):

| Rule | Checks |
|---|---|
| TL-D01 | An `effective` document has every approval its `doc_type` requires; each signer is registered in `threadline.yaml` with the role the meaning needs; whoever signed `authored` signed no other approval of that revision; `subject_sha256` matches the document body |
| TL-D02 | If the body of an effective document changed since the base ref, `rev` went up |
| TL-D03 | The approval file was committed exactly once, in a commit carrying a valid SSH signature from the named signer, and has not been edited since |

Signatures are verified with `ssh-keygen` against `qms/signers/allowed_signers` in the repository, whatever
the local git configuration says. `threadline hash <file.md>` prints the value to put in `subject_sha256`.

Meanings map to roles: `authored` needs `author`, `reviewed` needs `reviewer`, `approved_as_qa` needs `qa`,
`released` needs `release_manager`.

Squash merges break this, because they replace the signed commit with an unsigned one. See
[branch protection](guides/branch-protection.md).

## Risk policy

The `risk` block of `threadline.yaml` defines your ISO 14971 policy:

- `severity`, `p1` (the hazardous situation occurs) and `p2` (the situation leads to harm): ordered level names
- `probability`: the combined level for each `p1`/`p2` pair
- `acceptability`: `acceptable` or `unacceptable` for each severity and combined probability
- `software_p1_rule`: your stated convention for P1 of software failures

The loader rejects a policy with a missing cell. There is no risk priority number. The policy shipped by
`threadline init` is an illustrative 5x5 matrix and should be replaced with yours.

## Lifecycle profiles

`lifecycle_profile` selects which deliverables each software class requires (TL-C01).

| Profile | Classes | Notes |
|---|---|---|
| `iec62304-ed1` | `A`, `B`, `C` | IEC 62304:2006+A1:2015. The clause-to-class mapping was transcribed without the licensed text; verify it |
| `iec62304-ed2-draft` | `PRL-I`, `PRL-II` | Based on a committee draft. Every output is labelled `DRAFT STANDARD` |

The profile data is in [`src/threadline/data/lifecycle`](../src/threadline/data/lifecycle).

## Regulatory profiles

`regulatory_profiles` adds, per market, a checklist of clauses and the classification schemes that market
needs. The ISO 13485 clause map is always active.

| Profile | Checklist | Classification scheme |
|---|---|---|
| `qms-iso13485` (always on) | ISO 13485:2016 clauses | |
| `uk-mhra` | UK MDR 2002 essential requirements and Part 4A post-market surveillance | `uk-mhra` |
| `au-model-law` | WHO GMRF essential principles and Model Law obligations | `who-gmrf` |

For each checklist entry you add a `requirement` item with the same ID, either linking `evidence` items or
setting `applicable: false` with a `justification` (TL-G01). For each scheme you add a `classification` item
(TL-G02).

## Presets

A preset is a pack of hazards, risk controls, software requirements and failing test stubs for a failure
mode common in low-resource settings or ML devices. Each hazard cites its published source.

```bash
threadline preset add power-loss
```

| Preset | Covers |
|---|---|
| `power-loss` | Device loses power mid-use |
| `offline-queue` | Records queued while offline |
| `low-bandwidth-telemetry` | Telemetry over poor connections |
| `ml-34971` | Data quality, bias, over-trust and drift per BS/AAMI 34971 |

Items land in `dhf/presets/<name>/` and tests in `tests/presets/`. The pack is red until you estimate
severity, P1 and P2 for each hazard, review each control for new risks, and implement the test stubs.

## `threadline.yaml`

| Key | Meaning |
|---|---|
| `product` | Product name, printed on the technical file |
| `item_dirs` | Directories scanned for items. Default `[dhf, qms, records]` |
| `lifecycle_profile` | `iec62304-ed1` or `iec62304-ed2-draft` |
| `software_class` | `A`, `B`, `C`, or `PRL-I`, `PRL-II` with the Ed2 draft profile |
| `regulatory_profiles` | Any of `uk-mhra`, `au-model-law` |
| `risk` | Risk policy, above |
| `signers` | `id: {name, roles}` for each person who may sign |
| `approvals_required` | `doc_type: [meanings]`; `'*'` is the default. Default `[authored, approved_as_qa]` |

Unknown keys are rejected.
