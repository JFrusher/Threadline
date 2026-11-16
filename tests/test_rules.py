"""Tool validation suite: every rule has a fixture that must pass and one that must fail."""

import pytest
from conftest import FIXTURES, build_project
from ruamel.yaml import YAML

import threadline.checks  # noqa: F401
from threadline import rules

RULE_IDS = sorted(rules.RULES)


def _fixture(rule_id):
    return YAML(typ="safe").load((FIXTURES / f"{rule_id}.yaml").read_text())


def test_every_rule_has_a_fixture():
    missing = [r for r in RULE_IDS if not (FIXTURES / f"{r}.yaml").exists()]
    assert not missing


@pytest.mark.parametrize("rule_id", RULE_IDS)
def test_rule_passes(rule_id, tmp_path):
    ctx = build_project(tmp_path, _fixture(rule_id)["pass"])
    result = rules.run(ctx, only={rule_id})
    assert not result.skipped, "pass fixture must supply what the rule needs"
    assert result.findings == []


@pytest.mark.parametrize("rule_id", RULE_IDS)
def test_rule_fails(rule_id, tmp_path):
    ctx = build_project(tmp_path, _fixture(rule_id)["fail"])
    findings = rules.run(ctx, only={rule_id}).findings
    assert findings and all(f.rule == rule_id for f in findings)
