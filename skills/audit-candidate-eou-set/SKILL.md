---
name: audit-candidate-eou-set
description: "Audit a generated candidate EOU set for boundary quality, minimality, overlap, authority, operational value, and governance risk."
argument-hint: CANDIDATE_SET_PATH
arguments:
  - path
allowed-tools:
  - Read
  - Write
  - Grep
---

# Audit Candidate EOU Set

Audit `$path`.

## Required reading

1. `foundry/constitution.yml`
2. `foundry/registry.yml`
3. `foundry/governance.yml`
4. `foundry/meta-eous/audit-candidate-eou-set.yml`

## Tests

- Boundary Test: each candidate has one distinct success criterion.
- Non-Overlap Test: candidates do not duplicate each other or existing EOUs.
- Minimality Test: candidate cannot be replaced by rule, validator, schema field, regression case, stop condition, or checklist.
- Authority Test: generating units cannot approve, publish, or mutate active governance.
- Operational Value Test: each candidate prevents a real failure or improves a real decision.
- Counter-Generation Test: each kept candidate includes arguments against creation.
- Set Composition Test: the set contains validation and approval paths when needed.
- High-Stakes Test: finance, health, legal, safety, children, public claims, publication, and governance require human ownership.

## Output

Write an audit report with:

- verdict: PASS / REVISE / FAIL
- candidates to keep
- candidates to merge
- candidates to reject
- candidates to convert into rule / validator / schema field / regression case / checklist
- required revisions before specification
