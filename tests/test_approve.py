"""End-to-end: approve + baseline produce records that pass TL-D01/D03/D04/D05."""

import os
import subprocess

from conftest import build_project

from threadline import project, rules
from threadline.cli import main

DOC = "---\nid: SOP-01\ntype: document\ndoc_type: sop\ntitle: T\nrev: 1\nstatus: effective\n---\nBody.\n"


def _git(tmp, *a, key=None):
    env = os.environ | {"GIT_CONFIG_COUNT": "3", "GIT_CONFIG_KEY_0": "gpg.format", "GIT_CONFIG_VALUE_0": "ssh",
                        "GIT_CONFIG_KEY_1": "gpg.ssh.program", "GIT_CONFIG_VALUE_1": "ssh-keygen",
                        "GIT_CONFIG_KEY_2": "user.signingkey", "GIT_CONFIG_VALUE_2": str(key or "")}
    return env


def test_approve_and_release_baseline(tmp_path, monkeypatch):
    build_project(tmp_path, {
        "threadline.yaml": {"signers": {"ann": {"name": "A", "roles": ["author"]},
                                        "quinn": {"name": "Q", "roles": ["qa"]},
                                        "rita": {"name": "R", "roles": ["release_manager"]}}},
        "qms/SOP-01.md": DOC,
        "git": """
git init -q && git config user.name t && git config user.email t@x && git config commit.gpgsign false
mkdir -p qms/signers && for k in ann quinn rita; do ssh-keygen -q -t ed25519 -N "" -f $k.key; done
for k in ann quinn rita; do echo "$k $(cat $k.key.pub)" >> qms/signers/allowed_signers; done
printf '*.key*\\n' > .gitignore && git add -A && git commit -qm root-of-trust
"""})
    for who, meaning, subj in [("ann", "authored", "SOP-01"), ("quinn", "approved_as_qa", "SOP-01")]:
        for k, v in _git(tmp_path, key=tmp_path / f"{who}.key").items():
            monkeypatch.setenv(k, v)
        assert main(["approve", subj, "--meaning", meaning, "--signer", who, "--root", str(tmp_path)]) == 0
    main(["baseline", "v1", str(tmp_path)])
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "baseline v1"], cwd=tmp_path, check=True)
    for k, v in _git(tmp_path, key=tmp_path / "rita.key").items():
        monkeypatch.setenv(k, v)
    assert main(["approve", "BL-v1", "--meaning", "released", "--signer", "rita", "--root", str(tmp_path)]) == 0
    ctx = rules.Context(project.load(tmp_path), git_root=tmp_path, release="v1")
    found = rules.run(ctx, only={"TL-D01", "TL-D03", "TL-D04", "TL-D05"}).findings
    assert found == []
