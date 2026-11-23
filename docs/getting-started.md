# Getting started

This tutorial takes a brand-new Threadline repository from its first red `check` to green. It takes about an hour,
most of it spent writing your own requirements. You'll learn each rule family by fixing what it reports.

You need Python 3.12+, git, and a terminal. You don't need to know the standards in advance: every finding names
the clause it comes from, and the [glossary](glossary.md) explains the jargon.

> [!TIP]
> Want to see a finished design file first? [`examples/breathe-triage`](../examples/breathe-triage) passes every
> rule. Keep it open in another tab; copying its shapes is the fastest way to write your own.

## 1. Install and create a repository

```bash
pip install pytest "threadline @ git+https://github.com/JFrusher/Threadline"
```

```bash
threadline init my-qms && cd my-qms
```

```bash
git init && git add -A && git commit -m "Start the QMS"
```

That first commit matters. Threadline reads approvals and the signer registry from git history, and the commit that
first adds `qms/signers/allowed_signers` becomes your root of trust ([ADR-003](adr/ADR-003-signed-approval-records.md)).
Running `check` in a repository with no commits fails with a git error.

Here's what `init` created:

```text
my-qms/
├── threadline.yaml            product, software class, markets, risk policy, signers
├── dhf/                       design history file: one YAML file per item
│   ├── needs/  sys/  srs/  risk/
│   └── regulatory/            one stub per checklist clause (ISO 13485, UK MDR, AU Model Law)
├── qms/
│   ├── SOP-01.md … SOP-10.md  standard operating procedures
│   └── signers/allowed_signers
├── records/approvals/         signed approval records land here
├── tests/test_example.py      a placeholder test to replace
├── pytest.ini                 junit_family = xunit1 (required)
├── .github/                   CI workflows, PR template, CODEOWNERS
└── .vscode/                   JSON Schema so your editor autocompletes item fields
```

## 2. Run the first check

```bash
pytest --junitxml=junit.xml && threadline check --junit junit.xml
```

You'll see 56 findings. Here is how to read one:

```text
TL-C01 [IEC 62304 (per lifecycle profile)] IEC 62304:2006+A1:2015 5.1: Software development planning (class C) needs doc_type sdp
```

| Part | Meaning |
|---|---|
| `TL-C01` | The rule that fired. Look it up in the [rules reference](reference/rules.md). |
| `[IEC 62304 (per lifecycle profile)]` | The clause the rule enforces. |
| `IEC 62304:2006+A1:2015 5.1` | The item or clause the finding is about. |
| `Software development planning (class C) needs doc_type sdp` | What is missing or wrong. |

The last line groups them, so you can see where the work is:

```text
by rule: TL-C01 7 (...), TL-E02 1 (...), TL-G01 46 (...), TL-G02 2 (...)
56 finding(s), 5 rule(s) skipped, 56 items
```

"Skipped" rules need an input you haven't given yet, such as an SBOM or a base branch. They run in CI.
[Rules reference](reference/rules.md) lists every rule with its fix.

## 3. Set up the project

Open `threadline.yaml`. Three settings shape everything else:

```yaml
product: My Device
lifecycle_profile: iec62304-ed1   # or iec62304-ed2-draft
software_class: C                 # A, B or C (Ed1); PRL-I or PRL-II (Ed2 draft)
regulatory_profiles: [uk-mhra, au-model-law]
```

The software class decides which IEC 62304 deliverables TL-C01 asks for. Class A asks for least. Drop a regulatory
profile you don't sell into, and its checklist findings go away (delete its stubs in `dhf/regulatory/` too).

> [!WARNING]
> The `risk:` block is an illustrative 5×5 policy. Replace it with the acceptability matrix from your own risk
> management procedure (SOP-03) before you estimate any hazards. See [Configuration](reference/configuration.md).

## 4. Write the thread

Start with one complete strand: a need, a system requirement, a software requirement, and a test.

```yaml
# dhf/needs/UN-001.yaml
id: UN-001
type: user_need
title: Count breathing rate reliably
text: A community health worker can obtain a child's respiratory rate without a timer.
```

```yaml
# dhf/sys/SYS-001.yaml
id: SYS-001
type: system_requirement
title: Guided 60-second count
text: The system shall time a 60-second count and report breaths per minute.
derives_from: [UN-001]
```

```yaml
# dhf/srs/SRS-001.yaml
id: SRS-001
type: software_requirement
title: Count duration
text: The count shall last 60 ± 0.5 seconds.
derives_from: [SYS-001]
```

