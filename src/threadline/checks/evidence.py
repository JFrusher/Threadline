"""Verification evidence rules (JUnit, ADR-002)."""

from threadline.rules import Context, Finding, rule


@rule("TL-E01", "IEC 62304 5.7", "Every software requirement is verified by at least one passing test", "evidence")
def srs_verified(ctx: Context):
    for i in ctx.project.of_type("software_requirement"):
        if i.status != "obsolete" and not ctx.passing(i.id):
            yield Finding("TL-E01", i.id, "no passing test verifies this requirement")


@rule("TL-E02", "IEC 62304 5.7.5", "No test claims to verify an unknown item", "evidence")
def unknown_refs(ctx: Context):
    for item_id, cases in sorted(ctx.evidence.items()):
        if item_id not in ctx.project.items:
            for c in cases:
                yield Finding("TL-E02", item_id, f"{c.name} verifies unknown item")
