# Running Threadline in CI

`threadline init` writes three GitHub Actions workflows into `.github/workflows/`. This page explains what each one
does and how to set them up. All third-party actions in them are pinned to commit SHAs.

| Workflow | Runs on | Does |
|---|---|---|
| `threadline.yml` | every pull request, pushes to `main` | Tests, then `threadline check` with inline annotations |
| `sbom.yml` | every pull request, and weekly | SBOM with Syft, then the SOUP and advisory rules |
| `release.yml` | tags `v*` | Rebuilds all evidence and publishes the technical file |

## Before the first run

1. **Set the trust root.** In *Settings → Secrets and variables → Actions → Variables*, create
   `THREADLINE_TRUST_ROOT` with the full SHA of the commit that created `qms/signers/allowed_signers`. Only admins can
   change repository variables, which is the point: a pull request author can't move it.
2. **Protect `main`.** Require the `threadline` check, and use merge commits, not squash.
   See [Branch protection](branch-protection.md).
3. **Check the install line.** The generated workflows install `threadline==<version>` from PyPI. Until Threadline
   is published there, change it to `"threadline @ git+https://github.com/JFrusher/Threadline@<commit-sha>"`, and
   point `uses: JFrusher/threadline@…` at the same commit.

> [!IMPORTANT]
> Check out with `fetch-depth: 0`. Signatures (TL-D03, TL-D04) and the revision check (TL-D02) read git history, and a
> shallow clone makes them fail. Threadline adds a hint to the finding when it detects one.

## The pull request check

```yaml
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pytest "threadline @ git+https://github.com/JFrusher/Threadline@<commit-sha>"
      - run: pytest --junitxml=junit.xml
      - uses: JFrusher/Threadline@<commit-sha>
        with:
          junit: junit.xml
          base: ${{ github.event_name == 'pull_request' && format('origin/{0}', github.base_ref) || '' }}
          trust-root: ${{ vars.THREADLINE_TRUST_ROOT }}
```

The action runs `threadline check --format github`, so each finding is an annotation on the file it's about.

### Action inputs

| Input | Default | Meaning |
|---|---|---|
| `path` | `.` | Project root (the directory holding `threadline.yaml`). |
| `junit` | empty | JUnit XML with evidence. Empty skips the evidence rules. |
| `base` | empty | Git ref to diff documents against. Empty skips TL-D02. |
| `trust-root` | empty | Commit whose signer registry is trusted. Pass an admin-set variable, never a value from the pull request. |

### Tests in other languages

Any framework that writes JUnit XML with a `verifies` property on the testcase works. Pass several files with
repeated `--junit` flags (on the CLI) or merge them first. GoogleTest example:

```cpp
TEST(Triage, InfantThreshold) {
  RecordProperty("verifies", "SRS-002");
  ...
}
```

## The SBOM check

`sbom.yml` generates a CycloneDX SBOM with Syft (`anchore/sbom-action`) and runs:

```bash
threadline check --sbom sbom.cdx.json --osv
```

It runs weekly as well as on pull requests, because new advisories appear without any code change. A new advisory
fails the workflow until someone writes a `vulnerability` triage record for it.

## The release workflow

On a `v*` tag, `release.yml` runs two jobs.

**evidence** (read-only token): checks out full history, installs Pandoc, XeLaTeX and mermaid-cli, re-runs the full
test suite on the tagged commit, generates the SBOM, and runs:

```bash
threadline build --release "$GITHUB_REF_NAME" --junit junit.xml --sbom sbom.cdx.json --osv \
  --version "$GITHUB_REF_NAME" --trust-root "$TRUST_ROOT" --out dist/technical-file.pdf
```

**publish** (write token, no project code runs): attests build provenance for every file and creates the GitHub
Release with the PDF, hazard log, JUnit evidence and SBOM.

Splitting the jobs means the code under test never holds a token that can publish a release.

> [!WARNING]
> The generated release workflows install TeX with `--no-install-recommends`. In a clean Ubuntu 24.04 container that
> leaves out the `lmodern` and `texlive-fonts-recommended` packages, and the PDF build fails with
> ``File `lmodern.sty' not found``. If you see that, add both packages to the `apt-get install` line.

How to cut a release is in [Releasing and signing](releasing.md).

## Other CI systems

The action is a thin wrapper. On any CI, install Threadline and run the same commands; use `--format text` (the
default) for plain output. Keep full git history and pass the trust root from a protected variable.
