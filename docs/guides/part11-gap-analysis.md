# 21 CFR Part 11 gap analysis — Threadline electronic signatures

Part 11 is US law. Threadline's target markets (UK, AU Model Law states) do not impose it on device QMS records;
Threadline uses it as the strictest common benchmark (PRD §4). This table states what the tool does, what the
adopting manufacturer must still do, and what is out of scope. Mechanism: ADR-003.

| Part 11 | Requirement (summary) | Threadline control | Manufacturer must |
|---|---|---|---|
| 11.10(a) | System validation | Rule fixtures = tool validation suite; report per release | Validate for own intended use (SOP-10) |
| 11.10(b) | Accurate, complete copies | Git repo + PDF technical file per tag | Keep releases accessible for retention period |
| 11.10(c) | Record protection & retrieval | Git history, signed release, provenance attestation | Back up the repository; set retention |
| 11.10(d) | Limit system access | — | GitHub org access control, 2FA, CODEOWNERS |
| 11.10(e) | Audit trail | Git commit history (author, time, change) | Forbid force-push and history rewrite on protected branches |
| 11.10(f) | Operational checks / sequencing | TL-D01 (required approvals before `effective`), TL-D02 (rev bump) | Branch protection requiring CI |
| 11.10(g) | Authority checks | Signer roles in `threadline.yaml`, TL-D01 role check | Control who may edit `threadline.yaml` and `qms/signers/` (CODEOWNERS: QA) |
| 11.10(h) | Device checks | — | Not applicable (no data-input devices) |
| 11.10(i) | Training | `training_record` items | Train signers on SOP-01 |
| 11.10(j) | Accountability policy | — | Written policy that SSH signatures are legally binding equivalents |
| 11.10(k) | Documentation controls | SOP-01, documents under TL-D01/D02 | — |
| 11.50 | Signature manifestation: name, date/time, meaning | Approval record holds signer, `signed_at`, `meaning`; printed in technical file | — |
| 11.70 | Signature/record linking | `subject_sha256` binds the signature to content; TL-D01 | — |
| 11.100(a) | Unique to one person | Key → principal in `allowed_signers`; TL-D03 | Never share keys; one principal per person |
| 11.100(b) | Verify identity before issuing | — | Identity check before adding a key (record in `training_record` or a CAPA-controlled change) |
| 11.100(c) | Certify to FDA | — | Only if marketing in the US |
| 11.200(a) | Two distinct components | GitHub authentication + signing-key passphrase (or hardware key) | Require passphrase-protected or hardware-backed keys |
| 11.300 | Password/ID controls | — | Key rotation and revocation: remove key from `allowed_signers` (date-bounded entries) |

## Known gaps
1. `signed_at` is written by the signer. The commit time and the signature's timestamp are the trustworthy times;
   reviewers should compare them. Threadline does not yet check that they agree.
2. Revoking a key: `allowed_signers` supports `valid-after`/`valid-before` options. Threadline relies on ssh-keygen to
   honour them; it does not check key validity windows itself.
