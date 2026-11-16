import argparse
import sys
from pathlib import Path

from threadline import junit, project, rtm, rules


def _context(args) -> rules.Context:
    ctx = rules.Context(project.load(args.root))
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="threadline")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name, fn, help_ in [("check", cmd_check, "run all rules"), ("rtm", cmd_rtm, "print the RTM")]:
        p = sub.add_parser(name, help=help_)
        p.add_argument("root", nargs="?", type=Path, default=Path("."))
        p.add_argument("--junit", type=Path, action="append", help="JUnit XML with verification evidence")
        p.set_defaults(fn=fn)
    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
