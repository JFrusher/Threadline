from threadline import profiles


def test_ed2_draft_maps_classes():
    ed1 = profiles.lifecycle("iec62304-ed1")["activities"]
    ed2 = profiles.lifecycle("iec62304-ed2-draft")
    assert ed2["draft"] is True
    for a1, a2 in zip(ed1, ed2["activities"], strict=True):
        assert ("PRL-I" in a2["classes"]) == ("A" in a1["classes"])
        assert ("PRL-II" in a2["classes"]) == bool({"B", "C"} & set(a1["classes"]))
