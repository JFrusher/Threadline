---
id: SOP-03
type: document
doc_type: sop
title: Risk Management
rev: 1
status: draft
---
# SOP-03 Risk Management

**Purpose.** Manage risk across the device lifecycle (ISO 14971:2019, guidance ISO/TR 24971:2020).

## Risk policy
The policy for determining acceptable risk is `risk:` in `threadline.yaml`: severity levels, P1 (probability the
hazardous situation occurs), P2 (probability it leads to harm), the combination table and the acceptability
matrix. `software_p1_rule` states how P1 is set for software failures. Top management approves the policy via an
approval of this SOP.

## Procedure
1. **Analyse (5).** Each hazard is a `hazard` item: hazard, sequence of events, hazardous situation, harm,
   severity, P1, P2 (TL-R01).
2. **Evaluate (6).** Initial risk is evaluated against the policy.
3. **Control (7.1–7.2).** Unacceptable risks get `risk_control` items, in order of priority: inherent safety by
   design, protective measures, information for safety (TL-R02). Design/protective controls are implemented by
   software requirements (TL-R03). **Every risk control is verified by a passing test** (TL-R04).
4. **Residual risk (7.3–7.4).** Residual severity/P1/P2 are recorded; an unacceptable residual needs a
   benefit-risk justification (TL-R05).
5. **New risks (7.5).** Every control records a `new_risk_review` (TL-R06).
6. **Overall residual risk (8) and review (9).** Evaluated in the risk management report generated at release and
   approved by QA.
7. **Production and post-production (10).** PMS (SOP-06), complaints (SOP-05) and vulnerabilities feed back into
   hazards.

## Records
`dhf/risk/`, risk management report, DCB0129 hazard log export (UK NHS deployments).
