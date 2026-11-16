---
id: SOP-10
type: document
doc_type: sop
title: Tool Validation
rev: 1
status: effective
---
# SOP-10 Tool Validation

**Purpose.** Validate software used in the QMS and in product realisation (ISO 13485:2016 §4.1.6, §7.5.6;
approach per ISO/TR 80002-2).

## Procedure
1. List each tool with its intended use in the QMS: Threadline, GitHub (repository, Actions), pytest, Syft,
   Pandoc/LaTeX.
2. Assess the risk of the tool failing in that use (could a failure let a nonconforming device ship?).
3. Choose validation effort proportional to risk. For Threadline: its fixture suite proves every rule fails on
   bad input and passes on good input; the release ships that suite's results as a validation report. The
   manufacturer reviews it and adds tests for its own configuration.
4. Re-validate on every tool version change (pin versions in workflows).

## Records
Tool validation report per release, this SOP's approvals.
