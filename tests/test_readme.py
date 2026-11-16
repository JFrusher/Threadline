from pathlib import Path

from threadline.rules import rule_table


def test_readme_rule_table_is_current():
    assert rule_table() in (Path(__file__).parents[1] / "README.md").read_text()
