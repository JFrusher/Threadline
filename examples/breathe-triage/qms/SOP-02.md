---
id: SOP-02
type: document
doc_type: sop
title: Software Lifecycle
rev: 2
status: effective
---
# SOP-02 Software Lifecycle

**Purpose.** Define how medical device software is planned, built, verified, released and maintained
(IEC 62304:2006+A1:2015; UK designates EN 62304:2006 — see PRD §11).
**Scope.** All software items of the device, including SOUP.

## Procedure
1. **Plan (5.1).** A Software Development Plan (`doc_type: sdp`) states the lifecycle profile, software safety
   class (`threadline.yaml`), deliverables, tools, configuration management and problem resolution.
2. **Classify (4.3).** The software system and items are classified A/B/C (or PRL-I/PRL-II under the Ed2 draft
   profile) with a `classification` item and rationale.
3. **Requirements (5.2).** Software requirements are `software_requirement` items tracing to system requirements
   or risk controls (TL-L02).
4. **Architecture (5.3).** Architecture is described in a document (`doc_type: sad`) and `architecture_item`s,
   including SOUP used and segregation between items of different class.
5. **Implement and verify (5.4–5.7).** Every requirement and risk control is verified by a passing automated test
   linked with `@pytest.mark.verifies` (TL-E01, TL-R04). PR test runs gate merges.
6. **Release (5.8).** A `v*` tag runs `release.yml`: tests re-run on the tagged commit, SBOM generated, technical
   file built and attested. That run's JUnit file is the verification record.
7. **Maintain (6) and resolve problems (9).** Field problems enter through SOP-05; changes follow this SOP again.
8. **Configuration management (8).** Git is the configuration management system; SOUP is controlled by SOP-07.

## Records
SDP, SAD, items in `dhf/`, CI runs, release artefacts.
