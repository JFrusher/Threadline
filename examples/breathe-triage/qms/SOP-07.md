---
id: SOP-07
type: document
doc_type: sop
title: Supplier and SOUP Control
rev: 2
status: effective
---
# SOP-07 Supplier and SOUP Control

**Purpose.** Control purchased product and software of unknown provenance (ISO 13485:2016 §7.4;
IEC 62304 §5.3.3, §5.3.4, §7.1.2, §8.1.2).

## Procedure
1. Every third-party component in the SBOM has an approved `soup` item: name, version, supplier, licence,
   purpose, class, functional/performance requirements, required hardware/software, anomaly list URL, review
   date and result, linked hazards, approver (TL-P01). Stale entries are removed (TL-P02).
2. Before a SOUP is added or upgraded, review its published anomaly list for issues that could contribute to a
   hazardous situation; record the result.
3. `sbom.yml` regenerates the CycloneDX SBOM with Syft and queries OSV.dev on every PR and weekly. Every advisory
   gets a `vulnerability` triage item (TL-P03).
4. Service suppliers (hosting, CI) are evaluated and listed with their acceptance criteria.

## Records
`dhf/soup/`, `records/vulnerabilities/`, SBOM per release.
