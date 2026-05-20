---
name: ecp-propose
description: |
  Create a formal EOU Change Proposal from a diagnosed failure or refactor option, capturing simulation, regression case, audit, and approval requirements per rule 92.
  <example>
  Context: $eou-diagnose has produced a diagnosis recommending a change. Owner wants to convert it into an actionable ECP.
  user: "$ecp-propose foundry/audits/incidents/inc-0042.diagnosis.yml"
  assistant: "I'll read the diagnosis, target_eou, and proposed change; draft an ECP under foundry/self-evolution/ecp/proposed/ with simulation, regression case, audit, and approval blocks. Status starts at proposed."
  </example>
  <example>
  Context: User wants an ECP for a refactor option produced by $eou-refactor.
  user: "$ecp-propose ./refactor-options/ro-split-audit-eou.yml"
  assistant: "I'll draft the ECP. If the target requires a constitution change, I'll stop and direct you to the constitutional ECP process instead."
  </example>
argument-hint: DIAGNOSIS_OR_REFACTOR_PATH
arguments:
  - target
allowed-tools:
  - Read
  - Write
  - Grep
---

# Propose ECP

Create a formal EOU Change Proposal (ECP) from `$target`.

## Inputs

- `$target` (required) — path to a diagnosis report (`foundry/audits/incidents/{id}.diagnosis.yml`) or a refactor option file (`foundry/self-evolution/refactor-options/{id}-refactor-*.yml`).

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

## Output

| Artifact | Path | Format |
|---|---|---|
| ECP proposal | `foundry/self-evolution/ecp/proposed/{target_eou}-ecp-{YYYYMMDD}.yml` | YAML, conforming to `schemas/ecp.schema.yml`. `approval.status` MUST be `proposed`. |
| Run trace | `foundry/runs/{eou_id}/{run_id}.yml` | YAML per `schemas/run-trace.schema.yml`. Records inputs read, failure class identified, and the ECP path written. |

This skill produces these two artifacts and nothing else. It does not mutate the target EOU, the registry, the constitution, or any approved/implemented ECP.

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

## Constraints

- Do not apply the ECP. Write only.
- Do not set `approval.status` to anything other than `proposed`.
- Do not propose changes to `foundry/constitution.yml` via ordinary ECP — constitutional changes require a separate process with explicit human review.
- High-risk changes (`risk_level: high` or `critical`) must include a non-empty `rollback_considerations` field.

## Scope Note

**Upstream:** receives diagnoses from `$eou-diagnose` (when `decision: change`) or refactor options from `$eou-refactor`.

**Downstream:** produces an ECP that enters the governed change pipeline: `simulate → regression-test → audit (eou-audit on the ECP package) → human approval → implement`.

**Related:** `$eou-diagnose` (sibling — produces the input), `$eou-refactor` (sibling — alternate input source), `$eou-audit` (downstream consumer when ECP is audited).

**Pipeline:** `eou-diagnose | eou-refactor → ecp-propose → simulate → audit → human approval → implement`
