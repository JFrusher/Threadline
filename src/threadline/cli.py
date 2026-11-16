import argparse
import hashlib
import sys
from collections import Counter
from pathlib import Path

from threadline import git, junit, project, rtm, rules, sbom


def _context(args) -> rules.Context:
    ctx = rules.Context(project.load(args.root), git_root=git.work_tree(args.root))
    if args.sbom:
        ctx.sbom = sbom.components(args.sbom)
        if args.osv:
            ctx.advisories = sbom.advisories(ctx.sbom)
    elif args.osv:
        raise SystemExit("--osv needs --sbom")
    if args.base:
        if ctx.git_root is None:
            raise SystemExit("--base needs the project to be in a git work tree")
        ctx.base_ref = args.base
    if args.junit:
        ctx.tests = [c for f in args.junit for c in junit.parse(f)]
        ctx.evidence = junit.by_item(ctx.tests)
    return ctx


def cmd_check(args) -> int:
    ctx = _context(args)
    from threadline import profiles

    prof = profiles.lifecycle(ctx.project.config.lifecycle_profile)
    print(("DRAFT STANDARD: " if prof["draft"] else "NOTE: ") + prof["note"])
    result = rules.run(ctx)
    by_rule = {r.id: r for r in rules.RULES.values()}
    items = ctx.project.items
    for f in result.findings:
        r = by_rule[f.rule]
        if args.format == "github":
            # GitHub Actions annotation: shown inline on the PR's changed files
            path = items[f.item].path.relative_to(ctx.git_root or ctx.project.root) if f.item in items else None
            where = f"file={path}," if path else ""
            print(f"::error {where}title={f.rule} [{r.clause}]::{f.item}: {f.message}")
        else:
            print(f"{f.rule} [{r.clause}] {f.item}: {f.message}")
    for r in result.skipped:
        print(f"skipped {r.id} ({r.title}): needs {r.needs}")
    counts = Counter(f.rule for f in result.findings)
    if counts:
        print("\nby rule: " + ", ".join(f"{rid} {n} ({by_rule[rid].title})" for rid, n in sorted(counts.items())))
    print(f"{len(result.findings)} finding(s), {len(result.skipped)} rule(s) skipped, {len(items)} items")
    return 1 if result.findings else 0


def cmd_rtm(args) -> int:
    sys.stdout.write(rtm.render(_context(args)))
    return 0


