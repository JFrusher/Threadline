# FAQ

## General

### Does using Threadline make my device compliant?

No. Threadline checks that your records are complete and linked, and builds the technical file from them. Whether the
content is right, and whether the device is safe, is decided by qualified people in your quality system. You also
have to validate Threadline for your own use (ISO 13485 §4.1.6). See
[What Threadline does not do](guides/for-qa-ra.md#what-threadline-does-not-do).

### Is it a replacement for an eQMS?

For a small software team it can be the core of one: documents, records, approvals, traceability, risk, SOUP and the
technical file all live in the repository. It has no web interface, no training management workflow and no supplier
portal. If you need those, it can still own the design file and hand the PDF to your eQMS.

### Which markets does it support?

The UK (UK MDR 2002, MHRA) and Africa (the AU Model Law with the WHO GMRF baseline). ISO 13485 is always on. FDA and
EU MDR profiles are not in v1; the item model doesn't prevent adding them.

### Why is my brand-new repository red?

On purpose. `init` creates a stub for every checklist clause and the lifecycle profile asks for every deliverable your
software class needs. Each finding is something your design file doesn't have yet. Green means you've covered it all.

### Is the example device real?

No. Breathe-Triage is fictional, and its clinical and usability data are illustrative. It exists to show a complete
design file that passes every rule. Its fast-breathing thresholds come from peer-reviewed sources on the WHO
IMCI guideline, listed in the [PRD evidence ledger](PRD.md#11-evidence-ledger--what-is-verified-and-what-is-not); it
is not clinical guidance.

## Engineering

### Do I have to use Python or pytest?

Your product can be in any language. Threadline itself needs Python 3.12+. Your tests only need to write JUnit XML
with a `verifies` property on each testcase; the pytest marker is a convenience. See [CI](guides/ci.md#tests-in-other-languages).

### Why one YAML file per item?

So that each item has its own history, pull requests don't conflict, and there is no index to keep in sync.
[ADR-001](adr/ADR-001-one-yaml-per-item.md) has the reasoning.

### Why can't I just name my tests after requirements?

Names drift and differ per language. One explicit link that every framework can write is harder to get wrong.
[ADR-002](adr/ADR-002-junit-property-test-link.md).

### Why do skipped tests count as failures?

A skipped test proved nothing. Counting it as verification would let a disabled test hide an unverified risk control.

### `check` says "skipped TL-D02 … needs base_ref". Is that a problem?

No. A skipped rule needs an input you didn't pass (here, `--base`). CI passes them. Only `build --release` insists on
every rule running.

### `check` says the signer registry has uncommitted changes (TL-D04).

Commit it. Threadline reads signatures and the signer registry from git history, and in a new repository the first
commit that adds `qms/signers/allowed_signers` becomes your root of trust.

### TL-D03 fails on CI but passes locally.

Almost always a shallow clone. Check out with `fetch-depth: 0`. The finding includes a hint when Threadline detects a
shallow repository.

### TL-D03 fails after merging an approval pull request.

The pull request was squashed or rebased, which rewrote the signed commits. Merge approval pull requests with a merge
commit. [Branch protection](guides/branch-protection.md) shows the settings.

### Can I use GPG instead of SSH keys?

No. SSH signing only: one mechanism, no keyserver trust model, and `ssh-keygen` is everywhere.
[ADR-003](adr/ADR-003-signed-approval-records.md).

### Why does `build` need XeLaTeX?

Typesetting a long, table-heavy document well is what LaTeX is for. The release workflow installs it for you; you
only need it locally to build the PDF yourself.

## Quality and regulatory

### Are SSH-signed commits valid electronic signatures?

Threadline designs them to the strictest common benchmark, 21 CFR Part 11: they show who, when and what meaning, are
bound to the content, and unique to one person. Some Part 11 controls are procedural and yours to put in place, such
as identity checks and a written policy that these signatures are binding. The
[gap analysis](guides/part11-gap-analysis.md) lists each one.

### What happens if someone loses their key?

Revoke it and register a new one; earlier approvals stay valid. Losing the only QA key needs an admin to re-root the
signer registry. [Releasing and signing](guides/releasing.md#lost-keys).

### Can I trust the clause mappings?

Treat them as a draft to review. Some were transcribed without the licensed standard to hand, and every `check` run
prints that note. The [evidence ledger](PRD.md#11-evidence-ledger--what-is-verified-and-what-is-not) marks each
regulatory claim as verified, unverified or refuted, and templates only cite verified ones.

### How is Threadline itself validated?

Every rule has a passing and a failing fixture. The suite runs on every change, and its results ship with each
release as the tool validation report. The
[intended use and tool risk assessment](tool-validation/threadline-intended-use-and-risk.md) is the starting point for
your own validation.

### I found a wrong clause citation. What should I do?

Please [open a regulatory claim issue](https://github.com/JFrusher/Threadline/issues/new?template=regulatory-claim.yml)
with your source. Corrections to regulatory content are the most valuable contributions the project gets.
