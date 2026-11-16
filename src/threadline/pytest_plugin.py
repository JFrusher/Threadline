"""pytest plugin: `@pytest.mark.verifies("SRS-001", "RC-002")` writes JUnit `verifies` properties (ADR-002)."""

import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "verifies(*ids): item IDs this test verifies")
    # xunit2 schema has no testcase properties; evidence must be written in xunit1
    if config.option.xmlpath and config.getini("junit_family") != "xunit1":
        raise pytest.UsageError("threadline: set `junit_family = xunit1` in your pytest config")


@pytest.fixture(autouse=True)
def _threadline_verifies(request, record_property):
    for mark in request.node.iter_markers("verifies"):
        if not mark.args:
            raise pytest.UsageError(f"{request.node.nodeid}: @verifies needs at least one item ID")
        for item_id in mark.args:
            record_property("verifies", item_id)
