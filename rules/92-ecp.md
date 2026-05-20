---
name: 92-ecp
description: "Require an EOU Change Proposal for significant Foundry mutations: EOU purpose, authority level, validators, schema fields, promotion rules, generation envelope, or constitution."
---

# EOU Change Proposal Rule

**File an ECP before applying any significant Foundry mutation.** Without an ECP, the change has no recorded rationale, no simulation, no regression case, no audit, and no approver — every one of which is the evidence that distinguishes governed change from silent mutation.

Significant Foundry mutations require an ECP before the change is applied.

## MUST have an ECP (blocking)

The following changes may not be applied without an approved ECP:

- `purpose.statement` — changing what an EOU does
- `classification.authority_level` — raising or lowering authority
- `classification.risk_level` — changing risk tier
- `generation_envelope` — any change to allowed/forbidden outputs or default status
- `responsibility.executor`, `responsibility.approver` — changing ownership
- `validation.deterministic` or `validation.judgment` — adding or removing checks
- `blast_radius.allowed_scope` or `blast_radius.forbidden_scope` — widening or narrowing
- Any field in `foundry/constitution.yml` or `foundry/governance.yml`
- Promotion to `lifecycle_stage: active` or retirement

## SHOULD have an ECP (non-blocking but recommended)

- Adding or removing `stop_conditions`
- Adding or removing `failure_modes`
- Adding or removing `escalation.require_human_when` entries
- Changing `execution.steps` in ways that affect observable outputs

## ECP required fields (from `schemas/ecp.schema.yml`)

```yaml
target_eou:           # EOU ID being changed
problem:              # observed failure or gap triggering the proposal
failure_class:        # F1–F12 code from failure-taxonomy.yml
proposed_change:      # what changes and why
risks:                # what could go wrong
tests_required:       # what tests must pass before activation
simulation:           # simulation or dry-run result
approval:
  status:             # proposed | approved | rejected | implemented
  approver:           # named human identity — populated when approved
rollback_considerations: # how to revert if the change fails
```

## Output path

`foundry/self-evolution/ecp/proposed/{target_eou}-ecp-{YYYYMMDD}.yml`

## SHOULD violation indicators

SHOULD items are non-blocking but should be recorded in the audit when skipped:

| Skipped SHOULD item | Finding | Severity |
|---------------------|---------|----------|
| `stop_conditions` added/removed without ECP | `missing_ecp_for_stop_condition_change` | low |
| `failure_modes` added/removed without ECP | `missing_ecp_for_failure_mode_change` | low |
| `escalation.require_human_when` entries changed without ECP | `missing_ecp_for_escalation_change` | low |
| `execution.steps` changed in ways affecting observable outputs | `missing_ecp_for_step_change` | medium |

## Unauthorized mutation

Applying a MUST-have-ECP change without an approved ECP is a constitution violation. Revert the change and file the ECP before proceeding.
