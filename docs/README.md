# Threadline documentation

| Page | For | Covers |
|---|---|---|
| [Getting started](getting-started.md) | Engineers | Install, scaffold a repository, take one requirement from red to green |
| [Concepts](concepts.md) | Everyone | Items, links, evidence, documents and approvals, risk policy, profiles, presets, `threadline.yaml` |
| [CLI reference](cli.md) | Engineers | Every command, option and exit code |
| [Rule reference](rules.md) | Engineers, QA/RA | Every rule with its clause and the input it needs |
| [CI and releases](ci-and-releases.md) | Engineers, QA/RA | The GitHub Action, the scaffolded workflows, what counts as release evidence |
| [Threadline for QA and regulatory leads](for-qa-ra.md) | QA/RA | What it checks and what it doesn't, your responsibilities, reading the technical file |
| [Reading a Threadline technical file](for-auditors.md) | Auditors, reviewers | What the PDF contains, how to check it against the repository, what it does not claim |

## Guides

- [Branch protection and signing an approval](guides/branch-protection.md)
- [21 CFR Part 11 gap analysis](guides/part11-gap-analysis.md)
- [Threadline intended use and tool risk assessment](tool-validation/threadline-intended-use-and-risk.md)

## Design records

- [PRD](PRD.md): scope, standards mapped, and the evidence ledger of verified and unverified claims (§11)
- [PLAN](PLAN.md): phased implementation plan
- [ADR-001](adr/ADR-001-one-yaml-per-item.md): one YAML file per item
- [ADR-002](adr/ADR-002-junit-property-test-link.md): a JUnit property is the only test-to-item link
- [ADR-003](adr/ADR-003-signed-approval-records.md): signed approval records
