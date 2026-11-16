"""SOUP and vulnerability rules (IEC 62304 7.1.2, 8.1.2; IEC 81001-5-1)."""

from threadline.rules import Context, Finding, rule
from threadline.sbom import key


def _register(ctx):
    return {f"{s.name}@{s.version}": s for s in ctx.project.of_type("soup") if s.status != "obsolete"}


@rule("TL-P01", "IEC 62304 7.1.2, 8.1.2", "Every SBOM component has an effective SOUP entry for that version", "sbom")
def sbom_covered(ctx: Context):
    reg = _register(ctx)
    names = {s.name: s for s in reg.values()}
    for c in ctx.sbom:
        s = reg.get(key(c))
        if s is None:
            other = names.get(c["name"])
            hint = f" (register has {other.version})" if other else ""
            yield Finding("TL-P01", key(c), f"no SOUP entry for this version{hint}")
        elif s.status != "effective":
            yield Finding("TL-P01", s.id, f"SOUP entry for {key(c)} is {s.status}, not approved")


@rule("TL-P02", "IEC 62304 8.1.2", "Every SOUP entry matches a component in the SBOM", "sbom")
def no_stale(ctx: Context):
    present = {key(c) for c in ctx.sbom}
    for k, s in _register(ctx).items():
        if k not in present:
            yield Finding("TL-P02", s.id, f"{k} is not in the SBOM (stale entry)")


@rule("TL-P03", "IEC 81001-5-1 5.7, 6.1", "Every known advisory against a SOUP has a vulnerability triage record",
      "advisories")
def triaged(ctx: Context):
    reg = _register(ctx)
    done = {(v.advisory, s) for v in ctx.project.of_type("vulnerability") for s in v.soup}
    for comp, ids in sorted(ctx.advisories.items()):
        s = reg.get(comp)
        for adv in ids:
            if s is None or (adv, s.id) not in done:
                yield Finding("TL-P03", comp, f"advisory {adv} has no vulnerability triage record")
