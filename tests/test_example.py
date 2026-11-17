"""Dogfood: the example device must pass every rule with its own test evidence."""

import subprocess
import sys
from pathlib import Path

from threadline.cli import main

EXAMPLE = Path(__file__).parents[1] / "examples" / "breathe-triage"
# the example's signer-registry anchor; real projects take it from an admin-set CI variable
EXAMPLE_TRUST_ROOT = "87785d9a6e5fd9fa56d7f36ca3256c91d349238a"


def test_example_passes_all_rules(tmp_path, capsys):
    junit = tmp_path / "junit.xml"
    subprocess.run([sys.executable, "-m", "pytest", "-q", str(EXAMPLE), f"--junitxml={junit}"], check=True)
    code = main(["check", str(EXAMPLE), "--junit", str(junit), "--trust-root", EXAMPLE_TRUST_ROOT])
    out = capsys.readouterr().out
    assert code == 0, out
    assert "0 finding(s)" in out


def test_plugin_refuses_xunit2(tmp_path):
    (tmp_path / "test_x.py").write_text("def test_x():\n    pass\n")
    r = subprocess.run([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", str(tmp_path),
                        f"--junitxml={tmp_path / 'j.xml'}", "-o", "junit_family=xunit2"],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "junit_family = xunit1" in r.stderr


def test_github_annotations(tmp_path, capsys):
    from conftest import build_project
    build_project(tmp_path, {"dhf/SYS-001.yaml": {"id": "SYS-001", "type": "system_requirement", "title": "S",
                                                  "text": "x"}})
    assert main(["check", str(tmp_path), "--format", "github"]) == 1
    out = capsys.readouterr().out
    assert "::error file=dhf/SYS-001.yaml,title=TL-L03" in out
    assert "by rule: " in out and "TL-L03 1 (" in out
