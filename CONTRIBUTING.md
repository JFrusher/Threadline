# Contributing to Threadline

Thanks for helping. Threadline is used to argue that medical device software is safe, so the bar for changes is a
little higher than usual: every rule must be proven to fail, and every regulatory claim must have a source. This page
explains how to meet that bar without fuss.

## Ways to help

- **Correct a regulatory claim.** A wrong clause number or an outdated requirement is the most valuable thing you can
  report. [Open a regulatory claim issue](https://github.com/JFrusher/Threadline/issues/new?template=regulatory-claim.yml)
  with your source.
- **Report a bug** with the command you ran and its output.
- **Propose a rule, preset or profile.** Open a feature request first, so we can agree on the clause and the fixtures
  before you write code.
- **Improve the docs.** Small fixes can go straight to a pull request.

Found a security problem? Please don't open an issue; see [SECURITY.md](SECURITY.md).

## Set up

You need Python 3.12+, [uv](https://docs.astral.sh/uv/), git and OpenSSH. Building the PDF also needs Pandoc,
XeLaTeX and mermaid-cli, but only the build tests use them.

```bash
git clone https://github.com/JFrusher/Threadline && cd Threadline && uv sync
```

```bash
uv run ruff check && uv run pytest
```

Clone with full history: the example's approvals are verified from their signed commits.

## Ground rules

1. **One change per pull request.** If it closes a step in [docs/PLAN.md](docs/PLAN.md), name it (`PLAN 2.3`).
2. **Every rule has a passing and a failing fixture** in `tests/fixtures/<RULE-ID>.yaml`. That suite is Threadline's
   tool-validation evidence, so a rule without both isn't done.
3. **Regulatory claims cite a verified source.** Anything in templates, SOPs, presets or profiles must trace to a
   source marked **Verified** in the [PRD evidence ledger](docs/PRD.md#11-evidence-ledger--what-is-verified-and-what-is-not).
   Add the source to the ledger in the same pull request. If you can't verify it, it doesn't ship.
4. **Fix root causes, with evidence.** For a bug, first add a test that fails for the reason you think it does, then
   fix it. The history of `tests/test_attacks.py` shows the pattern.
5. **Keep it simple.** One way to do each thing. No options nobody asked for.

## Adding a rule

1. Write the function in the matching module of `src/threadline/checks/`, decorated with
   `@rule("TL-X01", "<clause>", "<one-line check>", needs=...)`.
2. Add `tests/fixtures/TL-X01.yaml` with a passing and a failing project.
3. Regenerate the README rule table: paste the output of
   `uv run python -c "from threadline.rules import rule_table; print(rule_table())"` over the old table.
   `tests/test_readme.py` fails until you do.
4. Add the rule to [docs/reference/rules.md](docs/reference/rules.md) with how to fix it.
5. Make sure the example still passes: `uv run pytest tests/test_example.py`.

## The example's signatures

The approvals in `examples/breathe-triage` are SSH-signed by demo keys, and the example's trust root is a fixed
commit. Don't rewrite history on branches that contain them, and **merge pull requests with a merge commit**, never
squash or rebase, or TL-D03 fails on `main`.

## Commit and pull request style

- Short imperative subject with a type prefix, as in the existing history: `fix:`, `feat:`, `docs:`, `example:`,
  `ci:`, `chore:`.
- The body says why, and names the evidence for a fix.
- Fill in the pull request template.

## Licences

By contributing you agree that code is licensed under [Apache-2.0](LICENSES/Apache-2.0.txt), and templates, SOPs,
presets, example content and docs under [CC-BY-4.0](LICENSES/CC-BY-4.0.txt).

## Conduct

Everyone taking part follows the [code of conduct](CODE_OF_CONDUCT.md).
