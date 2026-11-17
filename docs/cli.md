# CLI reference

```text
threadline check    [root] [shared options] [--format text|github]
threadline rtm      [root] [shared options]
threadline build    [root] [shared options] [--out PDF] [--version V] [--tool-validation F] [--chromium PATH]
threadline approve  ID... --meaning M --signer S [--root DIR] [--message TEXT]
threadline baseline VERSION [root]
threadline init     <target>
threadline preset add <name> [root]
threadline hash     <file>
```

`root` is the directory holding `threadline.yaml`. It defaults to the current directory.

## Shared options

`check`, `rtm` and `build` take the same inputs.

| Option | Meaning |
|---|---|
| `--junit FILE` | JUnit XML carrying `verifies` properties. Repeat it to combine several test runs. Without it, the rules that need evidence are skipped |
| `--sbom FILE` | CycloneDX JSON SBOM. Enables TL-P01 and TL-P02 |
| `--osv` | Query OSV.dev for advisories against the SBOM components. Enables TL-P03. Requires `--sbom` and network access |
| `--base REF` | Git ref to compare documents against, for example `origin/main`. Enables TL-D02. Requires a git work tree |
| `--trust-root COMMIT` | Commit whose signer registry is trusted. TL-D04 checks every registry change after it. Without it, the registry's first commit is trusted and `check` prints a note saying so. Pass it from an admin-set CI variable, never from a value a pull request can change |
| `--release VERSION` | Version being released. Enables TL-D05, which needs an effective baseline for that version |

## `threadline check`

Runs every rule and prints one line per finding, one line per skipped rule, a count of findings per rule,
and a summary.

```text
TL-E01 [IEC 62304 5.7] SRS-004: no test verifies this item
skipped TL-P01 (Every SBOM component has an effective SOUP entry for that version): needs sbom

by rule: TL-E01 1 (Every software requirement has tests and all of them pass)
1 finding(s), 5 rule(s) skipped, 200 items
```

The first line of output is the note attached to the active lifecycle profile. With the Ed2 draft profile it
starts with `DRAFT STANDARD:`.

`--format github` prints each finding as a GitHub Actions error annotation, so it appears on the changed
file in the pull request. The GitHub Action uses it.

Exit status is 0 when there are no findings and 1 otherwise. Skipped rules do not affect it.

## `threadline rtm`

Prints two Markdown tables to standard output: the requirements traceability matrix (software requirement,
system requirement, user need, risk controls, tests) and risk control traceability (hazard, risk control,
implementing requirements, tests).

```bash
threadline rtm --junit junit.xml > rtm.md
```

## `threadline build`

Runs every rule. If there is any finding it prints them and stops without writing anything. Otherwise it
writes the technical file PDF to `--out` and `hazard-log.md` (DCB0129 layout) beside it.

With `--release`, it also refuses unless `--trust-root` is given and every rule except TL-D02 ran, so pass
`--junit`, `--sbom` and `--osv` and build inside the git work tree.

| Option | Meaning |
|---|---|
| `--out PDF` | Output path. Default `dist/technical-file.pdf` |
| `--version V` | Version printed on the cover and in page footers. Default: `git describe --tags --always` |
| `--tool-validation FILE` | JUnit XML of Threadline's own test suite, rendered as the tool validation section |
| `--chromium PATH` | Chromium executable for mermaid-cli |

The build shells out to Pandoc with the XeLaTeX engine and DejaVu fonts, and to mermaid-cli (`mmdc`) when a
document contains a Mermaid diagram. On Ubuntu 24.04 this set of packages builds the example:

```bash
sudo apt-get install -y --no-install-recommends pandoc texlive-xetex texlive-latex-recommended texlive-fonts-recommended lmodern fonts-dejavu-core
```

```bash
npm install -g @mermaid-js/mermaid-cli@11.4.2
```

## `threadline approve`

Signs documents or a baseline. For each ID it writes an approval record for the subject's current revision
to `records/approvals/APR-<id>-r<rev>-<meaning>-<signer>.yaml`, then commits all of them in one SSH-signed
commit.

```bash
threadline approve SOP-01 SOP-02 --meaning approved_as_qa --signer quinn
```

| Option | Meaning |
|---|---|
| `--meaning` | `authored`, `reviewed`, `approved_as_qa` or `released` |
| `--signer` | Your principal in `qms/signers/allowed_signers`. Must hold the role the meaning needs |
| `--root DIR` | Project root. Default `.` |
| `--message TEXT` | Extra text for the commit message |

It refuses if a record with that name already exists: approvals are immutable. Your git configuration must
be set up for SSH signing; see [branch protection and signing](guides/branch-protection.md).

## `threadline baseline`

Writes `records/baselines/BL-<version>.yaml`, an effective baseline holding the SHA-256 of every item file
except approvals and baselines. Commit it, then sign it:

```bash
threadline baseline v1.2.0
```

```bash
threadline approve BL-v1.2.0 --meaning released --signer rita
```

Any later change to the design file makes TL-D05 fail for that release.

## `threadline init`

Creates a new repository from the template in `target`, which must be empty or absent. The generated
workflows pin Threadline to the version that ran `init`. See [Getting started](getting-started.md) for what
it contains.

## `threadline preset add`

Copies a preset pack into `dhf/presets/<name>/` and its test stubs into `tests/presets/`. Names:
`power-loss`, `offline-queue`, `low-bandwidth-telemetry`, `ml-34971`. It refuses to add a preset twice.
See [presets](concepts.md#presets).

## `threadline hash`

For a `.md` document, prints the hash an approval signs: SHA-256 over the document's ID, `doc_type`, title
and revision together with its body. This is the value `subject_sha256` must hold.

For any other file, prints the SHA-256 of its bytes. This is the value for a dataset's `sha256` entries and
a model's `weights_sha256`.

```bash
threadline hash qms/SOP-01.md
```

## pytest plugin

Installing Threadline registers a pytest plugin with one marker:

```python
@pytest.mark.verifies("SRS-001", "RC-002")
```

It writes a `verifies` property per ID into the JUnit XML. The marker needs at least one ID, and pytest must
be configured with `junit_family = xunit1`; the plugin stops the run otherwise.
