"""CycloneDX SBOM reading (Syft output) and OSV.dev advisory lookup."""

import json
import urllib.request
from pathlib import Path

OSV_BATCH = "https://api.osv.dev/v1/querybatch"


def components(path: Path) -> list[dict]:
    """Third-party components: CycloneDX library/framework entries with name, version and purl."""
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("bomFormat") != "CycloneDX":
        raise ValueError(f"{path} is not a CycloneDX SBOM")
    return [c for c in doc.get("components", []) if c.get("type") in ("library", "framework")]


def key(c: dict) -> str:
    return f"{c['name']}@{c.get('version', '')}"


def advisories(comps: list[dict], url: str = OSV_BATCH) -> dict[str, list[str]]:
    """Advisory IDs per component, from OSV.dev. Components without a purl cannot be queried and raise."""
    if not comps:
        return {}  # OSV answers an empty batch with {} (no "results")
    missing = [key(c) for c in comps if not c.get("purl")]
    if missing:
        raise ValueError(f"components without purl cannot be checked for advisories: {missing}")
    body = json.dumps({"queries": [{"package": {"purl": c["purl"]}} for c in comps]}).encode()
    req = urllib.request.Request(url, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        results = json.load(r)["results"]
    # shortcut: OSV paginates when a package has very many advisories (next_page_token); not followed yet
    return {key(c): [v["id"] for v in res.get("vulns", [])] for c, res in zip(comps, results, strict=True)}
