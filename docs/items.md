# Item types

Every item is one YAML file whose name is its ID (documents are Markdown with YAML frontmatter). This page lists all
29 types. It was generated from the Pydantic models in [`src/threadline/items.py`](../src/threadline/items.py),
which are the source of truth; `threadline init` also writes them as a JSON Schema to `.vscode/item.schema.json` for
editor autocompletion.

## Fields every item has

| Field | Value | Required | Notes |
|---|---|---|---|
| `id` | text | yes | Letters, digits, `.` and `-`. Must equal the filename without extension (TL-S01). |
| `type` | one of the types below | yes | |
| `title` | text | yes | |
| `rev` | integer | | Default 1. Bump it when an effective document's content changes (TL-D02). |
| `status` | one of `draft`, `in_review`, `effective`, `obsolete` | | Default `draft`. Live items may not link to obsolete ones (TL-L05). |

Unknown fields are rejected, so a typo fails TL-S01 instead of being silently ignored.

**Links** are lists of IDs. "Links to" says which item types each may point at; TL-L01 checks the target exists and
has an allowed type. Links live on the child and point up.


## Design controls (ISO 13485 7.3, IEC 62304 5)

#### `user_need`

| Field | Value | Required | Links to |
|---|---|---|---|
| `text` | text | yes |  |

#### `system_requirement`

| Field | Value | Required | Links to |
|---|---|---|---|
| `text` | text | yes |  |
| `derives_from` | list of IDs |  | `user_need` |

#### `software_requirement`

| Field | Value | Required | Links to |
|---|---|---|---|
| `text` | text | yes |  |
| `derives_from` | list of IDs |  | `system_requirement` |
| `implements` | list of IDs |  | `risk_control` |

#### `architecture_item`

| Field | Value | Required | Links to |
|---|---|---|---|
| `text` | text | yes |  |
| `software_class` | one of `A`, `B`, `C` |  |  |
| `implements` | list of IDs |  | `software_requirement` |
| `uses_soup` | list of IDs |  | `soup` |
| `segregation` | text |  |  |

## Risk management (ISO 14971)

#### `hazard`

| Field | Value | Required | Links to |
|---|---|---|---|
| `category` | one of `software`, `use`, `security`, `ml`, `other` |  |  |
| `hazard` | text |  |  |
| `sequence_of_events` | text |  |  |
| `hazardous_situation` | text |  |  |
| `harm` | text |  |  |
| `severity` | text |  |  |
| `p1` | text |  |  |
| `p2` | text |  |  |
| `controls` | list of IDs |  | `risk_control` |
| `residual` | `Residual` (severity, p1, p2) |  |  |
| `benefit_risk` | text |  |  |
| `references` | list of text |  |  |

#### `risk_control`

| Field | Value | Required | Links to |
|---|---|---|---|
| `kind` | one of `inherent_safety_by_design`, `protective_measure`, `information_for_safety` | yes |  |
| `text` | text | yes |  |
| `new_risk_review` | text |  |  |
| `new_hazards` | list of IDs |  | `hazard` |

#### `benefit_risk`

| Field | Value | Required | Links to |
|---|---|---|---|
| `text` | text | yes |  |

## Usability (IEC 62366-1)

#### `user_group`

| Field | Value | Required | Links to |
|---|---|---|---|
| `profile` | text | yes |  |

#### `use_environment`

| Field | Value | Required | Links to |
|---|---|---|---|
| `text` | text | yes |  |

#### `ui_characteristic`

| Field | Value | Required | Links to |
|---|---|---|---|
| `text` | text | yes |  |
| `related_scenarios` | list of IDs |  | `use_scenario` |

#### `use_scenario`

| Field | Value | Required | Links to |
|---|---|---|---|
| `task` | text | yes |  |
| `text` | text | yes |  |
| `hazard_related` | true/false |  |  |
| `user_groups` | list of IDs |  | `user_group` |
| `environments` | list of IDs |  | `use_environment` |
| `hazards` | list of IDs |  | `hazard` |

#### `formative_evaluation`

| Field | Value | Required | Links to |
|---|---|---|---|
| `date` | text | yes |  |
| `method` | text | yes |  |
| `participants` | integer | yes |  |
| `findings` | text | yes |  |
| `scenarios` | list of IDs |  | `use_scenario` |

#### `summative_protocol`

| Field | Value | Required | Links to |
|---|---|---|---|
| `method` | text | yes |  |
| `participants_per_group` | integer | yes |  |
| `acceptance_criteria` | text | yes |  |
| `scenarios` | list of IDs |  | `use_scenario` |
| `user_groups` | list of IDs |  | `user_group` |

#### `summative_report`

| Field | Value | Required | Links to |
|---|---|---|---|
| `illustrative` | true/false | yes |  |
| `protocol` | list of IDs | yes | `summative_protocol` |
| `results` | list of `ScenarioResult` (scenario, outcome, use_errors, notes) | yes |  |
| `conclusion` | text | yes |  |

## SOUP and security (IEC 62304 8, IEC 81001-5-1)

#### `soup`

| Field | Value | Required | Links to |
|---|---|---|---|
| `name` | text | yes |  |
| `version` | text | yes |  |
| `supplier` | text | yes |  |
| `licence` | text | yes |  |
| `purpose` | text | yes |  |
| `software_class` | one of `A`, `B`, `C` | yes |  |
| `functional_requirements` | text | yes |  |
| `system_requirements` | text | yes |  |
| `anomaly_list_url` | text | yes |  |
| `anomaly_review_date` | text | yes |  |
| `anomaly_review_result` | text | yes |  |
| `approver` | text | yes |  |
| `hazards` | list of IDs |  | `hazard` |

