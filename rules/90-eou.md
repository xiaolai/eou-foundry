---
name: 90-eou
description: Require new or changed workflows to be defined as EOU specs under foundry/eous/ or foundry/meta-eous/. Forbids the deprecated root-level eous/ directory.
---

# Executable Operating Unit Rule

**Define or update workflows as EOU specs under `foundry/eous/` or `foundry/meta-eous/`.** A workflow without an EOU spec has no schema, no validator, no audit gate, and no governed path through promotion — it cannot be inspected, retired, or held accountable.

The canonical EOU layer is `foundry/`.

When adding or changing workflows, define or update an EOU spec under:

```text
foundry/eous/
foundry/meta-eous/
```

Do not use the superseded root-level `eous/` directory.

## Required faceted classification

Every EOU must declare all six classification facets using schema-allowed values:

| Facet | Allowed values |
|-------|----------------|
| `function` | `generate \| specify \| validate \| diagnose \| promote \| refactor \| audit \| propose \| activate \| implement \| retire` |
| `target_object` | (free text — name the artifact the EOU acts on) |
| `automation_mode` | `deterministic \| LLM_assisted \| hybrid \| human_executed` |
| `authority_level` | `suggest_only \| draft_only \| write_candidate \| write_inactive \| mutate_active \| approve \| publish` |
| `risk_level` | `low \| medium \| high \| critical` |
| `lifecycle_stage` | `candidate \| draft \| simulated \| pilot \| active \| monitored \| stable \| deprecated \| retired` |

## Required structural fields

Every EOU must declare:

- `purpose` with `statement` and `non_goals`
- `operating_hypothesis`
- `inputs` with `required`, `optional`, `forbidden_assumptions`
- `context_manifest` with `source_of_truth`, `supporting`, `forbidden`
- `execution` with `steps`, `decision_points`, `stop_conditions`, `allowed_tools`, `prohibited_actions`
- `outputs` with `primary`, `secondary`, `trace`
- `success_criteria` with `must_pass` and `should_pass`
- `validation` with `deterministic`, `judgment`
- `failure_modes` with `known`, `warning_signs`, `repair_actions`
- `escalation` with `require_human_when`
- `responsibility` with `executor`, `reviewer`, `approver`, `cannot_delegate`
- `versioning` with `changelog`
- `blast_radius` with `allowed_scope` and `forbidden_scope`

## Additional fields for generating EOUs

EOUs with `function: generate` must also declare:

- `generation_envelope` (with `allowed_outputs`, `forbidden_outputs`, `default_status: candidate`)
- `generation_budget` (with `max_candidates`)
- `registry_diff`
- `minimality_test`
- `operational_value_test`
- `counter_generation` (with `required: true`)

## Forbidden

- Placeholder text such as "Perform bounded operation", "target artifact", "What this EOU is meant to do".
- Omitting `non_goals` from `purpose`.
- Setting `lifecycle_stage: active` without a completed ECP and human approval.
- Setting `responsibility.executor` equal to `responsibility.approver`.
- Writing EOU specs to the deprecated root-level `eous/` directory.

## Violation indicators

A violation of this rule is present when any of the following is observed:

| Violation | Severity | Required action |
|-----------|----------|-----------------|
| One or more of the six classification facets is missing from an EOU spec | critical | Block promotion; record in audit report as `classification_incomplete` |
| A facet value is not in the schema-allowed set (e.g., `function: execute`) | high | Flag in audit; EOU cannot be promoted until corrected |
| Placeholder text found in any required field | high | Flag in audit; block promotion |
| `non_goals` absent from `purpose` | medium | Flag in audit; require fix before `draft → pilot` |
| `lifecycle_stage: active` set without an approved ECP on record | critical | Revert lifecycle stage; file ECP before proceeding |
| `responsibility.executor` equals `responsibility.approver` | critical | Self-approval violation; block promotion; raise `self_approval` audit finding |
| EOU spec written to deprecated `eous/` directory | high | Reject; move to `foundry/eous/` before accepting |
