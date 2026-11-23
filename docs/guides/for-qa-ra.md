# Threadline for QA and regulatory leads

This page is for people who own the quality system rather than the code. You don't need to run any commands to use
it. It explains what Threadline checks on your behalf, what it leaves to you, and how to read what it produces.

## What changes for you

Your design history file stops being a set of documents someone updates before an audit. It becomes a set of small
records that engineers change in the same pull request as the code, and that a machine checks every time.

| Before | With Threadline |
|---|---|
| Traceability matrix maintained by hand in a spreadsheet | Rebuilt from the records on every change; a broken link fails the build |
| "Was this risk control tested?" answered by searching CI logs | Each risk control lists the tests that verify it; one failing test fails the control |
| Approval by signature page or e-mail | SSH-signed approval records, bound to the exact content and revision approved |
| SOUP list compiled before release | SBOM generated on every pull request and compared against the SOUP register |
| Technical file assembled by hand | Rebuilt from the repository for every release tag |

## What Threadline checks

Each rule enforces a specific clause. In plain terms:

- **Design controls** (ISO 13485 7.3, IEC 62304 5): every system requirement traces to a user need, every software
  requirement to a system requirement or risk control, there are no dangling links or cycles, and every software
  requirement is verified by tests that all pass.
- **Risk** (ISO 14971): every hazard has the full chain (hazard, sequence of events, hazardous situation, harm) and an
  estimate using your policy's levels; unacceptable risks are controlled; controls are implemented, verified and
  reviewed for new hazards; residual risk is acceptable or justified by benefit-risk.
- **Usability** (IEC 62366-1): hazard-related use scenarios name their hazards and user groups, are covered by a
  summative protocol, and have results.
- **Security** (IEC 81001-5-1): every threat is assessed and controlled; every published advisory against a
  dependency has a triage record.
- **SOUP** (IEC 62304 8): the SOUP register matches what is actually in the software, version for version, and each
  entry is approved.
- **AI/ML** (BS/AAMI 34971): models record their datasets, metrics by subgroup and acceptance criteria, and the files
  on disk match their registered hashes.
- **Document control** (ISO 13485 4.2.4): effective documents carry the approvals your policy requires, by people with
  the right roles, independent of the author, for the current revision and content. Content changes require a
  revision bump.
- **Regulatory profiles**: every clause of the ISO 13485, UK MDR 2002 and AU Model Law checklists is either mapped to
  evidence or justified as not applicable, and the device is classified under each market's scheme.
- **Lifecycle**: the deliverables IEC 62304 requires for your software class exist.

The full list, with clauses, is in the [rules reference](../reference/rules.md).

## What Threadline does not do

> [!IMPORTANT]
> Threadline checks that records are **complete and linked**. It does not judge whether they are **right**.

It will tell you a hazard has no severity estimate. It will not tell you the estimate is wrong. It will tell you a
clause has no evidence linked. It will not tell you the evidence is adequate. Specifically, it does not:

- decide whether the device is safe or effective,
- classify the device for you (it checks that you did, and recorded why),
- replace review by qualified people, or your Clinical Safety Officer under DCB0129,
- make your QMS certified or your device compliant.

## Adopting it: your responsibilities

1. **Validate it** for your intended use (ISO 13485 §4.1.6). Threadline's own
   [intended use and tool risk assessment](../tool-validation/threadline-intended-use-and-risk.md) is a starting
   point to copy into your SOP-10 records. Each release ships its test suite results as tool-validation evidence.
2. **Pin the version.** Re-validate when you change it. `init` pins it in the workflows.
3. **Replace the risk policy** in `threadline.yaml` with your own acceptability matrix.
4. **Review the profile data.** Some clause mappings were transcribed without the licensed standard to hand, and every
   run says so. Check them against your copies. The [evidence ledger](../PRD.md#11-evidence-ledger--what-is-verified-and-what-is-not)
   lists what is verified.
5. **Own the procedural controls.** Access control, key issuance and identity checks, branch protection, backups and
   retention are yours. The [Part 11 gap analysis](part11-gap-analysis.md) lists each one.
6. **Adapt the SOPs.** The ten SOPs from `init` are a starting point written for this way of working. They are yours
   to change, and must be approved like any other document.

## Reading the technical file

Each release produces a PDF. Every page footer shows the product, version and commit, so a page can always be traced
to one exact state of the repository.

| Section | Contents |
|---|---|
| Regulatory | Classifications, then each checklist (ISO 13485, UK MDR 2002, AU Model Law) with evidence links or justifications |
| Design controls | Intended use, user needs, system and software requirements, plans, architecture, clinical evaluation, lifecycle profile |
| Risk management report | Your risk policy, the hazard table with initial and residual risk, risk controls, overall residual risk |
| Usability engineering file | User groups, environments, UI characteristics, use scenarios, formative and summative evaluation |
| Cybersecurity | Threats and their controls |
| AI/ML data lifecycle | Datasets with hashes, models with subgroup metrics, change control plans |
| SOUP register and SBOM | Every third-party component and the triage of every advisory |
| Verification evidence | The traceability matrix and risk-control traceability, with the hash of the JUnit file |
| Quality management system | Controlled documents, a signatures table (who, when, meaning, signing commit), CAPAs, complaints, management reviews, training |
| Threadline rule results | Every rule, its clause and its result for this build |

Item IDs are hyperlinks: click `RC-001` in the hazard table to jump to the control. Fictional or illustrative data is
flagged on the cover.

## Working with engineers

- **Review the pull request, not a document.** Each change shows exactly which records moved. The PR template asks
  about risk impact, verification and SOUP for every change.
- **Make CODEOWNERS work for you.** The template routes changes to `threadline.yaml`, `qms/`, the signer registry and
  approvals to the QA team, and risk files to QA and engineering.
- **You sign with a command, not a pen.** `threadline approve SOP-03 --meaning approved_as_qa --signer you`. If that's
  unfamiliar, an engineer can pair with you once; [Releasing and signing](releasing.md) has the steps.

## See also

- [Guide for auditors](for-auditors.md): how an outside reviewer checks your release.
- [Glossary](../glossary.md) and [FAQ](../faq.md).
