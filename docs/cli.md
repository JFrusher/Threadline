# CLI reference

```text
threadline check  [root] [--junit F]... [--sbom F] [--osv] [--base REF]
threadline rtm    [root] [--junit F]... [--sbom F] [--osv] [--base REF]
threadline build  [root] [--junit F]... [--sbom F] [--osv] [--base REF]
                  [--out PDF] [--version V] [--tool-validation F] [--chromium PATH]
threadline init   <target>
threadline preset add <name> [root]
threadline hash   <file>
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

## `threadline check`

Runs every rule and prints one line per finding, one line per skipped rule, then a summary.

```text
TL-E01 [IEC 62304 5.7] SRS-004: no passing test verifies this requirement
skipped TL-P01 (Every SBOM component has an effective SOUP entry for that version): needs sbom
1 finding(s), 4 rule(s) skipped, 168 items
```

The first line of output is the note attached to the active lifecycle profile. With the Ed2 draft profile it
starts with `DRAFT STANDARD:`.

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

## `threadline init`

Creates a new repository from the template in `target`, which must be empty or absent. See
[Getting started](getting-started.md) for what it contains.

## `threadline preset add`

Copies a preset pack into `dhf/presets/<name>/` and its test stubs into `tests/presets/`. Names:
`power-loss`, `offline-queue`, `low-bandwidth-telemetry`, `ml-34971`. It refuses to add a preset twice.
See [presets](concepts.md#presets).

## `threadline hash`

For a `.md` file, prints the SHA-256 of the document body, ignoring frontmatter, line-ending style and
leading or trailing whitespace. This is the value for an approval's `subject_sha256`.

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
