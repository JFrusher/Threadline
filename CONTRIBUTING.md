# Contributing

Questions and bug reports go in [issues](https://github.com/JFrusher/threadline/issues). A useful bug report
has the command you ran, the output, and the smallest set of item files that reproduces it. A wrong clause or
citation has its own issue form. Security problems go through [SECURITY.md](SECURITY.md), not issues.

## Setup

```bash
uv sync
```

```bash
uv run ruff check && uv run pytest
```

The signature tests need `ssh-keygen` on your PATH, and the security tests need `pandoc`.
`tests/test_build.py` also builds a PDF, which needs the full toolchain listed in the
[CLI reference](docs/cli.md#threadline-build).

## Pull requests

- One change per PR. Each PR names the plan step it closes (for example `PLAN 2.3`); the steps are in
  [docs/PLAN.md](docs/PLAN.md).
- A PR that adds approval records must be merged with a merge commit, not squashed: TL-D03 verifies the
  signed commit that added each record ([ADR-003](docs/adr/ADR-003-signed-approval-records.md)).

## Adding or changing a rule

1. Register it with `@rule(id, clause, title, needs)` in the matching file under `src/threadline/checks/`.
2. Add `tests/fixtures/<rule-id>.yaml` with a `pass` project and a `fail` project. A rule without both is not
   done: this suite is Threadline's own tool-validation evidence, and adopters rely on it.
3. Regenerate the table in [docs/rules.md](docs/rules.md) from `threadline.rules.rule_table()`.
   `tests/test_readme.py` fails until you do.
4. Keep the worked example green: `examples/breathe-triage` must pass every rule.

## Regulatory claims

A claim about a standard or regulation in a template, profile or SOP must cite a source listed as
**Verified** in [docs/PRD.md](docs/PRD.md) §11. If you cannot verify it against a primary source, say so in
the text, as the lifecycle profile notes do.

## Graphics

The README's terminal recordings replay real command output captured in
[`docs/assets/tapes/`](docs/assets/tapes). When CLI output changes, recapture the tapes with the commands listed
in [`docs/assets/make_gifs.py`](docs/assets/make_gifs.py) and run it. The technical-file preview is four pages of
the example's built PDF; the banners are hand-written SVG with light and dark variants. Do not edit the GIFs by
hand.

## Licence

Code contributions are licensed Apache-2.0. Templates, SOPs, presets, example content and docs are
CC-BY-4.0.
