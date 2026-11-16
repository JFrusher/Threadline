from conftest import build_project

from threadline import rtm


def test_rtm_lists_trace_and_results(tmp_path):
    ctx = build_project(tmp_path, {
        "dhf/UN-001.yaml": {"id": "UN-001", "type": "user_need", "title": "N", "text": "x"},
        "dhf/SYS-001.yaml": {"id": "SYS-001", "type": "system_requirement", "title": "S", "text": "x",
                             "derives_from": ["UN-001"]},
        "dhf/SRS-001.yaml": {"id": "SRS-001", "type": "software_requirement", "title": "R", "text": "x",
                             "derives_from": ["SYS-001"]},
        "junit.xml": '<testsuite><testcase classname="t" name="a"><properties>'
                     '<property name="verifies" value="SRS-001"/></properties></testcase></testsuite>',
    })
    out = rtm.render(ctx)
    assert "| SRS-001 R | SYS-001 | UN-001 |  | PASS `t::a` |" in out
