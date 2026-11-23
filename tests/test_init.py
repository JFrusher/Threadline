import json

from threadline import project
from threadline.cli import main


def test_init_creates_loadable_project(tmp_path):
    target = tmp_path / "qms"
    assert main(["init", str(target)]) == 0
    p = project.load(target)
    assert p.load_errors == []
    assert (target / ".github" / "workflows" / "threadline.yml").exists()
    schema = json.loads((target / ".vscode" / "item.schema.json").read_text())
    assert "software_requirement" in json.dumps(schema)


def test_init_refuses_non_empty(tmp_path):
    (tmp_path / "x").write_text("x")
    try:
        main(["init", str(tmp_path)])
    except SystemExit as e:
        assert "not empty" in str(e)
    else:
        raise AssertionError("init overwrote a non-empty directory")


def test_init_pins_version_and_scaffolds_checklists(tmp_path):
    from importlib.metadata import version

    target = tmp_path / "qms"
    main(["init", str(target)])
    wf = (target / ".github" / "workflows" / "threadline.yml").read_text()
    assert f"threadline=={version('threadline')}" in wf and "__THREADLINE_VERSION__" not in wf
    p = project.load(target)
    assert "UKER-12.1a" in p.items and "ISO13485-4.2.4" in p.items and "AUEP-SW" in p.items


def test_check_before_first_commit(tmp_path, capsys):
    """A fresh `init` + `git init` with no commits reports findings instead of crashing on `git log`."""
    import subprocess

    target = tmp_path / "qms"
    main(["init", str(target)])
    subprocess.run(["git", "init", "-q", str(target)], check=True)
    assert main(["check", str(target)]) == 1
    assert "TL-D04 [21 CFR 11.100, 11.300; ADR-003] qms/signers/allowed_signers: signer registry has uncommitted" \
        in capsys.readouterr().out
