import argparse
import hashlib
import sys
from pathlib import Path

from threadline import git, junit, project, rtm, rules


def _context(args) -> rules.Context:
    ctx = rules.Context(project.load(args.root), git_root=git.work_tree(args.root))
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
    result = rules.run(ctx)
    by_rule = {r.id: r for r in rules.RULES.values()}
    for f in result.findings:
        r = by_rule[f.rule]
        print(f"{f.rule} [{r.clause}] {f.item}: {f.message}")
    for r in result.skipped:
        print(f"skipped {r.id} ({r.title}): needs {r.needs}")
    print(f"{len(result.findings)} finding(s), {len(result.skipped)} rule(s) skipped, "
          f"{len(ctx.project.items)} items")
    return 1 if result.findings else 0


def cmd_rtm(args) -> int:
    sys.stdout.write(rtm.render(_context(args)))
    return 0


def cmd_hash(args) -> int:
    """Content hash of a document (body only), or SHA-256 of any other file (datasets, model weights)."""
    from threadline.checks.documents import content_hash
    from threadline.project import _split_frontmatter

    if args.file.suffix == ".md":
        print(content_hash(_split_frontmatter(args.file.read_text(encoding="utf-8"))[1]))
    else:
        print(hashlib.sha256(args.file.read_bytes()).hexdigest())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="threadline")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name, fn, help_ in [("check", cmd_check, "run all rules"), ("rtm", cmd_rtm, "print the RTM")]:
        p = sub.add_parser(name, help=help_)
        p.add_argument("root", nargs="?", type=Path, default=Path("."))
        p.add_argument("--junit", type=Path, action="append", help="JUnit XML with verification evidence")
        p.add_argument("--base", help="git ref to diff documents against (e.g. origin/main)")
        p.set_defaults(fn=fn)
    p = sub.add_parser("hash", help="hash a document's content or a data file")
    p.add_argument("file", type=Path)
    p.set_defaults(fn=cmd_hash)
    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
