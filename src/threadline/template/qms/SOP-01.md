---
id: SOP-01
type: document
doc_type: sop
title: Document Control
rev: 1
status: draft
---
# SOP-01 Document Control

**Purpose.** Control documents and records required by the QMS (ISO 13485:2016 §4.2.4, §4.2.5).
**Scope.** Every Markdown document with `type: document` and every YAML item in `dhf/`, `qms/`, `records/`.

## Responsibilities
| Role | Duty |
|---|---|
| Author | Drafts and revises documents; signs `authored`. |
| Reviewer | Reviews content for adequacy; signs `reviewed` where required. Never the author. |
| QA | Approves before issue; signs `approved_as_qa`. Owns `threadline.yaml`, `qms/signers/`. |

## Procedure
1. **Identify.** Each document has a unique `id`, a `title`, a `rev` (integer) and a `status`
   (`draft` → `in_review` → `effective` → `obsolete`). The filename is the ID.
2. **Change.** All changes go through a pull request using the PR template. A content change to an `effective`
   document increases `rev` (enforced by TL-D02).
3. **Review and approve.** Signers compute the content hash with `threadline hash <file>` and commit an approval
   record in an SSH-signed commit (ADR-003, `docs/guides/branch-protection.md`). TL-D01/TL-D03 verify role,
   independence, content binding and signature.
4. **Issue.** A document becomes `effective` only when all approvals required for its `doc_type` exist for the
   current `rev`. The merged `main` branch is the controlled copy.
5. **Obsolete.** Set `status: obsolete`; never delete. Git history keeps every prior revision.
6. **External documents.** Standards and regulations are listed with edition in `requirement` items (`source`).
7. **Records.** Records (approvals, CAPA, complaints, reviews, training) are immutable once committed; corrections
   are new records referencing the old one.
8. **Retention.** Keep the repository and every release's technical file for at least the lifetime of the device
   as defined by the manufacturer, and not less than any period required by the target market.

## Records
Approval records (`records/approvals/`), git history, release technical files.
