"""Compile the technical file: Markdown assembled from items, rendered to PDF by Pandoc + XeLaTeX."""

import datetime
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

from threadline import git, profiles, rtm
from threadline.rules import RULES, Context, Result

# Item text is untrusted: no raw LaTeX/HTML may reach the PDF engine (it could \\input runner files)
PANDOC_FROM = "markdown-raw_tex-raw_attribute-raw_html"
DESIGN_DOC_TYPES = ("intended_use", "sdp", "sad", "detailed_design", "clinical_evaluation")
ILLUSTRATIVE = re.compile(r"ILLUSTRATIVE|FICTIONAL", re.I)


def link(ctx: Context, item_id: str) -> str:
    return f"[{item_id}](#{item_id})" if item_id in ctx.project.items else item_id


def anchor(item_id: str) -> str:
    return f"[{item_id}]{{#{item_id}}}"


def cell(text) -> str:
    # zero-width spaces let LaTeX wrap tokens like inherent_safety_by_design; item IDs never contain _ or /
    text = " ".join(str(text or "").split()).replace("|", "\\|")
    return text.replace("_", "_​").replace("/", "/​")


def links(ctx, ids) -> str:
    return ", ".join(link(ctx, i) for i in ids)


def table(header: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "_None._\n"
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def _items(ctx, type_):
    return sorted(ctx.project.of_type(type_), key=lambda i: i.id)


def _docs(ctx, doc_type):
    return [d for d in _items(ctx, "document") if d.doc_type == doc_type]


def _demote(body: str) -> str:
    """Shift document headings down two levels so they nest under the technical-file sections."""
    return re.sub(r"^(#+) ", lambda m: "#" * min(len(m.group(1)) + 2, 6) + " ", body, flags=re.M)


def section_documents(ctx, doc_type, title):
    out = []
    for d in _docs(ctx, doc_type):
        out += [f"### {anchor(d.id)} {d.title} (rev {d.rev}, {d.status})", "", _demote(d.body), ""]
    return f"## {title}\n\n" + ("\n".join(out) or "_None._\n")


def section_regulatory(ctx):
    out = ["# Regulatory\n"]
    out.append("## Classification\n")
    out.append(
        table(
            ["ID", "Scheme", "Result", "Rule", "Rationale"],
            [[anchor(c.id), c.scheme, c.result, c.rule, c.rationale] for c in _items(ctx, "classification")],
        )
    )
    for prof in profiles.active_regulatory(ctx.project.config):
        out.append(f"## {prof['name']}\n\n_{cell(prof['note'])}_\n")
        rows = []
        for e in prof["checklist"]:
            r = ctx.project.items.get(e["id"])
            status = (
                (links(ctx, r.evidence) if r.applicable else f"Not applicable: {r.justification}") if r else "MISSING"
            )
            rows.append([anchor(e["id"]) if r else e["id"], e["clause"], e["title"], status])
        out.append(table(["ID", "Clause", "Requirement", "Evidence / justification"], rows))
    return "\n".join(out)


def section_design(ctx):
    p = ctx.project
    out = ["# Design controls\n", section_documents(ctx, "intended_use", "Intended use")]
    out.append("## User needs\n")
    out.append(table(["ID", "Title", "Text"], [[anchor(i.id), i.title, i.text] for i in _items(ctx, "user_need")]))
    out.append("## System requirements\n")
    out.append(
        table(
            ["ID", "Title", "Text", "Derives from"],
            [[anchor(i.id), i.title, i.text, links(ctx, i.derives_from)] for i in _items(ctx, "system_requirement")],
        )
    )
    out.append("## Software requirements\n")
    out.append(
        table(
            ["ID", "Title", "Text", "Derives from", "Implements"],
            [
                [anchor(i.id), i.title, i.text, links(ctx, i.derives_from), links(ctx, i.implements)]
                for i in _items(ctx, "software_requirement")
            ],
        )
    )
    out += [
        section_documents(ctx, "sdp", "Software development plan"),
        section_documents(ctx, "sad", "Software architecture"),
    ]
    out.append("### Architecture items\n")
    out.append(
        table(
            ["ID", "Title", "Class", "Implements", "SOUP", "Segregation"],
            [
                [
                    anchor(i.id),
                    i.title,
                    i.software_class,
                    links(ctx, i.implements),
                    links(ctx, i.uses_soup),
                    i.segregation,
                ]
                for i in _items(ctx, "architecture_item")
            ],
        )
    )
    out.append(section_documents(ctx, "detailed_design", "Detailed design"))
    out.append(section_documents(ctx, "clinical_evaluation", "Clinical evaluation"))
    lc = profiles.lifecycle(p.config.lifecycle_profile)
    out.append(
        f"## Lifecycle profile\n\n{lc['standard']}, software class **{p.config.software_class}**.\n\n"
        f"_{cell(lc['note'])}_\n"
    )
    return "\n".join(out)


def risk_report(ctx) -> str:
    pol = ctx.project.config.risk
    out = [
        "# Risk management report (ISO 14971)\n",
        "## Risk policy\n",
        f"Severity levels: {', '.join(pol.severity)}. P1 levels: {', '.join(pol.p1)}. "
        f"P2 levels: {', '.join(pol.p2)}.\n\nSoftware P1 rule: {pol.software_p1_rule}\n",
    ]
    levels = list(dict.fromkeys(v for row in pol.probability.values() for v in row.values()))
    out.append(
        table(["Severity \\\\ P"] + levels, [[s] + [pol.acceptability[s][p] for p in levels] for s in pol.severity])
    )
    out.append("## Hazards\n")
    rows = []
    for h in _items(ctx, "hazard"):
        r = h.residual
        res = (
            f"{r.severity or h.severity}/{r.p1}/{r.p2}: "
            + ("acceptable" if pol.acceptable(r.severity or h.severity, r.p1, r.p2) else "UNACCEPTABLE")
            if r
            else "—"
        )
        init = f"{h.severity}/{h.p1}/{h.p2}: " + (
            "acceptable" if pol.acceptable(h.severity, h.p1, h.p2) else "unacceptable"
        )
        rows.append(
            [
                anchor(h.id),
                h.category,
                h.hazardous_situation,
                h.harm,
                init,
                links(ctx, h.controls),
                res,
                h.benefit_risk or "",
            ]
        )
    out.append(
        table(
            [
                "ID",
                "Category",
                "Hazardous situation",
                "Harm",
                "Initial (S/P1/P2)",
                "Controls",
                "Residual",
                "Benefit-risk",
            ],
            rows,
        )
    )
    refs = [(h.id, r) for h in _items(ctx, "hazard") for r in h.references]
    if refs:
        out.append("\n**Hazard references.**\n\n" + "\n".join(f"- {link(ctx, i)}: {r}" for i, r in refs) + "\n")
    out.append("## Risk controls\n")
    out.append(
        table(
            ["ID", "Title", "Kind", "Text", "New-risk review"],
            [[anchor(c.id), c.title, c.kind, c.text, c.new_risk_review] for c in _items(ctx, "risk_control")],
        )
    )
    unacceptable = [
        h.id
        for h in _items(ctx, "hazard")
        if h.residual
        and not pol.acceptable(h.residual.severity or h.severity, h.residual.p1, h.residual.p2)
        and not h.benefit_risk
    ]
    out.append("## Overall residual risk\n")
    out.append(
        "Every residual risk is acceptable under the policy or justified by benefit-risk.\n"
        if not unacceptable
        else f"Unacceptable residual risks without justification: {', '.join(unacceptable)}\n"
    )
    return "\n".join(out)


def hazard_log(ctx) -> str:
    """DCB0129 hazard log. Columns follow Threadline fields; map to the NHS England template before submission."""
    out = [
        "# Clinical risk management — hazard log (DCB0129)\n",
        "_Fields follow Threadline's hazard model; map them to the current NHS England hazard log template._\n",
    ]
    out.append(
        table(
            ["Hazard ID", "Title", "Cause", "Effect", "Harm", "Initial S/P1/P2", "Controls", "Residual"],
            [
                [
                    h.id,
                    h.title,
                    h.sequence_of_events,
                    h.hazardous_situation,
                    h.harm,
                    f"{h.severity}/{h.p1}/{h.p2}",
                    ", ".join(h.controls),
                    f"{h.residual.p1}/{h.residual.p2}" if h.residual else "",
                ]
                for h in _items(ctx, "hazard")
            ],
        )
    )
    return "\n".join(out)


def section_usability(ctx):
    out = ["# Usability engineering file (IEC 62366-1)\n"]
    out.append("## User groups\n")
    out.append(
        table(["ID", "Title", "Profile"], [[anchor(i.id), i.title, i.profile] for i in _items(ctx, "user_group")])
    )
    out.append("## Use environments\n")
    out.append(
        table(["ID", "Title", "Text"], [[anchor(i.id), i.title, i.text] for i in _items(ctx, "use_environment")])
    )
    out.append("## User interface characteristics\n")
    out.append(
        table(
            ["ID", "Title", "Text", "Scenarios"],
            [
                [anchor(i.id), i.title, i.text, links(ctx, i.related_scenarios)]
                for i in _items(ctx, "ui_characteristic")
            ],
        )
    )
    out.append("## Hazard-related use scenarios\n")
    out.append(
        table(
            ["ID", "Task", "Scenario", "User groups", "Hazards"],
            [
                [anchor(i.id), i.task, i.text, links(ctx, i.user_groups), links(ctx, i.hazards)]
                for i in _items(ctx, "use_scenario")
            ],
        )
    )
    out.append("## Formative evaluations\n")
    out.append(
        table(
            ["ID", "Date", "Method", "n", "Findings"],
            [[anchor(i.id), i.date, i.method, i.participants, i.findings] for i in _items(ctx, "formative_evaluation")],
        )
    )
    for p in _items(ctx, "summative_protocol"):
        out.append(
            f"## Summative protocol {anchor(p.id)}\n\n{p.method}. {p.participants_per_group} per user group. "
            f"Acceptance: {p.acceptance_criteria}\n"
        )
    for r in _items(ctx, "summative_report"):
        mark = "**ILLUSTRATIVE DATA — not a real evaluation.**\n\n" if r.illustrative else ""
        out.append(f"## Summative report {anchor(r.id)}\n\n{mark}")
        out.append(
            table(
                ["Scenario", "Outcome", "Use errors", "Notes"],
                [[link(ctx, x.scenario), x.outcome, x.use_errors, x.notes] for x in r.results],
            )
        )
        out.append(f"\n{r.conclusion}\n")
    return "\n".join(out)


def section_security_ml_soup(ctx):
    out = ["# Cybersecurity (IEC 81001-5-1)\n"]
    out.append(
        table(
            ["ID", "STRIDE", "Asset", "Entry point", "Assessment", "Controls"],
            [
                [anchor(t.id), t.stride, t.asset, t.entry_point, t.assessment, links(ctx, t.controls)]
                for t in _items(ctx, "threat")
            ],
        )
    )
    out.append("# AI/ML data lifecycle\n\n## Datasets\n")
    out.append(
        table(
            ["ID", "Source", "Consent basis", "Demographics", "Splits (SHA-256)"],
            [
                [
                    anchor(d.id),
                    d.source,
                    d.consent_basis,
                    d.demographics,
                    "; ".join(f"{k}: {d.sha256.get(k, '')[:12]}…" for k in d.splits),
                ]
                for d in _items(ctx, "dataset")
            ],
        )
    )
    out.append("## Models\n")
    out.append(
        table(
            ["ID", "Datasets", "Weights SHA-256", "Metrics", "Subgroups", "Acceptance"],
            [
                [
                    anchor(m.id),
                    links(ctx, m.datasets),
                    (m.weights_sha256 or "")[:16] + "…",
                    ", ".join(f"{k}={v}" for k, v in m.metrics.items()),
                    "; ".join(
                        f"{g}: " + ", ".join(f"{k}={v}" for k, v in s.items()) for g, s in m.subgroup_metrics.items()
                    ),
                    m.acceptance_criteria,
                ]
                for m in _items(ctx, "model")
            ],
        )
    )
    out.append("## Predetermined change control plans\n")
    out.append(
        table(
            ["ID", "Models", "Planned changes", "Protocol", "Impact"],
            [
                [anchor(p.id), links(ctx, p.models), p.planned_changes, p.modification_protocol, p.impact_assessment]
                for p in _items(ctx, "pccp")
            ],
        )
    )
    out.append("# SOUP register and SBOM (IEC 62304 8)\n")
    out.append(
        table(
            ["ID", "Name", "Version", "Licence", "Class", "Anomaly review", "Approver"],
            [
                [
                    anchor(s.id),
                    s.name,
                    s.version,
                    s.licence,
                    s.software_class,
                    f"{s.anomaly_review_date}: {s.anomaly_review_result}",
                    s.approver,
                ]
                for s in _items(ctx, "soup")
            ],
        )
    )
    if ctx.sbom is not None:
        out.append(
            f"\nSBOM components: {len(ctx.sbom)}. "
            + ("Advisories checked against OSV.dev." if ctx.advisories is not None else "Advisories not checked.")
        )
    out.append("\n## Vulnerability triage\n")
    out.append(
        table(
            ["ID", "Advisory", "SOUP", "Decision", "Rationale"],
            [
                [anchor(v.id), v.advisory, links(ctx, v.soup), v.decision, v.rationale]
                for v in _items(ctx, "vulnerability")
            ],
        )
    )
    return "\n".join(out)


def section_verification(ctx, junit_files: list[Path]):
    out = ["# Verification evidence\n"]
    if ctx.evidence is None:
        return out[0] + "\n_No JUnit evidence supplied — this file is not a release record._\n"
    passed = sum(t.passed for t in ctx.tests)
    out.append(f"{passed} of {len(ctx.tests)} tests passed.\n")
    out.append(
        table(["JUnit file", "SHA-256"], [[f.name, hashlib.sha256(f.read_bytes()).hexdigest()] for f in junit_files])
    )
    out.append("\n" + rtm.render(ctx))
    return "\n".join(out)


def section_qms(ctx):
    cfg = ctx.project.config
    out = ["# Quality management system\n", "## Controlled documents\n"]
    out.append(
        table(
            ["ID", "Title", "Type", "Rev", "Status"],
            [[link(ctx, d.id), d.title, d.doc_type, d.rev, d.status] for d in _items(ctx, "document")],
        )
    )
    out.append("## Signatures (21 CFR 11.50 manifestation)\n")
    rows = []
    for a in _items(ctx, "approval"):
        signer = cfg.signers.get(a.signer)
        commit = ""
        if ctx.git_root:
            commits = git.commits_touching(ctx.git_root, a.path)
            commit = commits[-1][:10] if commits else "uncommitted"
        rows.append(
            [link(ctx, a.subject), a.subject_rev, signer.name if signer else a.signer, a.meaning, a.signed_at, commit]
        )
    out.append(table(["Document", "Rev", "Signed by", "Meaning", "Signed at", "Commit"], rows))
    for type_, title, fields in [
        ("capa", "CAPA", ["problem", "root_cause", "action", "effectiveness_check"]),
        ("complaint", "Complaints", ["received", "description", "reportable", "reportability_rationale"]),
        ("management_review", "Management reviews", ["date", "inputs", "outputs"]),
        ("training_record", "Training records", ["person", "subject", "date"]),
    ]:
        out.append(f"## {title}\n")
        out.append(
            table(["ID"] + fields, [[anchor(i.id)] + [getattr(i, f) for f in fields] for i in _items(ctx, type_)])
        )
    out.append("## Procedures and other documents\n")
    for d in [d for d in _items(ctx, "document") if d.doc_type not in DESIGN_DOC_TYPES]:
        out += [f"### {anchor(d.id)} {d.title} (rev {d.rev}, {d.status})", "", _demote(d.body), ""]
    return "\n".join(out)


def section_checks(result: Result):
    out = ["# Threadline rule results\n"]
    skipped = {r.id for r in result.skipped}
    out.append(
        table(
            ["Rule", "Clause", "Check", "Result"],
            [
                [r.id, r.clause, r.title, "skipped (needs " + r.needs + ")" if r.id in skipped else "pass"]
                for r in RULES.values()
            ],
        )
    )
    return "\n".join(out)


def section_tool_validation(path: Path | None):
    if path is None:
        return ""
    from threadline import junit

    cases = junit.parse(path)
    out = [
        "# Tool validation report (ISO 13485 4.1.6)\n",
        f"Threadline rule fixture suite: {sum(c.passed for c in cases)} of {len(cases)} passed. "
        f"File SHA-256 `{hashlib.sha256(path.read_bytes()).hexdigest()}`.\n",
    ]
    out.append(table(["Test", "Result"], [[c.name, "pass" if c.passed else "FAIL"] for c in cases]))
    return "\n".join(out)


def assemble(
    ctx: Context, result: Result, junit_files: list[Path], tool_validation: Path | None, version: str, commit: str
) -> str:
    p = ctx.project
    banners = []
    lc = profiles.lifecycle(p.config.lifecycle_profile)
    if lc["draft"]:
        banners.append("**DRAFT STANDARD:** lifecycle profile " + lc["standard"])
    if ILLUSTRATIVE.search(p.config.product) or any(getattr(i, "illustrative", False) for i in p.items.values()):
        banners.append("**ILLUSTRATIVE:** contains fictional or illustrative data. Not for submission.")
    abstract = " ".join(banners) or "Generated by Threadline from the controlled repository."
    head = [
        "---",
        "title: " + json.dumps(f"Technical file — {p.config.product}"),
        "subtitle: " + json.dumps(f"Version {version} · commit {commit[:12]}"),
        "date: " + json.dumps(datetime.date.today().isoformat()),
        "abstract: " + json.dumps(abstract),
        "---",
        "",
    ]
    body = [
        section_regulatory(ctx),
        section_design(ctx),
        risk_report(ctx),
        section_usability(ctx),
        section_security_ml_soup(ctx),
        section_verification(ctx, junit_files),
        section_qms(ctx),
        section_checks(result),
        section_tool_validation(tool_validation),
    ]
    return "\n".join(head) + "\n" + "\n\n".join(body)


def render_mermaid(markdown: str, workdir: Path) -> str:
    """Replace ```mermaid blocks with PNG images rendered by mermaid-cli (`mmdc`, required on PATH)."""
    blocks = re.findall(r"```mermaid\n(.*?)```", markdown, re.S)
    if not blocks:
        return markdown
    mmdc = shutil.which("mmdc")
    if mmdc is None:
        raise SystemExit("documents contain Mermaid diagrams: install mermaid-cli (`mmdc`) to build")
    for n, src in enumerate(blocks):
        (workdir / f"diagram-{n}.mmd").write_text(src)
        subprocess.run(
            [
                mmdc,
                "-i",
                str(workdir / f"diagram-{n}.mmd"),
                "-o",
                str(workdir / f"diagram-{n}.png"),
                "-s",
                "2",
                "-p",
                str(workdir / "puppeteer.json"),
            ],
            check=True,
            capture_output=True,
        )
        markdown = markdown.replace(f"```mermaid\n{src}```", f"![Diagram {n + 1}](diagram-{n}.png){{ width=80% }}", 1)
    return markdown


def footer(product: str, version: str, commit: str) -> str:
    esc = re.sub(r"([&%$#_{}])", r"\\\1", f"{product} · {version} · {commit[:12]}")
    return (
        "\\usepackage{float}\n\\floatplacement{figure}{H}\n"  # keep diagrams with their section
        "\\usepackage{fancyhdr}\n\\pagestyle{fancy}\n\\fancyhf{}\n"
        f"\\fancyfoot[L]{{\\footnotesize {esc}}}\n\\fancyfoot[R]{{\\footnotesize \\thepage}}\n"
        "\\renewcommand{\\headrulewidth}{0pt}\n"
    )


def check_images(markdown: str, project_root: Path) -> None:
    """Every image target must be a relative path to a file inside the project (no runner files, no URLs)."""

    def walk(node):
        if isinstance(node, dict):
            if node.get("t") == "Image":
                yield node["c"][2][0]
            for v in node.values():
                yield from walk(v)
        elif isinstance(node, list):
            for v in node:
                yield from walk(v)

    ast = json.loads(
        subprocess.run(
            ["pandoc", "-f", PANDOC_FROM, "-t", "json"], input=markdown, text=True, capture_output=True, check=True
        ).stdout
    )
    root = project_root.resolve()
    for target in walk(ast):
        path = (root / target).resolve()
        if "://" in target or Path(target).is_absolute() or not path.is_relative_to(root) or not path.is_file():
            raise SystemExit(f"image {target!r}: images must be relative paths to files inside the project")


def to_pdf(
    markdown: str,
    out: Path,
    product: str,
    version: str,
    commit: str,
    workdir: Path,
    chromium: str | None,
    project_root: Path,
):
    workdir.mkdir(parents=True, exist_ok=True)
    if chromium:
        (workdir / "puppeteer.json").write_text(f'{{"executablePath": "{chromium}", "args": ["--no-sandbox"]}}')
    else:
        (workdir / "puppeteer.json").write_text('{"args": ["--no-sandbox"]}')
    check_images(markdown, project_root)
    md = render_mermaid(markdown, workdir)
    (workdir / "technical-file.md").write_text(md)
    (workdir / "footer.tex").write_text(footer(product, version, commit))
    subprocess.run(
        [
            "pandoc",
            "technical-file.md",
            "-f",
            PANDOC_FROM,
            f"--resource-path={workdir}:{project_root}",
            "-o",
            str(out.resolve()),
            "--pdf-engine=xelatex",
            "--toc",
            "--toc-depth=2",
            "-V",
            "geometry:margin=18mm",
            "-V",
            "colorlinks=true",
            "-V",
            "mainfont=DejaVu Serif",
            "-V",
            "monofont=DejaVu Sans Mono",
            "-V",
            "fontsize=9pt",
            "-V",
            "papersize=a4",
            "--include-in-header=footer.tex",
        ],
        cwd=workdir,
        check=True,
    )
