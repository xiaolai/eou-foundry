---
name: ecp-propose
description: Create a formal EOU Change Proposal from a diagnosed failure or refactor option.
---

# Propose ECP

Create a formal EOU Change Proposal (ECP) from `$target`.

## Required reading

1. `schemas/ecp.schema.yml` — field types and constraints
2. `foundry/constitution.yml` — invariants the ECP must not violate

## Procedure

1. Read `$target` to extract the diagnosed failure or refactor option.
2. Identify the failure class (F1–F12 from `foundry/failure-taxonomy.yml`) driving the change.
3. Determine the smallest change that addresses the root cause without constitutional violation.
4. Draft the ECP with all required fields (see structure below).
5. Confirm `approval.status` is `proposed` — never set it higher.
6. Write the ECP to `foundry/self-evolution/ecp/proposed/{eou_id}-ecp-{YYYYMMDD}.yml`.
7. Record the run in `runs/{run_id}/trace.yml`.

## Required ECP fields

```
id:               # ecp-{eou_id}-{YYYYMMDD}
eou_id:           # ID of the EOU being changed
failure_class:    # F1-F12 taxonomy code(s)
observed_problem: # Concrete failure symptom, not a vague label
proposed_change:  # One specific structural change (scope, steps, inputs, authority, etc.)
expected_benefit: # Observable outcome if the change is applied
risks:            # What can go wrong; who is affected
required_tests:   # List of regression case IDs or new test fixtures to add
simulation_status: # not_run | run_pass | run_fail
approval:
  status:         # must be "proposed" — never "approved" from this EOU
  approver:       # left blank until human owner approves
rollback_considerations: # How to revert if the change degrades outcomes
```

## Constraints

- Do not apply the ECP. Write only.
- Do not set `approval.status` to anything other than `proposed`.
- Do not propose changes to `foundry/constitution.yml` via ordinary ECP — constitutional changes require a separate process with explicit human review.
- High-risk changes (`risk_level: high` or `critical`) must include a non-empty `rollback_considerations` field.
