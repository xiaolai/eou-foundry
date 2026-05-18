---
name: eou-diagnose
description: "Diagnose EOU failures using the Foundry failure taxonomy and recommend the smallest repair path."
argument-hint: INCIDENT_OR_AUDIT_PATH
arguments:
  - target
allowed-tools:
  - Read
  - Write
  - Grep
---

# Diagnose EOU Failure

Diagnose `$target`.

Use `foundry/failure-taxonomy.yml`.

Classify each failure as F1-F12 and recommend repair:

- schema repair
- context manifest repair
- stop condition
- validator
- regression case
- ECP
- human approval gate
- EOU split/merge/retire

Do not treat all failures as prompt problems.
