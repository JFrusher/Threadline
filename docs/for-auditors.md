# Reading a Threadline technical file

This page is for an auditor or reviewer who has been handed a technical file built by Threadline and wants
to know what it is, how far to trust it, and how to check it.

## What you have

A release of a Threadline-managed device has four files, attached to a GitHub Release:

| File | Content |
|---|---|
| `technical-file.pdf` | The compiled file described below |
| `hazard-log.md` | The hazards in DCB0129 hazard-log layout |
| `junit.xml` | Raw results of the test run on the release commit |
| `sbom.cdx.json` | CycloneDX software bill of materials |

Every page footer of the PDF carries the product name, the version and the git commit it was built from.
A cover marked `ILLUSTRATIVE` means at least one record declares itself fictional example data.

## Sections of the PDF

| Section | What to look for |
|---|---|
| Regulatory | Classification for each market, then a clause-by-clause map of ISO 13485 and each market's checklist to the records offered as evidence, or a justification for non-applicability |
| Design controls | Intended use, user needs, system and software requirements, development plan, architecture, detailed design, clinical evaluation, and the lifecycle profile in force |
| Risk management report | The manufacturer's risk policy and acceptability matrix, every hazard with initial and residual estimates, risk controls, overall residual risk |
| Usability engineering file | User groups, environments, hazard-related use scenarios, formative evaluations, summative protocol and report |
| Cybersecurity | Threats and their controls |
| AI/ML data lifecycle | Datasets with hashes, models with metrics by subgroup, change control plans |
| SOUP register and SBOM | Third-party components and vulnerability triage |
| Verification evidence | The SHA-256 of the JUnit file, the requirements traceability matrix and risk control traceability |
| Quality management system | Controlled documents and their status, the signature table, CAPA, complaints, management reviews, training, procedures |
| Threadline rule results | Which rules ran and which were skipped for lack of input |
| Tool validation | Results of Threadline's own test suite for the version used, when supplied |

Item IDs in the PDF are links to the item's entry.

## What the tool guarantees, and what it does not

The file cannot be built while any rule reports a finding. So for the commit in the footer, and for the
rules listed as run in the rule results section, the conditions in the [rule reference](rules.md) held.
Rules listed as skipped were not evaluated. A release build refuses to run if any rule other than TL-D02
would be skipped, and requires an approved baseline of the design file for that version.

Those rules check that records exist, are linked, are signed, and are backed by a passing test. They do not
check that a requirement is correct, that a hazard analysis is complete, that a risk estimate is
reasonable, or that a test actually exercises what it claims to verify. That judgement remains with the
manufacturer's reviewers and with you.

Threadline is not a certified QMS. The manufacturer is responsible for validating it for their use
(ISO 13485:2016 §4.1.6); ask for that record. The project's own assessment of how the tool can fail is in
[intended use and tool risk assessment](tool-validation/threadline-intended-use-and-risk.md).

## Checking it yourself

All of this needs only a clone of the manufacturer's repository at the commit in the footer.

Confirm the release files were built by the repository's workflow:

```bash
gh attestation verify technical-file.pdf --repo OWNER/REPO
```

Confirm the JUnit file is the one the PDF was built from, by comparing with the hash printed in the
verification evidence section:

```bash
sha256sum junit.xml
```

Confirm a signature. Each row of the signature table names a commit. A signature is valid if the key was in
the signer registry just before that commit, so first recover the registry from the commit's parent. Run
these from the repository root, with the path to the registry in that repository:

```bash
git show COMMIT^:qms/signers/allowed_signers > signers-then
```

```bash
git -c gpg.ssh.program=ssh-keygen -c gpg.ssh.allowedSignersFile="$PWD/signers-then" log -1 --format='%G? %GS' COMMIT
```

`G` followed by the signer's ID is a good signature. The signer's name and roles are in `threadline.yaml`.
Checking against today's registry can show an older signature as unverified if the registry was re-rooted
or the key was revoked since.

Confirm the signer registry itself. The technical file does not print the trust root it was built with; ask
the manufacturer for the value of their `THREADLINE_TRUST_ROOT` repository variable and for the record of
who set it. Every later change to `qms/signers/allowed_signers` must be in a commit signed by a QA signer
(TL-D04). This lists those commits for you to check the same way:

```bash
git log --format='%h %G? %GS %s' TRUST_ROOT..COMMIT -- qms/signers/allowed_signers threadline.yaml
```

Confirm an approval is bound to the document as it stands. The output should equal `subject_sha256` in the
approval record:

```bash
threadline hash qms/SOP-01.md
```

Re-run the rules, including the release baseline check:

```bash
threadline check --junit junit.xml --sbom sbom.cdx.json --trust-root TRUST_ROOT --release VERSION
```

## Electronic signatures

An approval is a YAML record naming the document or baseline, its revision, a hash binding it to the
document's identity, revision and content, the meaning of the signature and the signer, committed in an
SSH-signed commit. The design is in
[ADR-003](adr/ADR-003-signed-approval-records.md). How it maps to 21 CFR Part 11, what the manufacturer must
add, and the known gaps are in the [Part 11 gap analysis](guides/part11-gap-analysis.md). One gap matters
when reading the signature table: `signed_at` is written by the signer, and the tool does not compare it
with the commit time.

## Known limits of the content

- The IEC 62304 clause-to-class mapping in the tool was transcribed without the licensed text.
- The UK profile's essential-requirement titles are summaries, not the legal wording.
- The AU Model Law profile groups essential principles by topic, not by IMDRF clause number, and the
  manufacturer must record the national law applied in each country.
- The IEC 62304 Ed2 profile follows an unpublished committee draft and labels its output accordingly.
