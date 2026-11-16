"""Schema and link rules."""

from threadline.rules import Context, Finding, rule


@rule("TL-S01", "ISO 13485 4.2.4", "Every item file is valid, its type is known and its filename is its ID")
def schema(ctx: Context):
    for path, msg in ctx.project.load_errors:
        yield Finding("TL-S01", str(path), msg)


@rule("TL-L01", "IEC 62304 5.1.1", "Every link points at an existing item of an allowed type")
def dangling(ctx: Context):
    items = ctx.project.items
    for item in items.values():
        for field, target, allowed in item.links():
            if target not in items:
                yield Finding("TL-L01", item.id, f"{field} -> {target}: no such item")
            elif allowed and items[target].type not in allowed:
                yield Finding(
                    "TL-L01", item.id,
                    f"{field} -> {target}: is {items[target].type}, expected {' or '.join(allowed)}",
                )


@rule("TL-L05", "ISO 13485 4.2.4, 7.3.9", "No live item links to an obsolete item")
def obsolete_links(ctx: Context):
    items = ctx.project.items
    for item in items.values():
        if item.status == "obsolete":
            continue
        for field, target, _ in item.links():
            if target in items and items[target].status == "obsolete":
                yield Finding("TL-L05", item.id, f"{field} -> {target}: target is obsolete")


@rule("TL-L02", "IEC 62304 5.2", "Every software requirement traces to a system requirement or risk control")
def srs_upward(ctx: Context):
    for i in ctx.project.of_type("software_requirement"):
        if not i.derives_from and not i.implements:
            yield Finding("TL-L02", i.id, "derives from no system requirement and implements no risk control")


@rule("TL-L03", "ISO 13485 7.3.3", "Every system requirement traces to a user need")
def sys_upward(ctx: Context):
    for i in ctx.project.of_type("system_requirement"):
        if not i.derives_from:
            yield Finding("TL-L03", i.id, "derives from no user need")


@rule("TL-L04", "ISO 13485 7.3.10", "The trace graph has no cycles")
def cycles(ctx: Context):
    items = ctx.project.items
    state: dict[str, int] = {}  # 1 = on stack, 2 = done

    def visit(node: str, stack: list[str]):
        state[node] = 1
        for _, target, _ in items[node].links():
            if target not in items:
                continue
            if state.get(target) == 1:
                yield Finding("TL-L04", node, "cycle: " + " -> ".join(stack[stack.index(target):] + [target]))
            elif target not in state:
                yield from visit(target, stack + [target])
        state[node] = 2

    for node in sorted(items):
        if node not in state:
            yield from visit(node, [node])
