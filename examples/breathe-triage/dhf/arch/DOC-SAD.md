---
id: DOC-SAD
type: document
doc_type: sad
title: Software Architecture
rev: 1
status: draft
---
# Software Architecture — Breathe-Triage

```mermaid
flowchart LR
  UI[UI shell<br/>class B] -->|age, taps, danger signs| CNT[Count<br/>class C]
  CNT -->|rate| CLS[Classifier<br/>class C]
  UI -->|danger signs| CLS
  CLS -->|classification + action| UI
  UI --> Q[(Offline queue<br/>class B)]
```

The classifier and counter (class C) are pure functions with no I/O and no SOUP. The UI shell and offline queue
(class B) cannot change a classification: they only display and store it. Segregation is by module boundary and by
the rule that class C code imports nothing outside the standard library (SRS-011 test).
