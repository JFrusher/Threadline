"""Lifecycle profile rule: deliverables required for the software class exist."""

from threadline import profiles
from threadline.rules import Context, Finding, rule


def _met(ctx, req: dict) -> bool:
    live = [i for i in ctx.project.items.values() if i.status != "obsolete"]
    if "item_type" in req:
        return any(i.type == req["item_type"] for i in live)
    if "doc_type" in req:
        return any(i.type == "document" and i.doc_type == req["doc_type"] for i in live)
    return req["document"] in ctx.project.items


@rule("TL-C01", "IEC 62304 (per lifecycle profile)", "Every activity the software class requires has its deliverable")
def deliverables(ctx: Context):
    cfg = ctx.project.config
    prof = profiles.lifecycle(cfg.lifecycle_profile)
    for a in prof["activities"]:
        if cfg.software_class in a["classes"] and not _met(ctx, a["requires"]):
            want = ", ".join(f"{k} {v}" for k, v in a["requires"].items())
            yield Finding("TL-C01", f"{prof['standard'].split(' —')[0]} {a['clause']}",
                          f"{a['title']} (class {cfg.software_class}) needs {want}")
