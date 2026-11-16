from threadline import profiles


def test_ed2_draft_maps_classes():
    ed1 = profiles.lifecycle("iec62304-ed1")["activities"]
    ed2 = profiles.lifecycle("iec62304-ed2-draft")
    assert ed2["draft"] is True
    for a1, a2 in zip(ed1, ed2["activities"], strict=True):
        assert ("PRL-I" in a2["classes"]) == ("A" in a1["classes"])
        assert ("PRL-II" in a2["classes"]) == bool({"B", "C"} & set(a1["classes"]))


def test_regulatory_checklists_parse_cleanly():
    for name in ("qms-iso13485", "uk-mhra", "au-model-law"):
        prof = profiles.regulatory(name)
        ids = [e["id"] for e in prof["checklist"]]
        assert len(ids) == len(set(ids)), name
        for e in prof["checklist"]:
            assert set(e) == {"id", "clause", "title"}, (name, e)


def test_lifecycle_activities_parse_cleanly():
    for a in profiles.lifecycle("iec62304-ed1")["activities"]:
        assert set(a) == {"clause", "title", "classes", "requires"}, a
        assert len(a["requires"]) == 1, a
