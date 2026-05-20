---
name: eou-promote
description: |
  Evaluate whether an EOU should be promoted, deprecated, or retired based on evidence, maturity model, audits, run traces, and owner approval. Produces a recommendation only — does not execute any lifecycle transition (that is the role of activate/retire execution, which requires human approval).
  <example>
  Context: An EOU has been at pilot stage for two weeks; owner wants to know if it qualifies for active promotion.
  user: "$eou-promote eou-diagnose"
  assistant: "I'll check evidence against the maturity-model gates (audit pass, named owner, regression coverage, trace presence) and write a lifecycle recommendation. If gates are not met, recommendation is hold/demote, not activate."
  </example>
  <example>
  Context: User wants to evaluate retirement of an unused EOU.
  user: "$eou-promote eou-old-validator"
  assistant: "I'll evaluate retirement evidence (successor documented or owner decision recorded). I produce a recommendation, never the retirement itself."
  </example>
argument-hint: EOU_ID
arguments:
  - eou_id
allowed-tools:
  - Read
  - Write
  - Grep
---

# Evaluate EOU Lifecycle

Evaluate `$eou_id` against the maturity model and produce a lifecycle recommendation.

This skill has `function: promote` — it evaluates and recommends. It does not
execute lifecycle transitions. The human owner executes promotion via `activate`
and retirement via `retire` after approving this recommendation.

## Inputs

- `$eou_id` (required) — the EOU identifier to evaluate; must match a spec file and registry entry.
- `target_stage` (optional) — the lifecycle stage to transition to; if omitted, infer the logical next stage from the gate table.

## Required reading

1. `foundry/maturity-model.yml` — promotion gate requirements per lifecycle stage
2. `foundry/registry.yml` — current registration status and lifecycle stage
3. `foundry/governance.yml` — approval authority for lifecycle transitions

## Also read (to evaluate evidence)

4. `foundry/audits/eou-audits/{eou_id}.audit.yml` — most recent audit (required for `draft → pilot` and above)
5. `foundry/self-evolution/regression/cases/*.yml` — filter to YAML files where the `eou_id` field equals `$eou_id` — regression coverage
6. `foundry/runs/` — scan for `trace.yml` files containing `eou_id: {eou_id}` — execution traces required for `pilot → active`

## Promotion prerequisites (all must be satisfied)

| Gate | Required evidence |
|---|---|
| `candidate → draft` | At least one complete spec pass and one failed-case regression fixture |
| `draft → simulated` | Spec complete, dry-run or sandbox trace available, no open critical findings |
| `draft → pilot` | Passed `eou-audit`, ECP approved for any open findings, human owner on record |
| `pilot → active` | Minimum 3 successful pilot traces, zero open critical findings, human owner approval |
| `active → monitored` | Elevated-risk event or audit finding requiring close observation; no gate, owner decision |
| `monitored → stable` | Minimum 5 clean traces post-monitoring period, zero open high/critical findings |
| `stable → active` | Reverse to active when monitoring obligation lapses; owner decision |
| Any → `deprecated` | Owner decision recorded; replacement EOU or alternative documented |
| Any → `retired` | Superseded by successor EOU or determined to have no operational value; archived, not deleted |

## Stop conditions

Halt and report before proceeding if:
- `$eou_id` does not resolve to a spec file in `foundry/eous/` or `foundry/meta-eous/`.
- `$eou_id` is not present in `foundry/registry.yml`.
- `foundry/maturity-model.yml` does not exist — gate requirements cannot be evaluated without it.
- No target transition is specified and the current lifecycle stage has no obvious next step.

## Procedure

1. Load the EOU spec at `foundry/eous/{eou_id}.yml` (or `foundry/meta-eous/{eou_id}.yml`).
2. Identify the current `lifecycle_stage`.
3. Check each gate requirement for the target transition.
4. For each missing gate, record the gap and block the recommendation.
5. Write the lifecycle recommendation.

## Output

Write to `foundry/governance/lifecycle/{eou_id}.recommendation.yml`:

```yaml
eou_id:
current_stage:
recommended_action:  # promote_to | deprecate | retire | hold
target_stage:        # if promote_to
gate_results:
  - gate:
    satisfied: true | false
    evidence:  # file path or description
    gap:       # what is missing (if not satisfied)
recommendation_rationale:
requires_human_approval: true  # always true for promote_to:active, retire
```

## Constraints

- Output recommendation only — do not modify the EOU spec, registry, or governance files directly.
- Do not execute any lifecycle transition. Evaluation and execution are separate acts:
  - `function: promote` (this skill) — evaluate gates and recommend
  - `function: activate` — execute promotion to active (requires human approval)
  - `function: retire` — execute retirement (requires human approval)
- A missing audit, trace, or owner record blocks promotion — record the gap, do not invent evidence.
- `promote_to: active` always requires `requires_human_approval: true`.

## Scope Note

**Upstream:** receives an EOU id. Typically invoked when an EOU at pilot or active stage is being considered for the next lifecycle transition.

**Downstream:** produces a lifecycle recommendation only. Execution (activate, retire) is a separate human-approved step, not part of this skill — promote evaluates, humans decide.

**Related:** `$eou-audit` (upstream gate — audit pass is required input for promotion to active); the `activate` and `retire` execution functions (not skills, but governed verbs that consume this skill's recommendation after human approval).

**Pipeline:** `eou-audit (pass) → eou-promote → human approval → activate | retire`
