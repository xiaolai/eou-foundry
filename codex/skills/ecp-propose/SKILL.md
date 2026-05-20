---
name: ecp-propose
description: Create a formal EOU Change Proposal from a diagnosed failure or refactor option.
---

# Propose ECP

Create a formal EOU Change Proposal (ECP) from `$target`.

## Required reading

1. `schemas/ecp.schema.yml` — field types and constraints
2. `foundry/constitution.yml` — invariants the ECP must not violate

## Stop conditions

Halt and report before drafting the ECP if:
- `$target` does not identify a concrete failure or refactor option — a goal that names no concrete failure class, incident id, or refactor-option id is not accepted.
- The `target_eou` cannot be determined from `$target`.
- The proposed change would require modifying `foundry/constitution.yml` — use the constitutional change process instead.

## Procedure

1. Read `$target` to extract the diagnosed failure or refactor option.
2. Identify the failure class (F1–F12 from `foundry/failure-taxonomy.yml`) driving the change.
3. Determine the smallest change that addresses the root cause without constitutional violation.
4. Draft the ECP with all required fields (see structure below).
5. Confirm `approval.status` is `proposed` — never set it higher.
6. Write the ECP to `foundry/self-evolution/ecp/proposed/{target_eou}-ecp-{YYYYMMDD}.yml`.
7. Record the run in `foundry/runs/{eou_id}/{run_id}.yml`.

## Required ECP fields

Field names match `schemas/ecp.schema.yml`. Do not use the old names (`eou_id`, `observed_problem`, `simulation_status`, `required_tests`).

```
id:                   # ecp-{target_eou}-{YYYYMMDD}
target_eou:           # ID of the EOU being changed
target_version_from:  # current version of the EOU (e.g. "0.2.0")
target_version_to:    # intended version after this change (e.g. "0.3.0")
failure_class:        # F1-F12 taxonomy code(s) — supplementary, not schema-required
problem:              # Concrete failure symptom, not a vague label
proposed_change:      # One specific structural change (scope, steps, inputs, authority, blast_radius, validators, stop_conditions, approval_requirements, or responsibility boundaries)
expected_benefit:     # Observable outcome if the change is applied
risks:                # What can go wrong; who is affected
tests_required:       # List of regression case IDs or new test fixtures to add
simulation:           # not_run | run_pass | run_fail
approval:
  status:             # must be "proposed" — never "approved" from this EOU
  approver:           # left blank until human owner approves
rollback_considerations: # How to revert if the change degrades outcomes (supplementary)
```

## Output

All output files written by this skill:

| Artifact | Path |
|----------|------|
| ECP proposal | `foundry/self-evolution/ecp/proposed/{target_eou}-ecp-{YYYYMMDD}.yml` |
| Run trace | `foundry/runs/{eou_id}/{run_id}.yml` |

## Constraints

- Do not apply the ECP. Write only.
- Do not set `approval.status` to anything other than `proposed`.
- Do not propose changes to `foundry/constitution.yml` via ordinary ECP — constitutional changes require a separate process with explicit human review.
- High-risk changes (`risk_level: high` or `critical`) must include a non-empty `rollback_considerations` field.
- `rollback_considerations` is supplementary in the schema but mandatory in this skill for high-risk changes — these two statements are not contradictory: the schema does not enforce presence, but this skill does.
