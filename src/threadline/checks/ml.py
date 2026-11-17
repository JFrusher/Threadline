"""AI/ML data-lifecycle rules (BS/AAMI 34971:2023 hazards; IEC 62304 8 configuration items)."""

import hashlib

from threadline.rules import Context, Finding, rule

_MODEL_FIELDS = ("datasets", "weights_path", "weights_sha256", "metrics", "acceptance_criteria", "subgroup_metrics")


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@rule("TL-M01", "BS/AAMI 34971 (data, bias); IEC 62304 8.1",
      "Every model records datasets, weights hash, metrics, subgroup metrics and acceptance criteria")
def model_complete(ctx: Context):
    for m in ctx.project.of_type("model"):
        missing = [f for f in _MODEL_FIELDS if not getattr(m, f)]
        if missing:
            yield Finding("TL-M01", m.id, "missing " + ", ".join(missing))


@rule("TL-M02", "IEC 62304 8.1.2, 8.2", "Model weights and dataset files match their registered SHA-256")
def hashes_match(ctx: Context):
    root = ctx.project.root
    files = [(m.id, m.weights_path, m.weights_sha256) for m in ctx.project.of_type("model") if m.weights_path]
    for d in ctx.project.of_type("dataset"):
        for split, rel in d.splits.items():
            files.append((d.id, rel, d.sha256.get(split)))
    for item_id, rel, expected in files:
        path = (root / rel).resolve()
        if not path.is_relative_to(root.resolve()):
            yield Finding("TL-M02", item_id, f"{rel} is outside the project")
        elif not path.is_file():
            yield Finding("TL-M02", item_id, f"{rel} not found")
        elif _sha256(path) != expected:
            yield Finding("TL-M02", item_id, f"{rel} hash differs from the registered SHA-256")
