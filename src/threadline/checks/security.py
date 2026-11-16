"""Security risk rules (IEC 81001-5-1:2021). Security controls are risk controls, so TL-R04 verifies them."""

from threadline.rules import Context, Finding, rule


@rule("TL-T01", "IEC 81001-5-1 5.2, 7.2", "Every threat is assessed")
def assessed(ctx: Context):
    for t in ctx.project.of_type("threat"):
        if not t.assessment:
            yield Finding("TL-T01", t.id, "threat has no assessment")


@rule("TL-T02", "IEC 81001-5-1 5.2, 7.3", "Every threat has a security risk control")
def controlled(ctx: Context):
    for t in ctx.project.of_type("threat"):
        if not t.controls:
            yield Finding("TL-T02", t.id, "threat has no risk control")
