# Branch protection and simulated roles

Threadline simulates four roles. Use separate GitHub accounts (or a GitHub team per role) so that independence is real.

| Role (`threadline.yaml`) | Signs | GitHub team |
|---|---|---|
| `author` | `authored` | `@org/dev` |
| `reviewer` | `reviewed` | `@org/dev` (not the author) |
| `qa` | `approved_as_qa` | `@org/qa` |
| `release_manager` | `released` | `@org/release` |

## Settings on `main`
1. Require a pull request, 1 approving review, CODEOWNERS review.
2. Require status checks: `threadline check` (with `--base origin/main`) and the test job.
3. Require signed commits.
4. Block force pushes and deletion.
5. **Merge method: merge commit or rebase-free fast-forward only.** Squash merges create a new unsigned commit and
   TL-D03 will reject the approval records (ADR-003).

## CODEOWNERS
```
/threadline.yaml      @org/qa
/qms/                 @org/qa
/qms/signers/         @org/qa
/records/approvals/   @org/qa
/dhf/risk/            @org/qa @org/dev
```

## Signing an approval
```bash
git config gpg.format ssh
git config user.signingkey ~/.ssh/id_ed25519.pub
sha256=$(threadline hash qms/SOP-01.md)
# write records/approvals/APR-SOP-01-r2-qa.yaml with subject_sha256: $sha256, then:
git add records/approvals/APR-SOP-01-r2-qa.yaml && git commit -S -m "approve SOP-01 r2 (QA)"
```
