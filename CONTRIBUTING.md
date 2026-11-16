# Contributing

- One change per PR. Each PR names the plan step it closes (e.g. `PLAN 2.3`).
- Every validator rule lands with a passing fixture **and** a failing fixture under `tests/fixtures/<rule-id>/`.
  That suite is Threadline's own tool-validation evidence, so a rule without both fixtures is not done.
- Regulatory claims in templates must cite a source listed as **Verified** in `docs/PRD.md` §11.
- Run `uv run ruff check && uv run pytest` before pushing.
