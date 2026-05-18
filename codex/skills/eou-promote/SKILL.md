---
name: eou-promote
description: Evaluate whether an EOU should be promoted, deprecated, or retired based on evidence, maturity model, audits, and owner approval.
---

# Promote or Retire EOU

Evaluate `$eou_id` against the maturity model and produce a lifecycle recommendation.

## Required reading

1. `foundry/maturity-model.yml` — promotion gate requirements per lifecycle stage
2. `foundry/registry.yml` — current registration status and lifecycle stage
3. `foundry/governance.yml` — approval authority for lifecycle transitions

## Also read (to evaluate evidence)

- `foundry/audits/eou-audits/{eou_id}.audit.yml` — most recent audit
- `foundry/self-evolution/regression/cases/*.yml` — regression coverage
- `runs/*/trace.yml` where `eou_id` matches — execution traces

## Promotion prerequisites (all must be satisfied)

| Gate | Required evidence |
|---|---|
| `candidate → draft` | At least one complete spec pass and one failed-case regression fixture |
| `draft → pilot` | Passed `eou-audit`, ECP approved for any open findings, human owner on record |
| `pilot → active` | Minimum 3 successful pilot traces, zero open critical findings, human owner approval |
| Any → `deprecated` | Owner decision recorded; replacement EOU or alternative documented |
| Any → `retired` | Superseded by successor EOU or determined to have no operational value; archived, not deleted |

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
- A missing audit, trace, or owner record blocks promotion — record the gap, do not invent evidence.
- `promote_to: active` always requires `requires_human_approval: true`.
