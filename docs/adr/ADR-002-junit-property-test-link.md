# ADR-002: A JUnit property is the only test → item link

**Status:** accepted · 2026-11-16

## Context
Tests prove requirements and risk controls. Common ways to link them — IDs in test names, docstrings, comments,
side files — drift and differ per language.

## Decision
A test verifies an item when its JUnit XML testcase has `<property name="verifies" value="SRS-014"/>`.
Threadline ships a pytest marker, `@pytest.mark.verifies("SRS-014")`, that writes the property.
Other frameworks emit the same property (e.g. GoogleTest `RecordProperty("verifies", "SRS-014")`).

A test passes when the testcase has no `<failure>`, `<error>` or `<skipped>` child.

## Consequences
- One parser, any language that writes JUnit XML.
- Name and docstring conventions are not read. A test without the property verifies nothing.
- PR runs gate merges. Only the run on the release tag is kept as verification evidence (PRD §5.4).
