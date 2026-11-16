"""Load a Threadline project: threadline.yaml + item files."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError, model_validator
from ruamel.yaml import YAML, YAMLError

from threadline.items import TYPES, Item

CONFIG_FILE = "threadline.yaml"
Meaning = Literal["authored", "reviewed", "approved_as_qa", "released"]
_yaml = YAML(typ="safe")


class RiskPolicy(BaseModel):
    """ISO 14971 risk acceptability policy. Levels are ordered low -> high."""

    model_config = ConfigDict(extra="forbid")
    severity: list[str]
    p1: list[str]  # probability the hazardous situation occurs
    p2: list[str]  # probability the hazardous situation leads to harm
    probability: dict[str, dict[str, str]]  # p1 -> p2 -> combined probability level
    acceptability: dict[str, dict[str, Literal["acceptable", "unacceptable"]]]  # severity -> P -> verdict
    software_p1_rule: str  # how P1 is set for software failures; stated, not assumed

    @model_validator(mode="after")
    def _complete(self):
        levels = {p for row in self.probability.values() for p in row.values()}
        for a in self.p1:
            for b in self.p2:
                if b not in self.probability.get(a, {}):
                    raise ValueError(f"risk.probability missing {a}/{b}")
        for s in self.severity:
            for p in levels:
                if p not in self.acceptability.get(s, {}):
                    raise ValueError(f"risk.acceptability missing {s}/{p}")
        return self

    def acceptable(self, severity: str, p1: str, p2: str) -> bool:
        return self.acceptability[severity][self.probability[p1][p2]] == "acceptable"


class Signer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    roles: list[str]


class Config(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product: str
    item_dirs: list[str] = ["dhf", "qms", "records"]
    lifecycle_profile: Literal["iec62304-ed1", "iec62304-ed2-draft"]
    software_class: Literal["A", "B", "C", "PRL-I", "PRL-II"]
    regulatory_profiles: list[Literal["uk-mhra", "au-model-law"]] = []
    risk: RiskPolicy
    signers: dict[str, Signer] = {}
    # doc_type -> meanings an effective document needs; "*" is the default
    approvals_required: dict[str, list[Meaning]] = {"*": ["authored", "approved_as_qa"]}

    @model_validator(mode="after")
    def _class_matches_profile(self):
        ed2 = self.lifecycle_profile == "iec62304-ed2-draft"
        if ed2 != self.software_class.startswith("PRL"):
            raise ValueError(f"software_class {self.software_class} does not fit {self.lifecycle_profile}")
        return self


@dataclass
class Project:
    root: Path
    config: Config
    items: dict[str, Item] = field(default_factory=dict)
    load_errors: list[tuple[Path, str]] = field(default_factory=list)

    def of_type(self, type_: str) -> list[Item]:
        return [i for i in self.items.values() if i.type == type_]


def _split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise ValueError("markdown file has no YAML frontmatter")
    head, sep, body = text[4:].partition("\n---\n")
    if not sep:
        raise ValueError("frontmatter not closed with ---")
    return _yaml.load(head) or {}, body


def _parse(path: Path) -> Item:
    if path.suffix == ".md":
        data, body = _split_frontmatter(path.read_text(encoding="utf-8"))
        data["body"] = body
    else:
        data = _yaml.load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("file is not a YAML mapping")
    model = TYPES.get(data.get("type"))
    if model is None:
        raise ValueError(f"unknown type {data.get('type')!r}")
    item = model.model_validate(data)
    if item.id != path.stem:
        raise ValueError(f"id {item.id!r} does not match filename {path.stem!r}")
    item.path = path
    return item


def load(root: Path) -> Project:
    root = Path(root)
    cfg_path = root / CONFIG_FILE
    if not cfg_path.is_file():
        raise FileNotFoundError(f"{cfg_path} not found — not a Threadline project")
    project = Project(root, Config.model_validate(_yaml.load(cfg_path.read_text(encoding="utf-8"))))
    for d in project.config.item_dirs:
        for path in sorted((root / d).rglob("*")):
            if path.suffix not in (".yaml", ".yml", ".md") or not path.is_file():
                continue
            try:
                item = _parse(path)
            except (ValidationError, ValueError, YAMLError) as e:
                project.load_errors.append((path.relative_to(root), str(e)))
                continue
            if item.id in project.items:
                project.load_errors.append((path.relative_to(root), f"duplicate id {item.id}"))
                continue
            project.items[item.id] = item
    return project
