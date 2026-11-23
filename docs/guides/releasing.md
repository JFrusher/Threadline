# Releasing and signing

This guide covers the human side of Threadline: registering people who can sign, approving documents, cutting a
release, and recovering from a lost key. The reasoning behind the design is in
[ADR-003](../adr/ADR-003-signed-approval-records.md); the Part 11 mapping is in the
[gap analysis](part11-gap-analysis.md).

## Roles

| Role | Signs | Typically |
|---|---|---|
| `author` | `authored` | The engineer or writer of a document |
| `reviewer` | `reviewed` | A peer who is not the author |
| `qa` | `approved_as_qa` | Quality lead; also guards the signer registry |
| `release_manager` | `released` | Whoever makes the release decision |

One person can hold several roles, but never review or QA-approve what they authored (TL-D01).

## 1. Set up SSH signing (each signer, once)

Use a passphrase-protected or hardware-backed key (Part 11 §11.200).

```bash
ssh-keygen -t ed25519 -f ~/.ssh/threadline_signing -C "quinn@example.com"
```

```bash
git config --global gpg.format ssh
```

```bash
git config --global user.signingkey ~/.ssh/threadline_signing.pub
```

Send the public key to your QA lead through a channel that lets them confirm it's yours.

## 2. Register signers

The QA lead adds each person in **one commit** to both files:

```yaml
# threadline.yaml
signers:
  ann: {name: Ann Author, roles: [author]}
  quinn: {name: Quinn QA, roles: [qa, reviewer]}
  rita: {name: Rita Release, roles: [release_manager]}
```

```text
# qms/signers/allowed_signers
ann ssh-ed25519 AAAAC3Nza... ann@example.com
quinn ssh-ed25519 AAAAC3Nza... quinn@example.com
rita ssh-ed25519 AAAAC3Nza... rita@example.com
```

The very first registry commit is the root of trust. Every later change must be committed with `git commit -S` by a
QA signer who was already registered (TL-D04). Record identity checks in a `training_record` or CAPA (SOP-09).

Then set the `THREADLINE_TRUST_ROOT` repository variable to that first commit's SHA (see [CI](ci.md)).

> [!CAUTION]
> Merge approval pull requests with a merge commit or fast-forward. Squash and rebase merges rewrite the signed
> commits, and every approval in them will fail TL-D03.

## 3. Approve documents

When a document is ready, set `status: effective` and ask the signers its `doc_type` needs:

```bash
threadline approve SOP-01 SOP-02 --meaning authored --signer ann
```

```bash
threadline approve SOP-01 SOP-02 --meaning approved_as_qa --signer quinn
```

Each command writes one record per document, bound to the document's current `rev` and content, and commits them all
in a single SSH-signed commit. `check` then verifies the signature, the key's registration date, the role, the
independence and the hash.

**Changing an effective document:** edit it, bump `rev`, and approve the new revision. Old approvals stay in history
as the record of the old revision. Forgetting the bump fails TL-D02 on the pull request.

## 4. Cut a release

```bash
threadline baseline v1.2.0
```

```bash
git add records/baselines && git commit -m "Baseline v1.2.0"
```

```bash
threadline approve BL-v1.2.0 --meaning released --signer rita
```

```bash
git tag v1.2.0 && git push origin main v1.2.0
```

The baseline freezes a hash of the whole design file. On the tag, the release workflow re-runs the tests, generates
the SBOM, queries OSV, and builds with `--release v1.2.0`. It refuses if any rule finds anything, if any rule was
skipped, if the baseline is missing or unapproved, or if anything in the design file changed after the baseline
was approved (TL-D05).

The GitHub Release then holds:

| File | What it is |
|---|---|
| `technical-file.pdf` | The technical file for this exact commit |
| `hazard-log.md` | DCB0129 hazard log |
| `junit.xml` | Verification evidence from the tagged commit |
| `sbom.cdx.json` | Software bill of materials |
| attestation | Build provenance for every file above |

## Revoking a signer

A QA signer removes the key line (and the role) in a signed commit. Approvals signed before stay valid, because each
is checked against the registry as it was when it was signed.

## Lost keys

**Lost an ordinary signer's key:** revoke it as above and register a new one. Nothing else changes.

**Lost the only QA key:** nobody can sign registry changes any more, so TL-D04 can't pass by the normal route. An
admin re-roots:

1. Commit the new registry (with a new QA key).
2. Record why in a CAPA.
3. Set `THREADLINE_TRUST_ROOT` to that commit.

Approvals signed before stay valid. Documents only need re-approval if their content or the approval policy changed.
Changing the variable is an admin-only act that GitHub records in the organisation audit log.

## Checking a release yourself

See the [auditor's guide](for-auditors.md#verify-a-release-yourself).
