import subprocess
from pathlib import Path

from ruamel.yaml import YAML

from threadline import junit, project, rules

FIXTURES = Path(__file__).parent / "fixtures"
_yaml = YAML(typ="safe")
_dump = YAML()


def build_project(tmp: Path, files: dict) -> rules.Context:
    """Write a fixture project into tmp and return its rule context.

    Special keys: `threadline.yaml` (merged over _base.yaml), `junit.xml` (evidence),
    `sbom` (CycloneDX components), `advisories`, `git` (shell run in tmp, enables base_ref=HEAD~1).
    Any other key is a file path; dict values are dumped as YAML, strings written as-is.
    """
    cfg = _yaml.load((FIXTURES / "_base.yaml").read_text()) | files.get("threadline.yaml", {})
    with open(tmp / "threadline.yaml", "w") as f:
        _dump.dump(cfg, f)
    for rel, content in files.items():
        if rel in ("threadline.yaml", "junit.xml", "sbom", "advisories", "git"):
            continue
        path = tmp / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, str):
            path.write_text(content)
        else:
            with open(path, "w") as f:
                _dump.dump(content, f)
    if "git" in files:
        subprocess.run(["bash", "-euc", files["git"]], cwd=tmp, check=True, capture_output=True)
    ctx = rules.Context(project.load(tmp))
    if "junit.xml" in files:
        (tmp / "junit.xml").write_text(files["junit.xml"])
        ctx.tests = junit.parse(tmp / "junit.xml")
        ctx.evidence = junit.by_item(ctx.tests)
    ctx.sbom = files.get("sbom")
    ctx.advisories = files.get("advisories")
    if "git" in files:
        ctx.base_ref = "HEAD~1"
    return ctx
