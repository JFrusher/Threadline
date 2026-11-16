"""Item types. One YAML file per item (ADR-001). Links live on the child and point upward."""

from pathlib import Path
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

Status = Literal["draft", "in_review", "effective", "obsolete"]
Ids = list[str]


class Item(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # field name -> item types the IDs in that field may point at
    LINKS: ClassVar[dict[str, tuple[str, ...]]] = {}

    id: str
    type: str
    title: str
    rev: int = 1
    status: Status = "draft"
    path: Path | None = Field(default=None, exclude=True)

    def links(self):
        """Yield (field, target_id, allowed_types) for every outgoing link."""
        for field, allowed in self.LINKS.items():
            for target in getattr(self, field):
                yield field, target, allowed


# --- Design controls (ISO 13485 7.3, IEC 62304 5) -------------------------------------------


class UserNeed(Item):
    type: Literal["user_need"]
    text: str


class SystemRequirement(Item):
    LINKS = {"derives_from": ("user_need",)}
    type: Literal["system_requirement"]
    text: str
    derives_from: Ids = []


class SoftwareRequirement(Item):
    LINKS = {"derives_from": ("system_requirement",), "implements": ("risk_control",)}
    type: Literal["software_requirement"]
    text: str
    derives_from: Ids = []
    implements: Ids = []


class ArchitectureItem(Item):
    LINKS = {"implements": ("software_requirement",), "uses_soup": ("soup",)}
    type: Literal["architecture_item"]
    text: str
    software_class: Literal["A", "B", "C"] | None = None
    implements: Ids = []
    uses_soup: Ids = []
    segregation: str | None = None  # how this item is separated from items of a higher class


# --- Risk management (ISO 14971) ------------------------------------------------------------


class Residual(BaseModel):
    model_config = ConfigDict(extra="forbid")
    severity: str | None = None  # defaults to the initial severity
    p1: str
    p2: str


class Hazard(Item):
    LINKS = {"controls": ("risk_control",)}
    type: Literal["hazard"]
    category: Literal["software", "use", "security", "ml", "other"] = "software"
    hazard: str | None = None
    sequence_of_events: str | None = None
    hazardous_situation: str | None = None
    harm: str | None = None
    severity: str | None = None
    p1: str | None = None
    p2: str | None = None
    controls: Ids = []
    residual: Residual | None = None
    benefit_risk: str | None = None  # justification when residual risk is not acceptable


class RiskControl(Item):
    LINKS = {"new_hazards": ("hazard",)}
    type: Literal["risk_control"]
    kind: Literal["inherent_safety_by_design", "protective_measure", "information_for_safety"]
    text: str
    new_risk_review: str | None = None  # ISO 14971 7.5: were new hazards introduced?
    new_hazards: Ids = []


class BenefitRisk(Item):
    type: Literal["benefit_risk"]
    text: str


# --- Usability (IEC 62366-1) ----------------------------------------------------------------


class UserGroup(Item):
    type: Literal["user_group"]
    profile: str


class UseEnvironment(Item):
    type: Literal["use_environment"]
    text: str


class UiCharacteristic(Item):
    LINKS = {"related_scenarios": ("use_scenario",)}
    type: Literal["ui_characteristic"]
    text: str
    related_scenarios: Ids = []


class UseScenario(Item):
    LINKS = {
        "user_groups": ("user_group",),
        "environments": ("use_environment",),
        "hazards": ("hazard",),
    }
    type: Literal["use_scenario"]
    task: str
    text: str
    hazard_related: bool = True
    user_groups: Ids = []
    environments: Ids = []
    hazards: Ids = []


class FormativeEvaluation(Item):
    LINKS = {"scenarios": ("use_scenario",)}
    type: Literal["formative_evaluation"]
    date: str
    method: str
    participants: int
    findings: str
    scenarios: Ids = []


class SummativeProtocol(Item):
    LINKS = {"scenarios": ("use_scenario",), "user_groups": ("user_group",)}
    type: Literal["summative_protocol"]
    method: str
    participants_per_group: int
    acceptance_criteria: str
    scenarios: Ids = []
    user_groups: Ids = []


class ScenarioResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scenario: str
    outcome: Literal["pass", "fail"]
    use_errors: int = 0
    notes: str = ""


class SummativeReport(Item):
    LINKS = {"protocol": ("summative_protocol",)}
    type: Literal["summative_report"]
    illustrative: bool  # true = fictional example data; printed as a watermark
    protocol: Ids
    results: list[ScenarioResult]
    conclusion: str


# --- SOUP and security (IEC 62304 8, IEC 81001-5-1) ------------------------------------------


class Soup(Item):
    LINKS = {"hazards": ("hazard",)}
    type: Literal["soup"]
    name: str  # as it appears in the SBOM
    version: str
    supplier: str
    licence: str
    purpose: str
    software_class: Literal["A", "B", "C"]
    functional_requirements: str  # 62304 5.3.3
    system_requirements: str  # 62304 5.3.4 hardware/software needed
    anomaly_list_url: str
    anomaly_review_date: str
    anomaly_review_result: str
    approver: str
    hazards: Ids = []


class Vulnerability(Item):
    LINKS = {"soup": ("soup",), "controls": ("risk_control",)}
    type: Literal["vulnerability"]
    advisory: str  # OSV / CVE / GHSA ID
    soup: Ids
    exploitability: str
    impact: str
    decision: Literal["not_affected", "mitigated", "fix_planned"]
    rationale: str
    controls: Ids = []


class Threat(Item):
    LINKS = {"controls": ("risk_control",), "hazards": ("hazard",)}
    type: Literal["threat"]
    stride: Literal[
        "spoofing", "tampering", "repudiation", "information_disclosure",
        "denial_of_service", "elevation_of_privilege",
    ]
    asset: str
    entry_point: str
    assessment: str | None = None
    controls: Ids = []
    hazards: Ids = []


# --- AI/ML (BS/AAMI 34971) ------------------------------------------------------------------


class Dataset(Item):
    type: Literal["dataset"]
    source: str
    licence: str
    consent_basis: str
    sites: str
    demographics: str
    splits: dict[str, str]  # split name -> path relative to project root
    sha256: dict[str, str]  # split name -> SHA-256 of that file


class Model(Item):
    LINKS = {"datasets": ("dataset",)}
    type: Literal["model"]
    training_code: str
    datasets: Ids = []
    hyperparameters: dict[str, float | int | str] = {}
    weights_path: str | None = None
    weights_sha256: str | None = None
    metrics: dict[str, float] = {}
    acceptance_criteria: str | None = None
    subgroup_metrics: dict[str, dict[str, float]] = {}


class Pccp(Item):
    LINKS = {"models": ("model",)}
    type: Literal["pccp"]
    models: Ids
    planned_changes: str
    modification_protocol: str
    impact_assessment: str


# --- QMS records (ISO 13485) ----------------------------------------------------------------


class Capa(Item):
    LINKS = {"sources": ("complaint", "management_review", "vulnerability")}
    type: Literal["capa"]
    problem: str
    root_cause: str
    action: str
    effectiveness_check: str
    sources: Ids = []


class Complaint(Item):
    type: Literal["complaint"]
    received: str
    description: str
    reportable: bool
    reportability_rationale: str
    markets: list[Literal["uk", "africa"]] = []


class ManagementReview(Item):
    type: Literal["management_review"]
    date: str
    inputs: str  # ISO 13485 5.6.2
    outputs: str  # ISO 13485 5.6.3


class TrainingRecord(Item):
    type: Literal["training_record"]
    person: str
    subject: str
    date: str
    effectiveness: str


class Approval(Item):
    type: Literal["approval"]
    subject: str
    subject_rev: int
    subject_sha256: str
    meaning: Literal["authored", "reviewed", "approved_as_qa", "released"]
    signer: str
    signed_at: str


# --- Regulatory -----------------------------------------------------------------------------


class Classification(Item):
    type: Literal["classification"]
    scheme: str  # e.g. iec62304-ed1, uk-mhra, who-gmrf, imdrf-samd
    result: str
    rule: str
    rationale: str


class Requirement(Item):
    """A clause of a standard or regulation, mapped to evidence (essential requirements, 13485 clauses)."""

    LINKS = {"evidence": ()}  # empty = any item type
    type: Literal["requirement"]
    source: str  # profile or standard the clause comes from
    clause: str
    applicable: bool = True
    evidence: Ids = []  # any item IDs; checked by TL-L01
    justification: str | None = None


class Document(Item):
    """Markdown document with YAML frontmatter. `body` is the content after the frontmatter."""

    type: Literal["document"]
    doc_type: str
    body: str = Field(default="", exclude=True)


TYPES: dict[str, type[Item]] = {
    m.model_fields["type"].annotation.__args__[0]: m
    for m in Item.__subclasses__()
}


def json_schema() -> dict:
    """JSON Schema for every YAML item type, keyed on `type` (for editor autocompletion)."""
    from functools import reduce
    from operator import or_
    from typing import Annotated

    from pydantic import TypeAdapter

    yaml_types = [m for m in TYPES.values() if m is not Document]
    return TypeAdapter(Annotated[reduce(or_, yaml_types), Field(discriminator="type")]).json_schema()
