"""Document control and electronic signatures (ISO 13485 4.2.4, ADR-003)."""

import hashlib

from threadline import git
from threadline.project import _split_frontmatter
from threadline.rules import Context, Finding, rule

# meaning -> signer role it needs
ROLE_FOR = {"authored": "author", "reviewed": "reviewer", "approved_as_qa": "qa", "released": "release_manager"}


def content_hash(body: str) -> str:
    return hashlib.sha256(body.replace("\r\n", "\n").strip().encode()).hexdigest()


@rule("TL-D01", "ISO 13485 4.2.4; 21 CFR 11.50, 11.70",
      "Effective documents carry the required approvals: right role, independent, bound to content")
def approvals(ctx: Context):
    cfg = ctx.project.config
    items = ctx.project.items
    apps = ctx.project.of_type("approval")
    for a in apps:
        subject = items.get(a.subject)
        if subject is None or subject.type != "document":
            yield Finding("TL-D01", a.id, f"subject {a.subject} is not a document")
        signer = cfg.signers.get(a.signer)
        if signer is None:
            yield Finding("TL-D01", a.id, f"signer {a.signer} is not in threadline.yaml signers")
        elif ROLE_FOR[a.meaning] not in signer.roles:
            yield Finding("TL-D01", a.id, f"{a.signer} lacks role {ROLE_FOR[a.meaning]} for {a.meaning}")
    for doc in ctx.project.of_type("document"):
        if doc.status != "effective":
            continue
        current = [a for a in apps if a.subject == doc.id and a.subject_rev == doc.rev]
        for a in current:
            if a.subject_sha256 != content_hash(doc.body):
                yield Finding("TL-D01", doc.id, f"{a.id} was signed for different content (hash mismatch)")
        meanings = {a.meaning for a in current}
        needed = cfg.approvals_required.get(doc.doc_type, cfg.approvals_required.get("*", []))
        for m in needed:
            if m not in meanings:
                yield Finding("TL-D01", doc.id, f"rev {doc.rev} has no '{m}' approval")
        authors = {a.signer for a in current if a.meaning == "authored"}
        for a in current:
            if a.meaning != "authored" and a.signer in authors:
                yield Finding("TL-D01", doc.id, f"'{a.meaning}' signed by the author {a.signer} (not independent)")


@rule("TL-D02", "ISO 13485 4.2.4", "A content change to an effective document comes with a revision bump",
      "base_ref")
def rev_bump(ctx: Context):
    for doc in ctx.project.of_type("document"):
        old_text = git.show(ctx.git_root, ctx.base_ref, doc.path)
        if old_text is None:
            continue
        old, old_body = _split_frontmatter(old_text)
        if old.get("status") == "effective" and content_hash(old_body) != content_hash(doc.body) \
                and doc.rev <= old.get("rev", 1):
            yield Finding("TL-D02", doc.id, f"content changed since {ctx.base_ref} but rev stayed {doc.rev}")


@rule("TL-D03", "21 CFR 11.70, 11.100; ADR-003",
      "Every approval record was committed once, in a commit SSH-signed by its signer", "git_root")
def signatures(ctx: Context):
    for a in ctx.project.of_type("approval"):
        commits = git.signed_commits(ctx.git_root, ctx.project.root, a.path)
        if not commits:
            yield Finding("TL-D03", a.id, "approval record is not committed")
        elif len(commits) > 1:
            yield Finding("TL-D03", a.id, "approval record was changed after signing; records are immutable")
        else:
            sha, status, principal = commits[0]
            if status != "G":
                yield Finding("TL-D03", a.id, f"commit {sha[:10]} has no valid signature from an allowed signer")
            elif principal != a.signer:
                yield Finding("TL-D03", a.id, f"commit {sha[:10]} signed by {principal}, record names {a.signer}")
            elif git.show(ctx.git_root, sha, a.path) != a.path.read_text(encoding="utf-8"):
                yield Finding("TL-D03", a.id, "file differs from the signed commit (edited after signing)")
