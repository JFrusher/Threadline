import io
import json

import pytest

from threadline import sbom


def test_components_filters_libraries(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"bomFormat": "CycloneDX", "components": [
        {"type": "library", "name": "numpy", "version": "2.1.3", "purl": "pkg:pypi/numpy@2.1.3"},
        {"type": "file", "name": "x.py"},
    ]}))
    assert [c["name"] for c in sbom.components(p)] == ["numpy"]


def test_components_rejects_non_cyclonedx(tmp_path):
    p = tmp_path / "s.json"
    p.write_text("{}")
    with pytest.raises(ValueError):
        sbom.components(p)


def test_advisories_from_recorded_osv_response(monkeypatch):
    # recorded from api.osv.dev on 2026-11-16
    recorded = {"results": [{"vulns": [{"id": "GHSA-fpfv-jqm9-f5jm", "modified": "2023-11-08T04:06:07Z"}]}, {}]}
    sent = {}

    def fake_urlopen(req, timeout):
        sent["body"] = json.loads(req.data)
        return io.BytesIO(json.dumps(recorded).encode())

    monkeypatch.setattr(sbom.urllib.request, "urlopen", fake_urlopen)
    comps = [{"name": "numpy", "version": "1.21.0", "purl": "pkg:pypi/numpy@1.21.0"},
             {"name": "numpy", "version": "2.1.3", "purl": "pkg:pypi/numpy@2.1.3"}]
    assert sbom.advisories(comps) == {"numpy@1.21.0": ["GHSA-fpfv-jqm9-f5jm"], "numpy@2.1.3": []}
    assert sent["body"]["queries"][0] == {"package": {"purl": "pkg:pypi/numpy@1.21.0"}}


def test_advisories_refuses_component_without_purl():
    with pytest.raises(ValueError):
        sbom.advisories([{"name": "x", "version": "1"}])


def test_advisories_for_no_components_makes_no_request(monkeypatch):
    monkeypatch.setattr(sbom.urllib.request, "urlopen", lambda *a, **k: pytest.fail("no request expected"))
    assert sbom.advisories([]) == {}