Two things to notice. The filename is the ID, always. And links point **up**: the child names its parent. Nothing
points down, so adding a requirement never means editing its parent.

Now replace `tests/test_example.py` with a real test:

```python
import pytest

@pytest.mark.verifies("SRS-001")
def test_count_lasts_sixty_seconds():
    assert count_duration() == pytest.approx(60, abs=0.5)
```

The `verifies` marker is the only link between tests and items. Threadline does not read test names or docstrings
([ADR-002](adr/ADR-002-junit-property-test-link.md)). A failing, erroring or skipped test does not count as
verification.

Run the check again. TL-E02 is gone (your test now verifies an item that exists), and TL-C01 no longer asks for a
software requirement.

> [!TIP]
> Install the YAML extension for your editor. `init` wrote `.vscode/item.schema.json`, so VS Code autocompletes every
> field and flags typos before Threadline does.

## 5. Add risk

A hazard records the full ISO 14971 chain and your estimate against the policy:

```yaml
# dhf/risk/HAZ-001.yaml
id: HAZ-001
type: hazard
title: Fast breathing missed in infant
hazard: Wrong threshold applied to age band
sequence_of_events: Infant 2–11 months with RR 50–59 classified as no fast breathing
hazardous_situation: Health worker does not treat or refer
harm: Untreated pneumonia progresses
severity: catastrophic
p1: certain        # software failures: see software_p1_rule in threadline.yaml
p2: medium
controls: [RC-001]
residual: {p1: very_low, p2: low}
```

```yaml
# dhf/risk/RC-001.yaml
id: RC-001
type: risk_control
title: Exact age-banded thresholds
kind: inherent_safety_by_design
text: Implement thresholds with boundary tests at 11/12 months and 49/50 breaths.
new_risk_review: "Reviewed: no new hazards introduced."
```

Then make a software requirement implement the control (`implements: [RC-001]`) and tag a test with
`@pytest.mark.verifies("SRS-002", "RC-001")`. The risk rules now check that:

- the hazard is complete and uses levels from your policy (TL-R01),
- an unacceptable initial risk has a control (TL-R02),
- the control is implemented by a requirement (TL-R03) and verified by passing tests (TL-R04),
- the residual risk is acceptable, or justified by a benefit-risk statement (TL-R05),
- the control was reviewed for new hazards it introduces (TL-R06).

Building for a setting with unreliable power or connectivity? A preset adds a researched starting point:

```bash
threadline preset add power-loss
```

It copies hazards, controls and requirements into `dhf/presets/power-loss/` and failing test stubs into
`tests/presets/`. The stubs fail until you implement them, so the preset can't quietly pass.

## 6. Map the regulations

The 46 TL-G01 findings come from the stubs `init` wrote in `dhf/regulatory/`, one per checklist clause. Each needs
evidence, or a justification for why it doesn't apply:

```yaml
# dhf/regulatory/UKER-1.yaml
id: UKER-1
type: requirement
title: Safe in intended use; risks acceptable; reduce use error
source: UK MHRA (Great Britain) — UK MDR 2002
clause: ER 1
evidence: [SOP-03, HAZ-001, SUMR-001]
```

```yaml
applicable: false
justification: The device has no measuring function.
```

TL-G02 asks for one `classification` item per scheme your markets need (for example `uk-mhra` and `who-gmrf`), each
with the rule you applied and your rationale. Look at `examples/breathe-triage/dhf/regulatory/CLS-UK.yaml`.

## 7. Documents and approvals

SOPs and plans are Markdown with YAML frontmatter. When a document becomes `effective`, TL-D01 requires the
approvals your `approvals_required` policy names (by default: `authored` and `approved_as_qa`), each by someone with
the right role, and the QA approval by someone other than the author.

Approvals are SSH-signed commits. Register your signers, then sign:

```bash
git config gpg.format ssh && git config user.signingkey ~/.ssh/id_ed25519.pub
```

```bash
threadline approve SOP-01 SOP-02 --meaning authored --signer ann
```

[Releasing and signing](guides/releasing.md) walks through registering signers, approving and the trust root.

## 8. Green, then CI

When `check` prints `0 finding(s)`, push the repository to GitHub. The workflows `init` wrote will run `check` on
every pull request, annotate findings on the diff, and rebuild the technical file when you tag a release. Set up
branch protection next: [CI guide](guides/ci.md) and [branch protection](guides/branch-protection.md).

## Where next

- [Concepts](concepts.md): the model behind items, links, evidence and signatures.
- [Item types](reference/items.md): every field of every item.
- [Releasing and signing](guides/releasing.md): baselines, `released` approvals, the trust root, key loss.
