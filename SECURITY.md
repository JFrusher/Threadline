# Security policy

Threadline produces evidence that medical device software is safe. A flaw that lets a forged approval pass, hides a
failing test, or leaks data into a published PDF matters more here than in most tools. Thank you for reporting one
responsibly.

## Reporting a vulnerability

**Please don't open a public issue.** Report privately through GitHub:
[Report a vulnerability](https://github.com/JFrusher/Threadline/security/advisories/new).

Include what you can of:

- the Threadline version or commit,
- a minimal project or command that shows the problem,
- what you expected and what happened,
- the impact as you see it (for example "an unregistered key's approval passes TL-D03").

The maintainer will acknowledge your report and keep you updated. Once a fix is ready we'll agree a disclosure
date with you and credit you in the advisory, unless you'd rather not be named.

## In scope

Anything that makes Threadline's output untrustworthy, including:

- approvals or signer-registry changes accepted without a valid signature from a registered key (TL-D01, TL-D03,
  TL-D04),
- verification evidence miscounted, such as a failing or skipped test treated as a pass,
- hash checks bypassed (approvals, baselines, model weights, datasets),
- item content escaping into the PDF toolchain (LaTeX, HTML, file inclusion),
- the release workflow running project code with publish permissions.

`tests/test_attacks.py` holds the exploits found and fixed so far; it's a good guide to what we consider serious.

## Out of scope

- Vulnerabilities in your own device software. Threadline's SBOM and OSV checks help you track those; they're yours
  to fix.
- Weak procedural controls in an adopting organisation, such as shared keys or unprotected branches. The
  [Part 11 gap analysis](docs/guides/part11-gap-analysis.md) lists the controls Threadline relies on.

## Supported versions

Threadline is pre-1.0. Fixes land on `main` only.
