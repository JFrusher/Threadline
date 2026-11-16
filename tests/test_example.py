"""Dogfood: the example device must pass every rule with its own test evidence."""

import subprocess
import sys
from pathlib import Path

from threadline.cli import main

EXAMPLE = Path(__file__).parents[1] / "examples" / "breathe-triage"


def test_example_passes_all_rules(tmp_path, capsys):
    junit = tmp_path / "junit.xml"
    subprocess.run([sys.executable, "-m", "pytest", "-q", str(EXAMPLE), f"--junitxml={junit}"], check=True)
    code = main(["check", str(EXAMPLE), "--junit", str(junit)])
    out = capsys.readouterr().out
    assert code == 0, out
    assert "0 finding(s)" in out


def test_plugin_refuses_xunit2(tmp_path):
    (tmp_path / "test_x.py").write_text("def test_x():\n    pass\n")
    r = subprocess.run([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", str(tmp_path),
                        f"--junitxml={tmp_path / 'j.xml'}", "-o", "junit_family=xunit2"],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "junit_family = xunit1" in r.stderr
