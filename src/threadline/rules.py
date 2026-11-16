"""Rule registry and the context rules run against."""

from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

from threadline.junit import TestCase
from threadline.project import Project


@dataclass(frozen=True)
class Finding:
    rule: str
    item: str
    message: str


@dataclass
class Context:
    project: Project
    evidence: dict[str, list[TestCase]] | None = None  # None = no JUnit given
    tests: list[TestCase] = field(default_factory=list)
    sbom: list[dict] | None = None  # CycloneDX components; None = no SBOM given
    advisories: dict[str, list[str]] | None = None  # "name@version" -> advisory IDs
    base_ref: str | None = None  # git ref to diff documents against
    git_root: Path | None = None  # set when the project is in a git work tree
    release: str | None = None  # version being released; enables the baseline rule
    trust_root: str | None = None  # commit whose signer registry is trusted; set outside the repo (CI variable)

    def verification(self, item_id: str) -> str | None:
        """None if verified: at least one test, and every test verifying the item passed."""
        cases = (self.evidence or {}).get(item_id, [])
        failed = [t.name for t in cases if not t.passed]
        if failed:
            return "failing verification: " + ", ".join(failed)
        return None if cases else "no test verifies this item"


@dataclass(frozen=True)
class Rule:
    id: str
    clause: str
    title: str
    needs: str | None  # Context field that must not be None
    fn: Callable[[Context], Iterator[Finding]]


RULES: dict[str, Rule] = {}


def rule(id: str, clause: str, title: str, needs: str | None = None):
    def register(fn):
        assert id not in RULES, f"duplicate rule {id}"
        RULES[id] = Rule(id, clause, title, needs, fn)
        return fn

    return register


@dataclass
class Result:
    findings: list[Finding]
    skipped: list[Rule]


def run(ctx: Context, only: set[str] | None = None) -> Result:
    import threadline.checks  # noqa: F401  registers the rules

    findings, skipped = [], []
    for r in RULES.values():
        if only and r.id not in only:
            continue
        if r.needs and getattr(ctx, r.needs) is None:
            skipped.append(r)
            continue
        findings.extend(r.fn(ctx))
    return Result(findings, skipped)


def relpath(ctx: Context, path: Path | None) -> str:
    return str(path.relative_to(ctx.project.root)) if path else "?"


def rule_table() -> str:
    """Markdown table of every rule, for the README (kept in sync by tests/test_readme.py)."""
    import threadline.checks  # noqa: F401

    rows = [
        f"| {r.id} | {r.clause} | {r.title} | {r.needs or ''} |" for r in sorted(RULES.values(), key=lambda r: r.id)
    ]
    return "\n".join(["| Rule | Clause | Check | Needs |", "|---|---|---|---|", *rows]) + "\n"
