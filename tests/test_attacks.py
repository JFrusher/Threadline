"""Attack and integrity cases. Each test is an exploit that must FAIL to work."""

import subprocess

from conftest import build_project

from threadline import rules

APR = ('id: {id}\ntype: approval\ntitle: A\nsubject: SOP-01\nsubject_rev: 1\nsubject_sha256: x\n'
       'meaning: approved_as_qa\nsigner: {signer}\nsigned_at: "2026-11-16T10:00:00Z"\n')
SETUP = """
git init -q && git config user.name t && git config user.email t@x && git config commit.gpgsign false
git config gpg.format ssh && git config gpg.ssh.program ssh-keygen
mkdir -p qms/signers records && ssh-keygen -q -t ed25519 -N "" -f quinn.key && ssh-keygen -q -t ed25519 -N "" -f eve.key
echo "quinn $(cat quinn.key.pub)" > qms/signers/allowed_signers
git add qms && git -c user.signingkey=$PWD/quinn.key commit -qS -m root-of-trust
"""


def _findings(ctx, rule_ids):
    return [f for f in rules.run(ctx, only=set(rule_ids)).findings]


def test_attacker_cannot_self_register_a_key(tmp_path):
    # eve adds her own key in an unsigned commit, then signs an approval with it
    script = SETUP + f"""
echo "eve $(cat eve.key.pub)" >> qms/signers/allowed_signers && git add qms && git commit -qm "add eve"
printf '{APR.format(id="APR-1", signer="eve")}' > records/APR-1.yaml
git add records && git -c user.signingkey=$PWD/eve.key commit -qS -m approve
"""
    ctx = build_project(tmp_path, {"git": script, "threadline.yaml": {"signers": {
        "quinn": {"name": "Q", "roles": ["qa"]}, "eve": {"name": "E", "roles": ["qa"]}}}})
    assert _findings(ctx, {"TL-D03", "TL-D04"}), "self-registered key accepted"


def test_failing_test_is_not_hidden_by_a_passing_one(tmp_path):
    junit = ('<testsuite><testcase classname="t" name="ok"><properties><property name="verifies" value="RC-001"/>'
             '</properties></testcase><testcase classname="t" name="bad"><properties>'
             '<property name="verifies" value="RC-001"/></properties><failure/></testcase></testsuite>')
    ctx = build_project(tmp_path, {
        "dhf/RC-001.yaml": {"id": "RC-001", "type": "risk_control", "title": "C", "kind": "protective_measure",
                            "text": "x", "new_risk_review": "none"},
        "junit.xml": junit})
    assert _findings(ctx, {"TL-R04"}), "risk control with a failing verification test counted as verified"


def test_obsolete_control_cannot_still_carry_a_hazard(tmp_path):
    ctx = build_project(tmp_path, {
        "dhf/HAZ-001.yaml": {"id": "HAZ-001", "type": "hazard", "title": "H", "hazard": "h", "hazardous_situation": "s",
                             "harm": "d", "severity": "catastrophic", "p1": "high", "p2": "high",
                             "controls": ["RC-001"], "residual": {"p1": "low", "p2": "low"},
                             "benefit_risk": "justified"},
        "dhf/RC-001.yaml": {"id": "RC-001", "type": "risk_control", "title": "C", "kind": "protective_measure",
                            "text": "x", "status": "obsolete", "new_risk_review": "none"},
        "dhf/SRS-001.yaml": {"id": "SRS-001", "type": "software_requirement", "title": "R", "text": "x",
                             "implements": ["RC-001"]},
        "junit.xml": "<testsuite/>"})
    found = [f for f in rules.run(ctx).findings if f.item == "HAZ-001"]
    assert found, "hazard relies on an obsolete control"


def test_approval_binds_document_metadata(tmp_path):
    from threadline.checks.documents import content_hash
    h = content_hash("Approved text.")
    doc = "---\nid: SOP-01\ntype: document\ndoc_type: {t}\ntitle: T\nrev: 1\nstatus: effective\n---\nApproved text.\n"
    ctx = build_project(tmp_path, {
        "threadline.yaml": {"signers": {"ann": {"name": "A", "roles": ["author"]}, "q": {"name": "Q", "roles": ["qa"]}},
                            "approvals_required": {"*": ["authored", "approved_as_qa"], "note": ["authored"]}},
        "qms/SOP-01.md": doc.format(t="note"),  # was approved as an sop; doc_type changed afterwards
        "records/APR-1.yaml": {"id": "APR-1", "type": "approval", "title": "a", "subject": "SOP-01",
                               "subject_rev": 1, "subject_sha256": h, "meaning": "authored", "signer": "ann",
                               "signed_at": "2026-11-16T10:00:00Z"}})
    assert _findings(ctx, {"TL-D01"}), "doc_type changed after approval without invalidating it"


def test_model_paths_stay_inside_project(tmp_path):
    ctx = build_project(tmp_path, {"dhf/MODEL-001.yaml": {
        "id": "MODEL-001", "type": "model", "title": "M", "training_code": "t", "weights_path": "/etc/hostname",
        "weights_sha256": "x"}})
    assert any("outside" in f.message for f in _findings(ctx, {"TL-M02"})), "path outside project hashed"


def test_raw_latex_in_items_is_not_executed(tmp_path):
    from threadline import build
    ctx = build_project(tmp_path, {"dhf/UN-001.yaml": {"id": "UN-001", "type": "user_need", "title": "N",
                                                       "text": r"\input{/etc/hostname}"}})
    md = build.assemble(ctx, rules.run(ctx), [], None, "v", "0" * 40)
    tex = subprocess.run(["pandoc", "-f", build.PANDOC_FROM, "-t", "latex"], input=md, capture_output=True,
                         text=True, check=True).stdout
    assert r"\input{/etc/hostname}" not in tex, "raw LaTeX passed through to the PDF engine"


def test_crlf_checkout_is_not_a_tamper(tmp_path):
    # Windows checkouts with core.autocrlf=true have CRLF in the working tree, LF in the commit
    script = SETUP + f"""
printf '{APR.format(id="APR-1", signer="quinn")}' > records/APR-1.yaml
git add records && git -c user.signingkey=$PWD/quinn.key commit -qS -m approve
sed -i 's/$/\\r/' records/APR-1.yaml
"""
    ctx = build_project(tmp_path, {"git": script, "threadline.yaml": {"signers": {
        "quinn": {"name": "Q", "roles": ["qa"]}}}})
    assert not _findings(ctx, {"TL-D03"}), "line-ending conversion reported as tampering"


def test_images_cannot_pull_in_runner_files(tmp_path):
    import pytest

    from threadline import build
    for target in ["/etc/hostname", "../outside.png", "https://example.com/x.png", "[x]: /etc/hostname"]:
        md = f"![x]({target})" if not target.startswith("[") else f"![x][x]\n\n{target}\n"
        with pytest.raises(SystemExit, match="images must be relative"):
            build.check_images(md, tmp_path)
    (tmp_path / "ok.png").write_bytes(b"x")
    build.check_images("![ok](ok.png)", tmp_path)
