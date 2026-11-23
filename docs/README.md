# Threadline documentation

Pick the path that fits you. Every page links onwards, so you don't need to read them in order.

## I'm an engineer

1. [Getting started](getting-started.md): from `threadline init` to your first green check.
2. [Concepts](concepts.md): items, links, evidence, rules, signatures, baselines.
3. [CI](guides/ci.md): pull request checks, SBOM, the release workflow.
4. Reference: [CLI](reference/cli.md) · [Configuration](reference/configuration.md) ·
   [Item types](reference/items.md) · [Rules](reference/rules.md)

## I own the quality system

1. [Threadline for QA and regulatory leads](guides/for-qa-ra.md): what it checks, what it doesn't, your
   responsibilities, and how to read the technical file.
2. [Releasing and signing](guides/releasing.md): registering signers, approving, cutting a release, lost keys.
3. [Branch protection and roles](guides/branch-protection.md)
4. [Part 11 gap analysis](guides/part11-gap-analysis.md)
5. [Tool validation: intended use and risk](tool-validation/threadline-intended-use-and-risk.md)

## I'm reviewing someone's device

- [Threadline for auditors and reviewers](guides/for-auditors.md): what a release contains and how to verify it
  yourself.

## Everyone

- [Glossary](glossary.md) · [FAQ](faq.md)

## Design records

- [Product requirements (PRD)](PRD.md), including the evidence ledger of verified and unverified regulatory claims
- [Implementation plan](PLAN.md)
- Architecture decisions: [ADR-001 one YAML file per item](adr/ADR-001-one-yaml-per-item.md) ·
  [ADR-002 JUnit property as the test link](adr/ADR-002-junit-property-test-link.md) ·
  [ADR-003 signed approval records](adr/ADR-003-signed-approval-records.md)
