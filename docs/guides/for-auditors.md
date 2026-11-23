# Threadline for auditors and reviewers

You've been handed a technical file built with Threadline, or access to a repository that uses it. This page explains
what you're looking at, what the tool did and did not establish, and how to verify a release independently.

> [!NOTE]
> Threadline is tooling a manufacturer adopted, not a certified system. The manufacturer remains responsible for
> validating it (ISO 13485 §4.1.6) and for every judgement in the file. Treat its output as you would any other
> validated tool's output.

## What a release contains

Each release is a GitHub Release for one git tag, holding:

| File | Purpose |
|---|---|
| `technical-file.pdf` | The technical file. Every page footer shows product, version and commit. |
| `hazard-log.md` | Clinical risk hazard log in the DCB0129 structure. |
| `junit.xml` | Raw test results from the run on the tagged commit. Its SHA-256 is printed in the PDF. |
| `sbom.cdx.json` | CycloneDX software bill of materials, used for the SOUP section. |
| attestation | GitHub build-provenance attestation over each file above. |

The release workflow refuses to produce these if any rule had a finding, if any rule was skipped for lack of input,
or if the design file changed after the release baseline was approved.

## What the tool established

For the release commit, every rule in the "Threadline rule results" section passed. That means, for example: every
software requirement and risk control is linked to at least one test and every such test passed in that run; every
hazard's risk was estimated with the manufacturer's stated policy; every effective document carried the required
approvals, each in a commit SSH-signed by a registered key. The [rules reference](../reference/rules.md) states each
rule precisely, and each has a failing fixture proving it can fail.

## What it did not establish

- That the content is correct: estimates, rationales, clinical claims, test adequacy.
- That the clause mappings in the profiles are complete. Some were transcribed without the licensed text; every run
  prints a note saying so.
- Procedural controls outside git: who may administer the repository, how keys were issued, identity checks. The
  [Part 11 gap analysis](part11-gap-analysis.md) lists these.

## Reading signatures in the PDF

The "Signatures (21 CFR 11.50 manifestation)" table lists every approval: document, revision, signer's name, meaning
(`authored`, `reviewed`, `approved_as_qa`, `released`), signing time and the signing commit. Behind each row is an
approval record in `records/approvals/` that:

- names the document, its revision, and the SHA-256 of its content and identity,
- was added in exactly one commit, SSH-signed by the named signer's key,
- used a key that was in the signer registry *before* that commit,
- has not changed since.

The `signed_at` field is written by the signer; the commit time and signature are the trustworthy times. Compare them
if timing matters.

## Verify a release yourself

You need git, `ssh-keygen` (OpenSSH 8.2+), and optionally the GitHub CLI.

**1. Check the files came from the manufacturer's workflow.**

```bash
gh attestation verify technical-file.pdf --repo <owner>/<repo>
```

**2. Check out the exact commit printed in the PDF footer.**

```bash
git clone https://github.com/<owner>/<repo> && cd <repo> && git checkout <commit>
```

**3. Check a signature by hand.** Find the commit that added an approval record (it should be exactly one), then
verify it against the signer registry as it was just before that commit:

```bash
git log --format=%H -- records/approvals/APR-SOP-01-r2-approved-as-qa-quinn.yaml
```

```bash
git show <commit>^:qms/signers/allowed_signers > /tmp/allowed_signers
```

```bash
git -c gpg.ssh.program=ssh-keygen -c gpg.ssh.allowedSignersFile=/tmp/allowed_signers log -1 --show-signature <commit>
```

Look for `Good "git" signature for quinn`. Setting `gpg.ssh.program` makes git use OpenSSH directly, whatever your
own git configuration says; Threadline does the same.

**4. Re-run every rule.** With Python 3.12+, at the same commit:

```bash
pip install pytest "threadline @ git+https://github.com/JFrusher/Threadline@<version-the-manufacturer-pinned>"
```

```bash
pytest --junitxml=junit.xml && threadline check --junit junit.xml --trust-root <trust-root-commit>
```

Ask the manufacturer for the trust-root commit (it's an admin-held repository variable). The output should end
`0 finding(s)`. The rules that need an SBOM or a release version are skipped here; the release workflow ran them.

**5. Rebuild the traceability matrix** to compare with the PDF:

```bash
threadline rtm --junit junit.xml
```

## Try it on the example

The repository ships a fictional device, Breathe-Triage, whose design file passes every rule. It's a safe place to
see what a complete file looks like, and what each rule reports when you break something. Its data is illustrative and
says so on the cover. See the [README](../../README.md#the-worked-example).
