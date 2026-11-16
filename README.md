# Threadline

QMS-as-code for Software as a Medical Device (SaMD).

Regulatory artifacts live in git as one YAML file per item. The `threadline` CLI and GitHub Action check the
digital thread — user need → requirement → risk control → passing test → signed release — and compile an
audit-ready technical file.

Target markets: **UK (MHRA)** and **Africa (AU Model Law on Medical Products Regulation / WHO GMRF baseline)**.

> **Disclaimer.** Threadline is not a certified quality management system and does not make any device
> compliant. It is tooling that a manufacturer's QMS may adopt, and the manufacturer must validate it for
> its own intended use (ISO 13485:2016 §4.1.6). The example device in `examples/` is fictional; its
> clinical and usability data are illustrative only.

Status: pre-alpha. See [docs/PRD.md](docs/PRD.md) and [docs/PLAN.md](docs/PLAN.md).

## Licences

- Code (`src/`, `tests/`, workflows): [Apache-2.0](LICENSES/Apache-2.0.txt)
- Templates, SOPs, example DHF and docs (`templates/`, `examples/`, `docs/`): [CC-BY-4.0](LICENSES/CC-BY-4.0.txt)
