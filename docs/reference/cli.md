# CLI reference

```text
threadline {check,rtm,build,init,preset,approve,baseline,hash} ...
```

Every command exits 0 on success. `check` exits 1 when there is any finding. Errors that stop a command (a missing
file, a refused build) print one line and exit non-zero.

## Shared options: `check`, `rtm`, `build`

These three commands load the same project and take the same inputs.

| Option | Meaning |
|---|---|
| `root` | Project directory holding `threadline.yaml`. Default: current directory. |
| `--junit FILE` | JUnit XML with `verifies` properties. Repeat to combine several files. Enables TL-E01, TL-E02, TL-R04. |
| `--sbom FILE` | CycloneDX JSON SBOM (for example from Syft). Enables TL-P01, TL-P02. |
| `--osv` | Query OSV.dev for advisories against the SBOM's components. Needs `--sbom` and network access. Enables TL-P03. |
| `--base REF` | Git ref to diff documents against, such as `origin/main`. Enables TL-D02. |
| `--release VERSION` | The version being released. Enables TL-D05 (needs an approved baseline). |
| `--trust-root COMMIT` | Commit whose signer registry is trusted. Pass an admin-set CI variable, never a value a pull request controls. |

TL-D03 and TL-D04 run automatically when the project is inside a git work tree.

## `threadline check`

Run every rule and print the findings.

```bash
threadline check --junit junit.xml --base origin/main --trust-root "$THREADLINE_TRUST_ROOT"
```

| Option | Meaning |
|---|---|
| `--format text` | Default. One line per finding: `RULE [clause] ITEM: message`. |
| `--format github` | GitHub Actions annotations (`::error file=…`), shown inline on the pull request's changed files. |

Output ends with a per-rule summary and a count:

```text
by rule: TL-E01 2 (Every software requirement has tests and all of them pass), TL-R04 1 (...)
3 finding(s), 5 rule(s) skipped, 200 items
```

The run also prints a `NOTE` (or `DRAFT STANDARD`) line about the lifecycle profile, and a reminder when no
`--trust-root` was given.

## `threadline rtm`

Print the requirements traceability matrix as Markdown: each software requirement with its system requirement, user
need, risk controls and tests (PASS/FAIL), then each hazard with its controls, implementing requirements and tests.

```bash
threadline rtm --junit junit.xml > rtm.md
```

## `threadline build`

Build the technical file PDF and a DCB0129 hazard log. Refuses to build while there is any finding.

```bash
threadline build --junit junit.xml --sbom sbom.cdx.json --osv --release v1.2.0 \
  --trust-root "$THREADLINE_TRUST_ROOT" --out dist/technical-file.pdf
```

| Option | Meaning |
|---|---|
| `--out FILE` | PDF path. Default `dist/technical-file.pdf`. The hazard log is written next to it as `hazard-log.md`. |
| `--version V` | Version printed on the cover and footers. Default: `git describe --tags --always`. |
| `--tool-validation FILE` | JUnit XML of Threadline's own test suite, rendered as the tool validation report. |
| `--chromium PATH` | Chromium executable for mermaid-cli, if it can't find one. |

With `--release`, `build` also requires `--trust-root` and refuses if any rule other than TL-D02 was skipped.

Requires on `PATH`: `pandoc`, `xelatex` (with the `lmodern` and `texlive-fonts-recommended` packages), and `mmdc`
(`@mermaid-js/mermaid-cli`) when any document contains a Mermaid diagram.

## `threadline init <dir>`

Create a new QMS repository from the template. The directory must be empty or not exist.

Writes `threadline.yaml`, ten SOPs, CI workflows pinned to the installed Threadline version, a PR template,
CODEOWNERS, a requirement stub for every checklist clause of the default profiles, and a JSON Schema for editor
autocompletion in `.vscode/`.

## `threadline preset add <name> [root]`

Copy a preset pack into the project: hazards, risk controls and requirements into `dhf/presets/<name>/`, failing test
stubs into `tests/presets/`.

| Preset | Contents |
|---|---|
| `power-loss` | Assessment lost or corrupted on power failure; starting on a nearly empty battery |
| `offline-queue` | Duplicate, lost or unnoticed unsynced records after offline use |
| `low-bandwidth-telemetry` | Truncated payloads accepted; retry storms draining battery or data |
| `ml-34971` | Biased training data, drift, over-trust and test-data leakage (BS/AAMI 34971) |

Each hazard cites its published source in `references`. Estimate severity, P1 and P2 against your own policy and
implement the stubs.

## `threadline approve ID... --meaning M --signer S`

Write approval records for the current revision of each document or baseline, and commit them in one SSH-signed
commit.

```bash
threadline approve SOP-01 SOP-02 --meaning approved_as_qa --signer quinn
```

| Option | Meaning |
|---|---|
| `ID...` | Document or baseline IDs. |
| `--meaning` | `authored`, `reviewed`, `approved_as_qa` or `released`. |
| `--signer` | Your name in `threadline.yaml` `signers:` and `qms/signers/allowed_signers`. Must hold the role the meaning needs. |
| `--message` | Extra text for the commit message. |
| `--root` | Project directory. Default: current directory. |

Records are named `APR-<id>-r<rev>-<meaning>-<signer>.yaml`. Git must be configured to sign with SSH
(`gpg.format=ssh`, `user.signingkey`). An existing record is never overwritten.

## `threadline baseline VERSION [root]`

Freeze the design file for a release: writes `records/baselines/BL-<VERSION>.yaml` with the SHA-256 of every item
file except approvals and baselines. Commit it, then sign it:

```bash
threadline approve BL-v1.2.0 --meaning released --signer rita
```

## `threadline hash <file>`

For a Markdown document: the hash an approval signs (id, doc_type, title, rev and body). For any other file, such as
a dataset split or model weights: its SHA-256, to paste into `sha256` or `weights_sha256`.
