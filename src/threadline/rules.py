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

    def passing(self, item_id: str) -> list[TestCase]:
        return [t for t in (self.evidence or {}).get(item_id, []) if t.passed]


@dataclass(frozen=True)
class Rule:
    id: str
    clause: str
    title: str
    needs: str | None  # "evidence" | "sbom" | "advisories" | "base_ref" | None
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
