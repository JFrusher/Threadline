"""Document control, electronic signatures and release baselines (ISO 13485 4.2.4, 7.3; ADR-003)."""

import hashlib

from ruamel.yaml import YAML

from threadline import git
from threadline.project import CONFIG_FILE, _split_frontmatter
from threadline.rules import Context, Finding, rule

# meaning -> signer role it needs
ROLE_FOR = {"authored": "author", "reviewed": "reviewer", "approved_as_qa": "qa", "released": "release_manager"}
NOT_IN_BASELINE = ("approval", "baseline")  # records about the baseline cannot be part of it


def _norm(text: str) -> str:
    return text.replace("\r\n", "\n").strip()


def content_hash(body: str) -> str:
    """Hash of a document body alone (TL-D02 change detection)."""
    return hashlib.sha256(_norm(body).encode()).hexdigest()


def document_hash(doc) -> str:
    """What an approval signs: identity, type, title and revision bound to the body."""
    head = f"id:{doc.id}\ndoc_type:{doc.doc_type}\ntitle:{doc.title}\nrev:{doc.rev}\n\n"
    return hashlib.sha256((head + _norm(doc.body)).encode()).hexdigest()


def dhf_hash(project) -> str:
    """Hash of every item file except approvals and baselines: what a release baseline freezes."""
    h = hashlib.sha256()
    for item in sorted(project.items.values(), key=lambda i: i.path.relative_to(project.root).as_posix()):
        if item.type in NOT_IN_BASELINE:
            continue
        h.update(item.path.relative_to(project.root).as_posix().encode() + b"\n")
        h.update(_norm(item.path.read_text(encoding="utf-8")).encode() + b"\n")
    return h.hexdigest()


def subject_hash(subject) -> str:
    return subject.dhf_sha256 if subject.type == "baseline" else document_hash(subject)


@rule(
    "TL-D01",
    "ISO 13485 4.2.4, 7.3.4; 21 CFR 11.50, 11.70",
    "Effective documents and baselines carry the required approvals: right role, independent, bound to content",
)
def approvals(ctx: Context):
    cfg = ctx.project.config
    items = ctx.project.items
    apps = ctx.project.of_type("approval")
    for a in apps:
        subject = items.get(a.subject)
        if subject is None or subject.type not in ("document", "baseline"):
            yield Finding("TL-D01", a.id, f"subject {a.subject} is not a document or baseline")
        signer = cfg.signers.get(a.signer)
        if signer is None:
            yield Finding("TL-D01", a.id, f"signer {a.signer} is not in threadline.yaml signers")
        elif ROLE_FOR[a.meaning] not in signer.roles:
            yield Finding("TL-D01", a.id, f"{a.signer} lacks role {ROLE_FOR[a.meaning]} for {a.meaning}")
    for subj in ctx.project.of_type("document") + ctx.project.of_type("baseline"):
        if subj.status != "effective":
            continue
        current = [a for a in apps if a.subject == subj.id and a.subject_rev == subj.rev]
        expected = subject_hash(subj)
        for a in current:
            if a.subject_sha256 != expected:
                yield Finding("TL-D01", subj.id, f"{a.id} was signed for different content or metadata")
        meanings = {a.meaning for a in current}
        needed = (
            ["released"]
            if subj.type == "baseline"
            else cfg.approvals_required.get(subj.doc_type, cfg.approvals_required.get("*", []))
        )
        for m in needed:
            if m not in meanings:
                yield Finding("TL-D01", subj.id, f"rev {subj.rev} has no '{m}' approval")
        authors = {a.signer for a in current if a.meaning == "authored"}
        for a in current:
            if a.meaning != "authored" and a.signer in authors:
                yield Finding("TL-D01", subj.id, f"'{a.meaning}' signed by the author {a.signer} (not independent)")


@rule("TL-D02", "ISO 13485 4.2.4", "A content change to an effective document comes with a revision bump", "base_ref")
def rev_bump(ctx: Context):
    for doc in ctx.project.of_type("document"):
        old_text = git.show(ctx.git_root, ctx.base_ref, doc.path)
        if old_text is None:
            continue
        old, old_body = _split_frontmatter(old_text)
        if (
            old.get("status") == "effective"
            and content_hash(old_body) != content_hash(doc.body)
            and doc.rev <= old.get("rev", 1)
        ):
            yield Finding("TL-D02", doc.id, f"content changed since {ctx.base_ref} but rev stayed {doc.rev}")


def _shallow_hint(ctx) -> str:
    return " (shallow clone: check out with fetch-depth: 0)" if git.is_shallow(ctx.git_root) else ""