#### `vulnerability`

| Field | Value | Required | Links to |
|---|---|---|---|
| `advisory` | text | yes |  |
| `soup` | list of IDs | yes | `soup` |
| `exploitability` | text | yes |  |
| `impact` | text | yes |  |
| `decision` | one of `not_affected`, `mitigated`, `fix_planned` | yes |  |
| `rationale` | text | yes |  |
| `controls` | list of IDs |  | `risk_control` |

#### `threat`

| Field | Value | Required | Links to |
|---|---|---|---|
| `stride` | one of `spoofing`, `tampering`, `repudiation`, `information_disclosure`, `denial_of_service`, `elevation_of_privilege` | yes |  |
| `asset` | text | yes |  |
| `entry_point` | text | yes |  |
| `assessment` | text |  |  |
| `controls` | list of IDs |  | `risk_control` |
| `hazards` | list of IDs |  | `hazard` |

## AI/ML (BS/AAMI 34971)

#### `dataset`

| Field | Value | Required | Links to |
|---|---|---|---|
| `source` | text | yes |  |
| `licence` | text | yes |  |
| `consent_basis` | text | yes |  |
| `sites` | text | yes |  |
| `demographics` | text | yes |  |
| `splits` | map of text → text | yes |  |
| `sha256` | map of text → text | yes |  |

#### `model`

| Field | Value | Required | Links to |
|---|---|---|---|
| `training_code` | text | yes |  |
| `datasets` | list of IDs |  | `dataset` |
| `hyperparameters` | map of text → number or integer or text |  |  |
| `weights_path` | text |  |  |
| `weights_sha256` | text |  |  |
| `metrics` | map of text → number |  |  |
| `acceptance_criteria` | text |  |  |
| `subgroup_metrics` | map of text → map of text → number |  |  |

#### `pccp`

| Field | Value | Required | Links to |
|---|---|---|---|
| `models` | list of IDs | yes | `model` |
| `planned_changes` | text | yes |  |
| `modification_protocol` | text | yes |  |
| `impact_assessment` | text | yes |  |

## QMS records (ISO 13485)

#### `capa`

| Field | Value | Required | Links to |
|---|---|---|---|
| `problem` | text | yes |  |
| `root_cause` | text | yes |  |
| `action` | text | yes |  |
| `effectiveness_check` | text | yes |  |
| `sources` | list of IDs |  | `complaint`, `management_review`, `vulnerability` |

#### `complaint`

| Field | Value | Required | Links to |
|---|---|---|---|
| `received` | text | yes |  |
| `description` | text | yes |  |
| `reportable` | true/false | yes |  |
| `reportability_rationale` | text | yes |  |
| `markets` | list of one of `uk`, `africa` |  |  |

#### `management_review`

| Field | Value | Required | Links to |
|---|---|---|---|
| `date` | text | yes |  |
| `inputs` | text | yes |  |
| `outputs` | text | yes |  |

#### `training_record`

| Field | Value | Required | Links to |
|---|---|---|---|
| `person` | text | yes |  |
| `subject` | text | yes |  |
| `date` | text | yes |  |
| `effectiveness` | text | yes |  |

#### `baseline`

| Field | Value | Required | Links to |
|---|---|---|---|
| `version` | text | yes |  |
| `dhf_sha256` | text | yes |  |

#### `approval`

| Field | Value | Required | Links to |
|---|---|---|---|
| `subject` | text | yes |  |
| `subject_rev` | integer | yes |  |
| `subject_sha256` | text | yes |  |
| `meaning` | one of `authored`, `reviewed`, `approved_as_qa`, `released` | yes |  |
| `signer` | text | yes |  |
| `signed_at` | text | yes |  |

## Regulatory and documents

#### `classification`

| Field | Value | Required | Links to |
|---|---|---|---|
| `scheme` | text | yes |  |
| `result` | text | yes |  |
| `rule` | text | yes |  |
| `rationale` | text | yes |  |

#### `requirement`

| Field | Value | Required | Links to |
|---|---|---|---|
| `source` | text | yes |  |
| `clause` | text | yes |  |
| `applicable` | true/false |  |  |
| `evidence` | list of IDs |  | any item |
| `justification` | text |  |  |

#### `document`

| Field | Value | Required | Links to |
|---|---|---|---|
| `doc_type` | text | yes |  |
| _(body)_ | Markdown after the frontmatter |  |  |

## Examples

[`examples/breathe-triage`](../examples/breathe-triage) has at least one item of almost every type. A few to start
with:

| Type | Example |
|---|---|
| `software_requirement` | [`dhf/srs/SRS-002.yaml`](../examples/breathe-triage/dhf/srs/SRS-002.yaml) |
| `hazard` | [`dhf/risk/HAZ-001.yaml`](../examples/breathe-triage/dhf/risk/HAZ-001.yaml) |
| `summative_report` | [`dhf/usability/SUMR-001.yaml`](../examples/breathe-triage/dhf/usability/SUMR-001.yaml) |
| `model` | [`dhf/ml/MODEL-001.yaml`](../examples/breathe-triage/dhf/ml/MODEL-001.yaml) |
| `document` | [`qms/SOP-01.md`](../examples/breathe-triage/qms/SOP-01.md) |
| `approval` | [`records/approvals/`](../examples/breathe-triage/records/approvals) |
| `baseline` | [`records/baselines/BL-example-v1.0.0.yaml`](../examples/breathe-triage/records/baselines/BL-example-v1.0.0.yaml) |
