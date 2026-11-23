# Configuration: `threadline.yaml`

One file at the project root configures everything. Unknown keys are rejected, so typos fail loudly.

```yaml
product: Breathe-Triage (fictional example device)
lifecycle_profile: iec62304-ed1
software_class: C
regulatory_profiles: [uk-mhra, au-model-law]
risk: { ... }            # see below
signers:
  ann: {name: Ann Author, roles: [author]}
  quinn: {name: Quinn QA, roles: [qa, reviewer]}
  rita: {name: Rita Release, roles: [release_manager]}
approvals_required:
  '*': [authored, approved_as_qa]
```

| Key | Required | Meaning |
|---|---|---|
| `product` | yes | Device name, printed on the technical file. If it contains "illustrative" or "fictional", the PDF is flagged as not for submission. |
| `item_dirs` | | Directories scanned for items. Default `[dhf, qms, records]`. |
| `lifecycle_profile` | yes | `iec62304-ed1`, or `iec62304-ed2-draft` (an unpublished draft; every run prints a `DRAFT STANDARD` banner). |
| `software_class` | yes | `A`, `B` or `C` with Ed1; `PRL-I` or `PRL-II` with the Ed2 draft. Decides which deliverables TL-C01 asks for. |
| `regulatory_profiles` | | Any of `uk-mhra`, `au-model-law`. The ISO 13485 clause map is always active. |
| `risk` | yes | Your ISO 14971 risk acceptability policy. |
| `signers` | | Who may sign, and in which roles. |
| `approvals_required` | | Which approval meanings an effective document needs, by `doc_type`. |

## `risk`

Levels are listed low to high. Threadline doesn't assume any scale: it checks your hazards against the policy you
write here, which should match your risk management procedure (SOP-03).

```yaml
risk:
  severity: [negligible, minor, serious, critical, catastrophic]
  p1: [very_low, low, medium, high, certain]   # probability the hazardous situation occurs
  p2: [very_low, low, medium, high]            # probability the situation leads to harm
  probability:                                  # P1 × P2 → combined probability
    very_low: {very_low: improbable, low: improbable, medium: improbable, high: remote}
    # ... one row per P1 level
  acceptability:                                # severity × probability → verdict
    catastrophic: {improbable: acceptable, remote: unacceptable, occasional: unacceptable, ...}
    # ... one row per severity
  software_p1_rule: >-
    P1 for a software failure is set to 'certain' unless a risk control external to the failing software item is
    cited.
```

Every P1/P2 combination needs a probability, and every severity/probability combination a verdict; a gap is a load
error. `software_p1_rule` is free text, printed in the technical file, stating how you estimate P1 for software
failures. Threadline requires you to state it but does not prescribe it.

> [!WARNING]
> The policy `threadline init` writes is an illustrative 5×5 example. Replace it with your own before estimating
> hazards.

## `signers` and roles

```yaml
signers:
  quinn: {name: Quinn QA, roles: [qa, reviewer]}
```

The key (`quinn`) is the signer's principal. It must match the name on their key in
`qms/signers/allowed_signers`, and it appears in approval record IDs, so it is limited to letters, digits, `.` and `-`.

| Meaning | Role required |
|---|---|
| `authored` | `author` |
| `reviewed` | `reviewer` |
| `approved_as_qa` | `qa` |
| `released` | `release_manager` |

The `qa` role also controls the signer registry: every change to `signers:` or `allowed_signers` after the first
commit must be signed by a QA signer who was already registered (TL-D04).

## `approvals_required`

```yaml
approvals_required:
  '*': [authored, approved_as_qa]          # default for every doc_type
  clinical_evaluation: [authored, reviewed, approved_as_qa]
```

An effective document needs every meaning listed for its `doc_type`, or for `'*'` if its type isn't listed. Baselines
always need `released`.

## `qms/signers/allowed_signers`

The standard OpenSSH allowed-signers format: one line per key, principal first.

```text
quinn ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... quinn@example.com
```

Change it only in a commit signed by a current QA signer. See [Releasing and signing](../guides/releasing.md).

## `pytest.ini`

```ini
[pytest]
junit_family = xunit1
```

Required. The `xunit2` JUnit format has no testcase properties, so it can't carry `verifies` links; the plugin
refuses to write evidence in it.
