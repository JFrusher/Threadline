from importlib.resources import files

import pytest

from threadline import project, rules
from threadline.cli import main

PRESETS = sorted(p.name for p in (files("threadline") / "data" / "presets").iterdir())


def test_four_presets_ship():
    assert PRESETS == ["low-bandwidth-telemetry", "ml-34971", "offline-queue", "power-loss"]


@pytest.mark.parametrize("name", PRESETS)
def test_preset_loads_and_demands_team_estimates(name, tmp_path):
    main(["init", str(tmp_path / "q")])
    assert main(["preset", "add", name, str(tmp_path / "q")]) == 0
    ctx = rules.Context(project.load(tmp_path / "q"))
    assert ctx.project.load_errors == []
    found = {f.rule for f in rules.run(ctx).findings}
    assert {"TL-R01", "TL-R06"} <= found  # severity/probabilities and new-risk review are the team's job
    assert {"TL-L01", "TL-L02", "TL-R03"}.isdisjoint(found)  # the pack itself is fully linked
    hazards = [i for i in ctx.project.of_type("hazard")]
    assert hazards and all(h.references for h in hazards)
    with pytest.raises(SystemExit, match="already added"):
        main(["preset", "add", name, str(tmp_path / "q")])


def test_unknown_preset(tmp_path):
    with pytest.raises(SystemExit, match="available"):
        main(["preset", "add", "nope", str(tmp_path)])
