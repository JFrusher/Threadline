"""Usability engineering rules (IEC 62366-1:2015+A1:2020)."""

from threadline.rules import Context, Finding, rule


def _hazard_related(ctx):
    return [s for s in ctx.project.of_type("use_scenario") if s.hazard_related and s.status != "obsolete"]


@rule("TL-U01", "IEC 62366-1 5.4, 5.5", "Every hazard-related use scenario names its hazards and user groups")
def scenario_linked(ctx: Context):
    for s in _hazard_related(ctx):
        if not s.hazards:
            yield Finding("TL-U01", s.id, "hazard-related scenario links no hazard")
        if not s.user_groups:
            yield Finding("TL-U01", s.id, "scenario names no user group")


@rule("TL-U02", "IEC 62366-1 5.7.1", "A summative protocol covers every hazard-related use scenario")
def summative_coverage(ctx: Context):
    covered = {sc for p in ctx.project.of_type("summative_protocol") for sc in p.scenarios}
    for s in _hazard_related(ctx):
        if s.id not in covered:
            yield Finding("TL-U02", s.id, "no summative protocol covers this scenario")


@rule("TL-U03", "IEC 62366-1 5.7.3", "Every summative protocol has a report with a result for each of its scenarios")
def summative_results(ctx: Context):
    reports = ctx.project.of_type("summative_report")
    for p in ctx.project.of_type("summative_protocol"):
        mine = [r for r in reports if p.id in r.protocol]
        if not mine:
            yield Finding("TL-U03", p.id, "no summative report")
            continue
        done = {res.scenario for r in mine for res in r.results}
        for sc in p.scenarios:
            if sc not in done:
                yield Finding("TL-U03", p.id, f"no result for {sc}")
