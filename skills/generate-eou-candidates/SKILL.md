---
name: generate-eou-candidates
description: |
  Generate a minimal, ranked candidate EOU set from a messy workflow under Foundry V2 generation-envelope constraints. Candidates are proposal-only at lifecycle_stage candidate, with arguments_against and minimality results recorded per candidate; activation is forbidden at this stage.
  <example>
  Context: User has a workflow description and wants candidate EOUs to consider before specifying any.
  user: "$generate-eou-candidates Compile-chapter workflow: fetch source, parse, render, validate, publish."
  assistant: "I'll extract decision boundaries (not visible activity labels), test minimality per candidate (rule/validator/regression case alternatives), produce ≤ 7 candidates with arguments_against, and write a candidate-set artifact at foundry/self-evolution/candidate-sets/."
  </example>
  <example>
  Context: User points the skill at an existing YAML workflow description.
  user: "$generate-eou-candidates ./workflows/book-build.yml"
  assistant: "I'll load the workflow, run registry-diff against existing EOUs to avoid duplicates, and emit candidates only where a rule/validator/checklist cannot serve the need."
  </example>
argument-hint: WORKFLOW_DESCRIPTION_OR_FILE
arguments:
  - workflow
allowed-tools:
  - Read
  - Write
  - Grep
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
| `function` | One of: `generate \| specify \| validate \| diagnose \| promote \| refactor \| audit \| propose \| activate \| implement \| retire` |
| `automation_mode` | `deterministic \| LLM_assisted \| hybrid \| human_executed` |
| `authority_level` | `suggest_only \| draft_only \| write_candidate \| write_inactive \| mutate_active \| approve \| publish` |
| `risk_level` | `low \| medium \| high \| critical` |
| `lifecycle_stage` | `candidate` (always — do not set active) |

Also fill: `purpose`, `non_goals`, `distinct_success_criterion`, `failure_modes`, `owner_required`, `activation_requirements`, `operational_value`, `arguments_against`, `minimality_result`.

### Step 6 — Operational value test (per candidate)

Reject any candidate whose only value is completeness, or that duplicates an existing EOU, or that has no distinct success criterion. Each kept candidate must answer at least one: prevents_failure, improves_decision, exposes_hidden_judgment, improves_traceability.

### Step 7 — Rank and select minimal set

Budget: **max 7 candidates**. Rank by operational value descending. Select the minimal subset that covers the workflow's critical failure modes. Record rejected candidates with reasons.

## Output

Write to `foundry/self-evolution/candidate-sets/cs-generate-eou-candidates-{YYYYMMDD}-{hhmm}.yml` per `schemas/candidate-set.schema.yml` (ECP-0013):

```yaml
id: cs-generate-eou-candidates-{YYYYMMDD}-{hhmm}
generated_by: generate-eou-candidates
generated_at: {ISO-8601 UTC timestamp}
target_class: eou_spec
audit_status: pending_audit
source_workflow:
candidates:
  - id:
    status: candidate
    purpose:
    non_goals: []
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
audit_outcome:
  accepted: []
  merged: []
  demoted_to_rule: []
  demoted_to_validator: []
  demoted_to_stop_condition: []
  rejected: []
  minimal_recommended_subset: []
rejected_candidates:
  - id:
    reason:
    prefer_instead:   # rule | schema_field | validator | regression_case | checklist | existing_eou
open_questions: []
registry_diff_notes: []
```

The `audit_outcome` block is populated by `$audit-candidate-eou-set` (the downstream skill), not by this generator. Emit it with all seven keys present and empty; do not pre-populate. The generator's job ends at `audit_status: pending_audit`.

Record the run in `foundry/runs/{eou_id}/{run_id}.yml`. The `run_id` is `generate-eou-candidates-{YYYYMMDD}-{HHmmss}` using the current UTC time.

## Constraints

- Do not set `lifecycle_stage: active` on any candidate.
- Do not mutate `foundry/registry.yml` or any existing EOU spec.
- Do not weaken validators or change the constitution.
- Generate ≤ 7 candidates; if the workflow requires more, split the workflow first.
- Prefer fewer, sharper EOUs — a rule beats a new EOU every time.
- Do not proceed past Step 2 if the stop conditions are met — clarify before generating candidates.
- Every candidate in `recommended_minimal_set` must appear in the `candidates` list with all required fields populated.

## Scope Note

**Upstream:** top of the candidate pipeline. Receives a messy workflow description or a workflow YAML file.

**Downstream:** produces a candidate-set artifact at `foundry/self-evolution/candidate-sets/cs-{generator}-{YYYYMMDD}-{hhmm}.yml`, consumed by `$audit-candidate-eou-set`.

**Related:** `$audit-candidate-eou-set` (downstream consumer); `$eou-specify` (further downstream — consumes a single approved candidate from the audited set).

**Pipeline:** `messy workflow → generate-eou-candidates → audit-candidate-eou-set → human review → eou-specify → eou-audit`
