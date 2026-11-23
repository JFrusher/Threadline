"""Requirements traceability matrix (Markdown)."""

from threadline.rules import Context


def _tests(ctx: Context, item_id: str) -> str:
    if ctx.evidence is None:
        return "_no evidence_"
    cases = ctx.evidence.get(item_id, [])
    # "; " not <br>: the technical file is built with raw HTML disabled
    return "; ".join(f"{'PASS' if c.passed else 'FAIL'} `{c.name}`" for c in cases) or "**none**"


def render(ctx: Context) -> str:
    p = ctx.project
    out = ["## Requirements traceability matrix", "",
           "| Software requirement | System requirement | User need | Risk controls | Tests |",
           "|---|---|---|---|---|"]
    for s in sorted(p.of_type("software_requirement"), key=lambda i: i.id):
        sys_ids = s.derives_from
        un_ids = sorted({u for x in sys_ids if x in p.items for u in p.items[x].derives_from})
        out.append(f"| {s.id} {s.title} | {', '.join(sys_ids)} | {', '.join(un_ids)} "
                   f"| {', '.join(s.implements)} | {_tests(ctx, s.id)} |")
    implementers: dict[str, list[str]] = {}
    for s in p.of_type("software_requirement"):
        for rc in s.implements:
            implementers.setdefault(rc, []).append(s.id)
    out += ["", "## Risk control traceability", "",
            "| Hazard | Risk control | Implemented by | Tests |", "|---|---|---|---|"]
    for h in sorted(p.of_type("hazard"), key=lambda i: i.id):
        for rc in h.controls or ["**none**"]:
            out.append(f"| {h.id} {h.title} | {rc} | {', '.join(implementers.get(rc, []))} "
                       f"| {_tests(ctx, rc) if rc in p.items else ''} |")
    return "\n".join(out) + "\n"
