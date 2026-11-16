"""Lifecycle and regulatory profile data shipped with Threadline."""

from functools import cache
from importlib.resources import files

from ruamel.yaml import YAML


@cache
def lifecycle(name: str) -> dict:
    data = YAML(typ="safe").load((files("threadline") / "data" / "lifecycle" / f"{name}.yaml").read_text())
    if "derive_from" in data:
        base = lifecycle(data["derive_from"])
        data["activities"] = [
            a | {"classes": [new for new, old in data["class_map"].items() if set(old) & set(a["classes"])]}
            for a in base["activities"]
        ]
    return data


@cache
def regulatory(name: str) -> dict:
    return YAML(typ="safe").load((files("threadline") / "data" / "regulatory" / f"{name}.yaml").read_text())


def active_regulatory(cfg) -> list[dict]:
    return [regulatory("qms-iso13485")] + [regulatory(n) for n in cfg.regulatory_profiles]
