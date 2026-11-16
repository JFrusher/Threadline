"""Regulatory profile rules: checklists mapped to evidence, required classifications."""

from threadline import profiles
from threadline.rules import Context, Finding, rule


@rule("TL-G01", "ISO 13485 4.2.3; UK MDR 2002 Part II; AU Model Law",
      "Every checklist clause of the active profiles is mapped to evidence or justified as not applicable")
def checklist(ctx: Context):
    items = ctx.project.items
    for prof in profiles.active_regulatory(ctx.project.config):
        for entry in prof["checklist"]:
            r = items.get(entry["id"])
            if r is None or r.type != "requirement":
                yield Finding("TL-G01", entry["id"], f"{prof['name']} {entry['clause']}: no requirement item")
            elif r.applicable and not r.evidence:
                yield Finding("TL-G01", r.id, "applicable but linked to no evidence")
            elif not r.applicable and not r.justification:
                yield Finding("TL-G01", r.id, "not applicable but no justification")


@rule("TL-G02", "UK MDR 2002 reg. 7 / Annex IX; WHO GMRF classification",
      "Every classification scheme the active profiles need has a classification item")
def classified(ctx: Context):
    have = {c.scheme for c in ctx.project.of_type("classification")}
    for prof in profiles.active_regulatory(ctx.project.config):
        for scheme in prof["classification_schemes"]:
            if scheme not in have:
                yield Finding("TL-G02", scheme, f"{prof['name']}: no classification item for scheme {scheme}")