@rule(
    "TL-D03",
    "21 CFR 11.70, 11.100; ADR-003",
    "Every approval was committed once, SSH-signed by its signer with a key registered before that commit",
    "git_root",
)
def signatures(ctx: Context):
    registry = ctx.project.root / git.ALLOWED_SIGNERS
    for a in ctx.project.of_type("approval"):
        commits = git.commits(ctx.git_root, a.path)
        if not commits:
            yield Finding("TL-D03", a.id, "approval record is not committed")
            continue
        if len(commits) > 1:
            yield Finding("TL-D03", a.id, "approval record was changed after signing; records are immutable")
            continue
        sha = commits[0]
        keys = git.show(ctx.git_root, git.parent(ctx.git_root, sha), registry)
        if keys is None:
            yield Finding(
                "TL-D03", a.id, f"commit {sha[:10]}: no signer registry existed before it" + _shallow_hint(ctx)
            )
            continue
        status, principal = git.signature(ctx.git_root, sha, keys)
        if status != "G":
            yield Finding(
                "TL-D03",
                a.id,
                f"commit {sha[:10]} has no valid signature from a key registered before it" + _shallow_hint(ctx),
            )
        elif principal != a.signer:
            yield Finding("TL-D03", a.id, f"commit {sha[:10]} signed by {principal}, record names {a.signer}")
        elif _norm(git.show(ctx.git_root, sha, a.path) or "") != _norm(a.path.read_text(encoding="utf-8")):
            yield Finding("TL-D03", a.id, "file differs from the signed commit (edited after signing)")


def _signers_at(ctx, ref) -> dict | None:
    text = git.show(ctx.git_root, ref, ctx.project.root / CONFIG_FILE)
    return None if text is None else (YAML(typ="safe").load(text) or {}).get("signers") or {}


@rule(
    "TL-D04",
    "21 CFR 11.100, 11.300; ADR-003",
    "After its first commit, every change to the signer registry is SSH-signed by a QA signer it already trusted",
    "git_root",
)
def registry_chain(ctx: Context):
    root = ctx.project.root
    keys_path, cfg_path = root / git.ALLOWED_SIGNERS, root / CONFIG_FILE
    if not keys_path.is_file():
        return
    shas = set(git.commits(ctx.git_root, keys_path)) | set(git.commits(ctx.git_root, cfg_path))
    ordered = [s for s in git.commits(ctx.git_root) if s in shas][::-1]
    seen_root = False
    if ctx.trust_root:
        # an admin-set anchor outside the repo: the registry at that commit is trusted, later changes are checked
        root_sha = git.resolve(ctx.git_root, ctx.trust_root)
        if root_sha is None or not git.is_ancestor(ctx.git_root, root_sha, "HEAD"):
            yield Finding("TL-D04", ctx.trust_root, "trust root is not a commit in this branch's history")
            return
        if git.show(ctx.git_root, root_sha, keys_path) is None:
            yield Finding("TL-D04", ctx.trust_root, "trust root commit has no signer registry")
            return
        later = set(git._git(ctx.git_root, "rev-list", f"{root_sha}..HEAD").split())
        ordered = [s for s in ordered if s in later]
        seen_root = True
    for sha in ordered:
        before = git.parent(ctx.git_root, sha)
        keys_before, keys_after = git.show(ctx.git_root, before, keys_path), git.show(ctx.git_root, sha, keys_path)
        signers_before, signers_after = _signers_at(ctx, before), _signers_at(ctx, sha)
        if keys_before == keys_after and (signers_before or {}) == (signers_after or {}):
            continue
        if keys_before is None and not seen_root:
            seen_root = True  # the registry's first commit is the root of trust, shown in the technical file
            continue
        if keys_before is None:
            yield Finding("TL-D04", sha[:10], "signer registry re-created after deletion; cannot be trusted")
            continue
        status, principal = git.signature(ctx.git_root, sha, keys_before)
        if status != "G" or "qa" not in (signers_before or {}).get(principal, {}).get("roles", []):
            yield Finding(
                "TL-D04",
                sha[:10],
                "changes the signer registry without a signature from a QA signer "
                "registered before it" + _shallow_hint(ctx),
            )
    head_keys, head_signers = git.show(ctx.git_root, "HEAD", keys_path), _signers_at(ctx, "HEAD")
    current = {k: v.model_dump() for k, v in ctx.project.config.signers.items()}
    if head_keys != keys_path.read_text(encoding="utf-8") or (head_signers or {}) != current:
        yield Finding("TL-D04", str(git.ALLOWED_SIGNERS), "signer registry has uncommitted changes")


@rule(
    "TL-D05",
    "ISO 13485 7.3.4, 7.3.10; IEC 62304 5.8",
    "The release has an effective baseline matching the current design file, approved as released",
    "release",
)
def release_baseline(ctx: Context):
    ok = [b for b in ctx.project.of_type("baseline") if b.version == ctx.release and b.status == "effective"]
    if not ok:
        yield Finding("TL-D05", ctx.release, "no effective baseline for this release")
    elif ok[0].dhf_sha256 != dhf_hash(ctx.project):
        yield Finding("TL-D05", ok[0].id, "design file changed since the baseline was approved")
