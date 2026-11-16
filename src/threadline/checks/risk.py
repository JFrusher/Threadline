"""ISO 14971 risk management rules."""

from threadline.rules import Context, Finding, rule

_REQUIRED = ("hazard", "hazardous_situation", "harm", "severity", "p1", "p2")


def _levels_ok(ctx, severity, p1, p2):
    pol = ctx.project.config.risk
    return severity in pol.severity and p1 in pol.p1 and p2 in pol.p2


@rule("TL-R01", "ISO 14971 5.4, 5.5", "Every hazard has situation, harm and estimated severity, P1, P2")
def hazard_complete(ctx: Context):
    for h in ctx.project.of_type("hazard"):
        missing = [f for f in _REQUIRED if not getattr(h, f)]
        if missing:
            yield Finding("TL-R01", h.id, "missing " + ", ".join(missing))
        elif not _levels_ok(ctx, h.severity, h.p1, h.p2):
            yield Finding("TL-R01", h.id, "severity/p1/p2 not levels of the risk policy")


def _complete(ctx, h):
    return all(getattr(h, f) for f in _REQUIRED) and _levels_ok(ctx, h.severity, h.p1, h.p2)


@rule("TL-R02", "ISO 14971 7.1", "Every hazard with unacceptable initial risk has a risk control")
def needs_control(ctx: Context):
    pol = ctx.project.config.risk
    for h in ctx.project.of_type("hazard"):
        if _complete(ctx, h) and not pol.acceptable(h.severity, h.p1, h.p2) and not h.controls:
            yield Finding("TL-R02", h.id, "initial risk unacceptable and no risk control")


@rule("TL-R03", "ISO 14971 7.2", "Every design/protective risk control is implemented by a software requirement")
def control_implemented(ctx: Context):
    implemented = {rc for s in ctx.project.of_type("software_requirement") for rc in s.implements}
    for rc in ctx.project.of_type("risk_control"):
        if rc.kind != "information_for_safety" and rc.id not in implemented:
            yield Finding("TL-R03", rc.id, "no software requirement implements this risk control")


@rule("TL-R04", "ISO 14971 7.2", "Every risk control is verified by at least one passing test", "evidence")
def control_verified(ctx: Context):
    for rc in ctx.project.of_type("risk_control"):
        if rc.status != "obsolete" and not ctx.passing(rc.id):
            yield Finding("TL-R04", rc.id, "no passing test verifies this risk control")


@rule("TL-R05", "ISO 14971 7.3, 7.4", "Residual risk is evaluated and acceptable, or benefit-risk is justified")
def residual(ctx: Context):
    pol = ctx.project.config.risk
    for h in ctx.project.of_type("hazard"):
        if not h.controls:
            continue
        r = h.residual
        if r is None:
            yield Finding("TL-R05", h.id, "has risk controls but no residual risk estimate")
            continue
        sev = r.severity or h.severity
        if not _levels_ok(ctx, sev, r.p1, r.p2):
            yield Finding("TL-R05", h.id, "residual severity/p1/p2 not levels of the risk policy")
        elif not pol.acceptable(sev, r.p1, r.p2) and not h.benefit_risk:
            yield Finding("TL-R05", h.id, "residual risk unacceptable and no benefit-risk justification")


@rule("TL-R06", "ISO 14971 7.5", "Every risk control is reviewed for new hazards it introduces")
def new_risks(ctx: Context):
    for rc in ctx.project.of_type("risk_control"):
        if not rc.new_risk_review:
            yield Finding("TL-R06", rc.id, "no new_risk_review recorded")
