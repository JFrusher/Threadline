# ADR-003: Approvals are signed records in git

**Status:** accepted · 2026-11-16

## Context
ISO 13485 §4.2.4 needs documents reviewed and approved before issue. Part 11 (our design benchmark) needs a
signature that shows name, time and meaning (§11.50), is bound to the record (§11.70) and is unique to one person
(§11.100). GitHub PR approvals live outside the repository and are not bound to document content.

## Decision
- An approval is an item (`type: approval`) naming the subject, its `rev`, the SHA-256 of its content, the
  meaning and the signer.
- The commit that **adds** the approval file must carry a valid **SSH** signature from a key listed for that
  signer in `qms/signers/allowed_signers`. Signer roles live in `threadline.yaml`.
- CI verifies signature, role, independence (signer ≠ author for review/approval meanings) and hash binding.
  The hash covers the document's id, doc_type, title and rev as well as its body.
- **Chain of trust for the registry.** A signature is checked against `allowed_signers` *as it was in the parent
  of the signing commit*, so a key added later cannot validate earlier approvals and a key cannot approve in the
  commit that adds it. The registry's first commit is the root of trust. Every later change to
  `allowed_signers` or to `signers:` in `threadline.yaml` must be SSH-signed by a key that the previous registry
  trusted and that belongs to a `qa` signer (TL-D04). Uncommitted registry changes are findings.
- **Release.** A `baseline` item holds the SHA-256 of every item file except approvals and baselines.
  A `released` approval of it, by a `release_manager`, is required by `build --release` (TL-D05).
- SSH signing only. GPG is not supported: one mechanism, no keyserver trust model, and `ssh-keygen` ships everywhere.
- PR approvals and branch protection remain process controls, not signature records.

## Consequences
- Signatures can be verified offline from the repo alone.
- Squash or rebase merges rewrite commits and drop signatures. Repos must merge approval PRs with merge commits
  or fast-forward (documented in the branch-protection guide).
