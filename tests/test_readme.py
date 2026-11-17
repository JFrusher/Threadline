from pathlib import Path

from threadline.rules import rule_table


def test_rule_reference_table_is_current():
    assert rule_table() in (Path(__file__).parents[1] / "docs" / "rules.md").read_text()
