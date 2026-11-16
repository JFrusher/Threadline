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
- SSH signing only. GPG is not supported: one mechanism, no keyserver trust model, and `ssh-keygen` ships everywhere.
- PR approvals and branch protection remain process controls, not signature records.

## Consequences
- Signatures can be verified offline from the repo alone.
- Squash or rebase merges rewrite commits and drop signatures. Repos must merge approval PRs with merge commits
  or fast-forward (documented in the branch-protection guide).
