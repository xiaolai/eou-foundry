---
name: generate-eou-candidates
description: Generate a minimal, ranked candidate EOU set from a messy workflow using Foundry V2 constraints. Candidates are proposal-only and cannot be activated.
---

# Generate EOU Candidates

Generate candidate EOUs from `$workflow`.

## Inputs

- `$workflow` (required) — the workflow to analyze; may be a file path (YAML or Markdown) or a free-text description. If a file path, read it; if text, treat it as the workflow description.
- `workflow_slug` — derived from the workflow name or file stem, normalized to lowercase alphanumeric + hyphens (e.g., `code-review-workflow`). Used in the output filename.

## Required reading

1. `foundry/constitution.yml`
2. `foundry/registry.yml`
3. `foundry/failure-taxonomy.yml`
4. `foundry/meta-eous/generate-eou-candidates.yml`
5. `schemas/eou.schema.yml`

## Stop conditions

Halt and report if any of the following hold:

- Workflow goal is unclear.
- Desired artifact or output is undefined.
- No failure modes are provided or inferable.
- Responsibility boundary is unclear.
- High-stakes workflow has no identified owner.

## Procedure

### Step 1 — Summarize the workflow

Extract: what actor does what action to produce what artifact, and what the known failure modes are. State any ambiguities as open questions.

### Step 2 — Identify decision boundaries

Locate where the success criterion changes — each boundary is a candidate EOU boundary, not each visible action. Separate deterministic steps (scriptable) from judgment steps (LLM or human required).

### Step 3 — Registry diff

For each candidate boundary, check `foundry/registry.yml` and `foundry/eous/` + `foundry/meta-eous/`:

- Does this candidate duplicate an existing EOU? → record and skip.
- Can it extend an existing EOU? → record the extension recommendation.
- Should it be a refactor instead of a new EOU? → record.
- Would a rule, schema field, validator, stop condition, regression case, or human checklist serve better? → record and prefer that over a new EOU.

### Step 4 — Minimality test (per candidate)

For each remaining candidate, answer:

1. Can this be a rule instead of an EOU?
2. Can this be a validator or schema field?
3. Can this be a regression case?
4. Can this be a human review checklist?

Keep the candidate only if none of the above applies. Record the minimality result.

### Step 5 — Classify and fill required fields

For each kept candidate:

| Field | Value |
|-------|-------|
| `function` | One of: `generate \| specify \| validate \| diagnose \| promote \| refactor \| audit \| propose` |
| `automation_mode` | `deterministic \| LLM_assisted \| hybrid \| human_executed` |
| `authority_level` | `suggest_only \| draft_only \| write_candidate \| write_inactive \| mutate_active \| approve \| publish` |
| `risk_level` | `low \| medium \| high \| critical` |
| `lifecycle_stage` | `candidate` (always — do not set active) |

Also fill: `purpose`, `non_goal`, `distinct_success_criterion`, `failure_modes`, `owner_required`, `activation_requirements`, `operational_value`, `arguments_against`, `minimality_result`.

### Step 6 — Operational value test (per candidate)

Reject any candidate whose only value is completeness, or that duplicates an existing EOU, or that has no distinct success criterion. Each kept candidate must answer at least one: prevents_failure, improves_decision, exposes_hidden_judgment, improves_traceability.

### Step 7 — Rank and select minimal set

Budget: **max 7 candidates**. Rank by operational value descending. Select the minimal subset that covers the workflow's critical failure modes. Record rejected candidates with reasons.

## Output

Write to `foundry/self-evolution/ecp/proposed/{workflow_slug}-candidates-{YYYYMMDD}.yml`:

```yaml
source_workflow:
candidates:
  - id:
    purpose:
    non_goal:
    distinct_success_criterion:
    classification:
      function:
      automation_mode:
      authority_level:
      risk_level:
      lifecycle_stage: candidate
    failure_modes: []
    owner_required:
    activation_requirements: []
    operational_value:
    arguments_against:
    minimality_result:
rejected_candidates:
  - id:
    reason:
    prefer_instead:   # rule | schema_field | validator | regression_case | checklist | existing_eou
recommended_minimal_set: []
open_questions: []
registry_diff_notes: []
```

Record the run in `foundry/runs/{eou_id}/{run_id}.yml`. The `run_id` is `generate-eou-candidates-{YYYYMMDD}-{HHmmss}` using the current UTC time.

## Constraints

- Do not set `lifecycle_stage: active` on any candidate.
- Do not mutate `foundry/registry.yml` or any existing EOU spec.
- Do not weaken validators or change the constitution.
- Generate ≤ 7 candidates; if the workflow requires more, split the workflow first.
- Prefer fewer, sharper EOUs — a rule beats a new EOU every time.
- Do not proceed past Step 2 if the stop conditions are met — clarify before generating candidates.
- Every candidate in `recommended_minimal_set` must appear in the `candidates` list with all required fields populated.
