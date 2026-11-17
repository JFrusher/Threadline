# Getting started

This page takes a new repository from the first red `threadline check` to one fully traced requirement.
It assumes Python 3.12 or newer, git, and pytest.

## 1. Install

```bash
pip install git+https://github.com/JFrusher/threadline
```

## 2. Scaffold

```bash
threadline init my-qms && cd my-qms
```

Commit the scaffold before running any check. The commit that first adds `qms/signers/allowed_signers` is
the root of trust for your signer registry, and `threadline check` needs at least one commit to read history
from.

```bash
git init && git add -A && git commit -m "QMS scaffold"
```

You get:

```text
threadline.yaml            product, software class, profiles, risk policy, signers
dhf/                       design history: needs, sys, srs, risk (empty)
qms/SOP-01.md … SOP-10.md  ten procedures, status draft
qms/signers/allowed_signers
records/approvals/         signed approval records go here
tests/test_example.py      one placeholder test
.github/                   workflows, PR template, CODEOWNERS
.vscode/                   JSON Schema for item files (autocompletion in VS Code)
```

> [!NOTE]
> The scaffolded workflows pin Threadline to the version that ran `init`, with
> `pip install "threadline==<version>"` and `uses: JFrusher/threadline@v<version>`. Until that version is
> published to PyPI and tagged, change them to the git URL above and to `@main`.

## 3. Run the first check

```bash
pytest --junitxml=junit.xml
```

```bash
threadline check --junit junit.xml
```

It fails with dozens of findings. Together they list what your configuration requires: lifecycle deliverables for
class C (TL-C01), one clause-map item per checklist clause of the active regulatory profiles (TL-G01), and a
classification for each market (TL-G02). The remaining finding, TL-E02, says the placeholder test claims to
verify `SRS-001`, which does not exist yet.

Edit `threadline.yaml` first: set `product`, `software_class` and `regulatory_profiles` to match your device.
A class A device with one market has a much shorter list.

## 4. Add one traced requirement

Each item is a YAML file whose name is its ID. Links live on the child and point upward.

`dhf/needs/UN-001.yaml`

```yaml
id: UN-001
type: user_need
title: Count breathing rate
text: A health worker needs to count a child's breaths over one minute.
```

`dhf/sys/SYS-001.yaml`

```yaml
id: SYS-001
type: system_requirement
title: Timed breath count
text: The system shall count breaths over a 60 second window.
derives_from: [UN-001]
```

`dhf/srs/SRS-001.yaml`

```yaml
id: SRS-001
type: software_requirement
title: Count from taps
text: The software shall compute rate as the number of taps within the 60 second window.
derives_from: [SYS-001]
```

Then link a real test to it in `tests/`:

```python
import pytest

@pytest.mark.verifies("SRS-001")
def test_rate_counts_taps_in_window():
    ...
```

Run the two commands from step 3 again. TL-E02 is gone, and so is the TL-C01 finding for clause 5.2.

`pytest.ini` in the scaffold sets `junit_family = xunit1`. Keep it: the default `xunit2` format has no
per-test properties, and the plugin stops the run if it is changed.

## 5. Add a hazard and its control

`dhf/risk/HAZ-001.yaml`

```yaml
id: HAZ-001
type: hazard
title: Truncated count
hazard: Count ends before the full window
sequence_of_events: Rate computed from a count shorter than 60 seconds
hazardous_situation: Fast breathing is missed
harm: Untreated pneumonia
severity: catastrophic
p1: medium
p2: medium
controls: [RC-001]
residual: {p1: very_low, p2: low}
```

`dhf/risk/RC-001.yaml`

```yaml
id: RC-001
type: risk_control
title: Full count only
kind: inherent_safety_by_design
text: Reject any count shorter than the full window.
new_risk_review: 'Reviewed: no new hazards introduced.'
```

`check` now reports that the control is not implemented by a requirement (TL-R03) and not verified by a test
(TL-R04). Add `implements: [RC-001]` to a software requirement and add `"RC-001"` to a test's `verifies`
marker to clear both.

Severity and probability names come from the `risk` policy in `threadline.yaml`. The shipped 5x5 matrix is
an example; replace it with your own policy.

## 6. Carry on from the worked example

[`examples/breathe-triage`](../examples/breathe-triage) passes every rule and has at least one item of each
type you will need: architecture items, classification, clause maps, usability file, threat model, ML model,
SOUP, QMS records and signed approvals. Copy its shapes.

To see the traceability matrix at any point:

```bash
threadline rtm --junit junit.xml
```

For risk packs covering common low-resource failure modes, see [presets](concepts.md#presets).

## Next

- [Concepts](concepts.md) for every item type and link
- [CI and releases](ci-and-releases.md) to gate pull requests and publish a technical file
- [Branch protection and signing](guides/branch-protection.md) before you make any document `effective`
