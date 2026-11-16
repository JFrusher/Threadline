import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import build_project

from threadline import build, junit, project, rules
from threadline.cli import main

EXAMPLE = Path(__file__).parents[1] / "examples" / "breathe-triage"


@pytest.fixture(scope="module")
def example_ctx(tmp_path_factory):
    j = tmp_path_factory.mktemp("j") / "junit.xml"
    subprocess.run([sys.executable, "-m", "pytest", "-q", str(EXAMPLE), f"--junitxml={j}"], check=True)
    ctx = rules.Context(project.load(EXAMPLE))
    ctx.tests = junit.parse(j)
    ctx.evidence = junit.by_item(ctx.tests)
    return ctx, j


def test_assemble_has_every_section(example_ctx):
    ctx, j = example_ctx
    md = build.assemble(ctx, rules.run(ctx), [j], None, "v-test", "0" * 40)
    for heading in ["# Regulatory", "# Design controls", "# Risk management report", "# Usability engineering file",
                    "# Cybersecurity", "# AI/ML data lifecycle", "# SOUP register", "# Verification evidence",
                    "# Quality management system", "# Threadline rule results"]:
        assert f"\n{heading}" in md, heading
    assert "ILLUSTRATIVE" in md.split("---")[1]  # banner in the title block
    assert "[SRS-001]{#SRS-001}" in md and "[SRS-001](#SRS-001)" in md


def test_build_refuses_on_findings(tmp_path):
    build_project(tmp_path, {"dhf/SYS-001.yaml": {"id": "SYS-001", "type": "system_requirement", "title": "S",
                                                  "text": "x"}})
    with pytest.raises(SystemExit, match="refusing to build"):
        main(["build", str(tmp_path), "--out", str(tmp_path / "out" / "tf.pdf")])


def test_cell_breaks_long_tokens_not_ids():
    assert build.cell("a_b/c") == "a_​b/​c"
    assert build.cell("[SRS-001](#SRS-001)") == "[SRS-001](#SRS-001)"


@pytest.mark.skipif(not (shutil.which("xelatex") and shutil.which("mmdc")), reason="needs XeLaTeX and mermaid-cli")
def test_pdf_builds(example_ctx, tmp_path):
    _, j = example_ctx
    out = tmp_path / "tf.pdf"
    chromium = next(Path("/opt/pw-browsers").glob("chromium-*/chrome-linux64/chrome"), None)
    from test_example import EXAMPLE_TRUST_ROOT

    args = ["build", str(EXAMPLE), "--junit", str(j), "--out", str(out), "--trust-root", EXAMPLE_TRUST_ROOT]
    assert main(args + (["--chromium", str(chromium)] if chromium else [])) == 0
    assert out.read_bytes()[:4] == b"%PDF"