def cmd_build(args) -> int:
    from threadline import build

    ctx = _context(args)
    ctx.release = args.release
    result = rules.run(ctx)
    if args.release:
        # D02 needs a base branch, which a tag build has none of
        missing = [r.id for r in result.skipped if r.id != "TL-D02"]
        if missing:
            raise SystemExit(
                f"--release needs every rule to run; skipped: {', '.join(missing)} "
                "(pass --junit, --sbom, --osv and build inside the git work tree)"
            )
    if result.findings:
        for f in result.findings:
            print(f"{f.rule} {f.item}: {f.message}")
        raise SystemExit(f"refusing to build: {len(result.findings)} finding(s)")
    commit = git._git(ctx.git_root, "rev-parse", "HEAD").strip() if ctx.git_root else "uncommitted"
    version = args.version or (
        git._git(ctx.git_root, "describe", "--tags", "--always").strip() if ctx.git_root else "unversioned"
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    md = build.assemble(ctx, result, args.junit or [], args.tool_validation, version, commit)
    build.to_pdf(
        md,
        args.out,
        ctx.project.config.product,
        version,
        commit,
        args.out.parent / "build",
        args.chromium,
        ctx.project.root,
    )
    (args.out.parent / "hazard-log.md").write_text(build.hazard_log(ctx))
    print(f"wrote {args.out} and {args.out.parent / 'hazard-log.md'}")
    return 0


def cmd_preset(args) -> int:
    import shutil
    from importlib.resources import files

    presets = files("threadline") / "data" / "presets"
    names = sorted(p.name for p in presets.iterdir())
    if args.name not in names:
        raise SystemExit(f"unknown preset {args.name!r}; available: {', '.join(names)}")
    src = presets / args.name
    dhf, tests = args.root / "dhf" / "presets" / args.name, args.root / "tests" / "presets"
    if dhf.exists():
        raise SystemExit(f"{dhf} exists; preset already added")
    shutil.copytree(src / "dhf", dhf)
    tests.mkdir(parents=True, exist_ok=True)
    for t in (src).iterdir():
        if t.name.startswith("test_"):
            shutil.copyfile(t, tests / t.name)
    print(
        f"added {args.name}: estimate severity/P1/P2 for each hazard (TL-R01), review controls for new risks "
        f"(TL-R06), then implement the failing test stubs in {tests}"
    )
    return 0


def cmd_approve(args) -> int:
    """Write approval records for the current revisions and commit them in one SSH-signed commit."""
    import datetime
    import subprocess

    from ruamel.yaml import YAML

    from threadline.checks.documents import ROLE_FOR, subject_hash

    p = project.load(args.root)
    signer = p.config.signers.get(args.signer)
    if signer is None or ROLE_FOR[args.meaning] not in signer.roles:
        raise SystemExit(f"{args.signer} is not a signer with role {ROLE_FOR[args.meaning]}")
    now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    records = []
    for sid in args.subjects:
        subject = p.items.get(sid)
        if subject is None or subject.type not in ("document", "baseline"):
            raise SystemExit(f"{sid} is not a document or baseline")
        item_id = f"APR-{subject.id}-r{subject.rev}-{args.meaning.replace('_', '-')}-{args.signer}"
        path = (args.root / "records" / "approvals" / f"{item_id}.yaml").resolve()
        if path.exists():
            raise SystemExit(f"{path} exists; approvals are immutable")
        records.append(
            (
                path,
                {
                    "id": item_id,
                    "type": "approval",
                    "title": f"{subject.id} rev {subject.rev} {args.meaning}",
                    "subject": subject.id,
                    "subject_rev": subject.rev,
                    "subject_sha256": subject_hash(subject),
                    "meaning": args.meaning,
                    "signer": args.signer,
                    "signed_at": now,
                },
            )
        )
    for path, data in records:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            YAML().dump(data, f)
    paths = [str(path) for path, _ in records]
    msg = f"approve ({args.meaning}, {args.signer}): {' '.join(args.subjects)}" + (
        f"\n\n{args.message}" if args.message else ""
    )
    for cmd in (["git", "add", *paths], ["git", "commit", "-S", "-m", msg, "--", *paths]):
        r = subprocess.run(cmd, cwd=args.root, capture_output=True, text=True)
        if r.returncode:
            raise SystemExit(
                f"{' '.join(cmd[:2])} failed — is git set up for SSH signing "
                f"(gpg.format=ssh, user.signingkey)?\n{r.stderr}"
            )
    print(f"signed {len(records)} approval(s) as {args.signer} ({args.meaning})")
    return 0


def cmd_baseline(args) -> int:
    from ruamel.yaml import YAML

    from threadline.checks.documents import dhf_hash

    p = project.load(args.root)
    item_id = f"BL-{args.version}"
    path = args.root / "records" / "baselines" / f"{item_id}.yaml"
    if path.exists():
        raise SystemExit(f"{path} exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        YAML().dump(
            {
                "id": item_id,
                "type": "baseline",
                "title": f"Release baseline {args.version}",
                "status": "effective",
                "version": args.version,
                "dhf_sha256": dhf_hash(p),
            },
            f,
        )
    print(f"wrote {path}; commit it, then: threadline approve {item_id} --meaning released --signer <you>")
    return 0


def cmd_hash(args) -> int:
    """Content hash of a document (body only), or SHA-256 of any other file (datasets, model weights)."""
    from threadline.checks.documents import document_hash

    if args.file.suffix == ".md":
        print(document_hash(project._parse(args.file)))
    else:
        print(hashlib.sha256(args.file.read_bytes()).hexdigest())
    return 0


def cmd_init(args) -> int:
    import json
    import shutil
    from importlib.resources import files

    from threadline.items import json_schema

    if args.target.exists() and any(args.target.iterdir()):
        raise SystemExit(f"{args.target} is not empty")
    from importlib.metadata import version

    from ruamel.yaml import YAML

    from threadline import profiles

    shutil.copytree(files("threadline") / "template", args.target, dirs_exist_ok=True)
    for wf in (args.target / ".github" / "workflows").glob("*.yml"):
        wf.write_text(wf.read_text().replace("__THREADLINE_VERSION__", version("threadline")))
    # one stub per checklist clause: teams link evidence instead of creating files (TL-G01 stays red until they do)
    cfg = project.load(args.target).config
    for prof in profiles.active_regulatory(cfg):
        for e in prof["checklist"]:
            with open(args.target / "dhf" / "regulatory" / f"{e['id']}.yaml", "w") as f:
                YAML().dump(
                    {
                        "id": e["id"],
                        "type": "requirement",
                        "title": e["title"],
                        "source": prof["name"],
                        "clause": e["clause"],
                        "evidence": [],
                    },
                    f,
                )
    (args.target / ".vscode").mkdir(exist_ok=True)
    (args.target / ".vscode" / "item.schema.json").write_text(json.dumps(json_schema(), indent=1))
    (args.target / ".vscode" / "settings.json").write_text(
        json.dumps(
            {"yaml.schemas": {"./.vscode/item.schema.json": ["dhf/**/*.yaml", "qms/**/*.yaml", "records/**/*.yaml"]}},
            indent=1,
        )
    )
    print(f"created {args.target}. Next: git init; pytest --junitxml=junit.xml; threadline check --junit junit.xml")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="threadline")
    sub = parser.add_subparsers(dest="cmd", required=True)
    commands = [
        ("check", cmd_check, "run all rules"),
        ("rtm", cmd_rtm, "print the RTM"),
        ("build", cmd_build, "build the technical file PDF (refuses on any finding)"),
    ]
    for name, fn, help_ in commands:
        p = sub.add_parser(name, help=help_)
        p.add_argument("root", nargs="?", type=Path, default=Path("."))
        p.add_argument("--junit", type=Path, action="append", help="JUnit XML with verification evidence")
        p.add_argument("--sbom", type=Path, help="CycloneDX JSON SBOM (e.g. from Syft)")
        p.add_argument("--osv", action="store_true", help="query OSV.dev for advisories against SBOM components")
        p.add_argument("--base", help="git ref to diff documents against (e.g. origin/main)")
        if name == "check":
            p.add_argument("--format", choices=["text", "github"], default="text")
        p.set_defaults(fn=fn)
        if name == "build":
            p.add_argument("--out", type=Path, default=Path("dist/technical-file.pdf"))
            p.add_argument("--version", help="release version (default: git describe)")
            p.add_argument("--tool-validation", type=Path, help="JUnit of Threadline's own fixture suite")
            p.add_argument("--chromium", help="Chromium executable for mermaid-cli")
            p.add_argument("--release", help="release version: requires an approved baseline and no skipped rules")
    p = sub.add_parser("init", help="create a new QMS repository from the template")
    p.add_argument("target", type=Path)
    p.set_defaults(fn=cmd_init)
    p = sub.add_parser("preset", help="add a low-resource or ML risk preset pack")
    p.add_argument("action", choices=["add"])
    p.add_argument("name")
    p.add_argument("root", nargs="?", type=Path, default=Path("."))
    p.set_defaults(fn=cmd_preset)
    p = sub.add_parser("approve", help="sign an approval of a document or baseline (SSH-signed commit)")
    p.add_argument("subjects", nargs="+", help="document or baseline IDs")
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--message", help="extra commit message text")
    p.add_argument("--meaning", required=True, choices=["authored", "reviewed", "approved_as_qa", "released"])
    p.add_argument("--signer", required=True, help="your principal in qms/signers/allowed_signers")
    p.set_defaults(fn=cmd_approve)
    p = sub.add_parser("baseline", help="freeze the design file for a release")
    p.add_argument("version")
    p.add_argument("root", nargs="?", type=Path, default=Path("."))
    p.set_defaults(fn=cmd_baseline)
    p = sub.add_parser("hash", help="hash a document's content or a data file")
    p.add_argument("file", type=Path)
    p.set_defaults(fn=cmd_hash)
    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
