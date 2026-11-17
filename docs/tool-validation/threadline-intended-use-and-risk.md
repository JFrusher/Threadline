# Threadline — intended use and tool risk assessment

Per ISO 13485:2016 §4.1.6 / §7.5.6, approach per ISO/TR 80002-2. Adopters copy this into their own SOP-10 records
and complete it for their configuration.

## Intended use
Threadline checks that a manufacturer's design history items in git are complete and linked (needs → requirements
→ risk controls → passing tests → approvals), checks SOUP against an SBOM, and compiles a technical file. It does
not decide whether a device is safe, classify a device, or replace review by qualified people.

## Failure modes and their effect

| Failure | Effect | Risk | Control |
|---|---|---|---|
| A rule passes on bad input (false negative) | Incomplete trace / unverified risk control could ship | High | Every rule has a failing fixture that must fail (tests/test_rules.py); suite runs on every change and ships per release |
| A rule fails on good input (false positive) | Wasted effort; pressure to bypass the tool | Low | Every rule has a passing fixture; dogfood test on the full example |
| Evidence misread (JUnit) | Untested item reported as tested | High | Only `verifies` properties count; skipped/failed/errored cases are not passes (TL-R04 fixture uses a skipped test); xunit2 refused |
| Signature mis-verified | Unauthorised approval accepted | High | Verification always via ssh-keygen with the repo's allowed_signers, ignoring user git config; unsigned, wrong-key, uncommitted and edited-after-signing fixtures |
| Wrong hash accepted | Approval or model weights not bound to content | High | Hash-mismatch fixtures for TL-D01 and TL-M02 |
| Profile data wrong (clause mapping) | Missing deliverable not flagged | Medium | Profile data marked unverified where not checked against licensed text; parse-guard tests; QA review of profiles before use |
| Untrusted item text reaches the PDF engine | Runner files leaked into a published PDF; content hidden | High | Raw LaTeX/HTML disabled in Pandoc; images must be project files (tests/test_attacks.py) |
| Self-registered signer key | Forged approvals | High | Registry chain of trust (TL-D04); signatures checked against the registry before the signing commit |
| PDF omits content | Auditor sees incomplete file | Medium | Section presence test; build refuses on any finding; JUnit and SBOM attached raw next to the PDF |

## Validation evidence
`tool-validation.xml` (JUnit of `pytest tests`) attached to each release and rendered in the technical file.
Re-validate on every Threadline version change; pin the version in workflows.
