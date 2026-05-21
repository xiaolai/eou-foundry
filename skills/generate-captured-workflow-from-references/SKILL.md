---
name: generate-captured-workflow-from-references
description: |
  Synthesize a Stage 0 captured_workflow (D2.4 step 1–5 outputs + per-app constitutional `domain_values` layer) from a user goal, structured 5-role reference set, and explicit constraints. For users entering an unfamiliar craft domain who cannot articulate a workflow unaided, and for any user who needs the constitutional layer made explicit before downstream EOU generation begins.
  <example>
  Context: A user wants to open a small seasonal restaurant but has never run one.
  user: "$generate-captured-workflow-from-references cooking — goal: small seasonal restaurant; references at refs/cooking.yml"
  assistant: "I'll load the goal and references, validate that all 5 role slots are filled with ≥1 user-contributed reference each, deconstruct the references for hidden judgments, failure modes, decision boundaries, and surface a 3–8 priority-ordered domain_values block. The output is a captured_workflow.yml that $generate-eou-candidates can consume."
  </example>
  <example>
  Context: An expert filmmaker wants to make their constitutional layer explicit before generating EOUs for a video-production app.
  user: "$generate-captured-workflow-from-references — video"
  assistant: "Stage 0 is useful even for domain experts. I'll surface your domain_values as a contested-form, priority-ordered block, require ≥1 user-contributed reference per role slot (V2 anti-abdication enforcement), and produce a captured_workflow at lifecycle_stage candidate. The captured_workflow stays at candidate permanently per the schema; it feeds downstream skills but never claims active status."
  </example>
argument-hint: APP_OR_DOMAIN_NAME [--refs PATH]
arguments:
  - app
  - refs
allowed-tools:
  - Read
  - Write
  - Grep
---

# Generate Captured Workflow from References

Synthesize a Stage 0 `captured_workflow` for `$app` from a structured reference set and constraints.

## What this skill does

One sentence — synthesize the inputs that D2.4 step 6 (`$generate-eou-candidates`) needs, plus the per-app constitutional `domain_values` layer, from a user goal + 5-role reference set + constraints + explicit user contributions.

## Inputs required

- `$app` (required) — the app or domain identifier; used in the output filename `cw-{slug}.yml`.
- `user_goal` (required) — outcome category in plain language ("I want to make X").
- `reference_set` (required) — mapping with all 5 role slots filled, each with `{ref, why}` entries:
  - `aspirational` — what the user wants to make
  - `anti_reference` — similar surface, wrong soul
  - `boundary_case` — edge of the field
  - `mainstream_baseline` — the median of the field
  - `outlier` — "I dislike this but it succeeds" (mandatory V1 defense against blind-spot encoding)
- `constraints` (required) — audience, scale, budget, time, risk_tolerance, desired_effect.
- `negative_constraints` (required) — what the user rejects explicitly.
- `user_contributed_references` (required) — ≥1 reference per role slot that the AI did not propose (V2 anti-abdication enforcement).
- `starter_pack` (optional) — `engine/starter-packs/{domain}.yml` if present and the user opts in.

## Inputs forbidden

- Pre-existing workflow prose — that input belongs to `$generate-eou-candidates`, not this skill. If the user can already articulate a workflow, this skill returns the `operational_value_test` reject decision and recommends `$generate-eou-candidates` directly.

## Required reading

1. `schemas/captured-workflow.schema.yml`
2. `dev-docs/06-values-over-rules.md`
3. `dev-docs/08-stage-0-design.md`
4. `engine/meta-eous/generate-captured-workflow-from-references.yml`

## Stop conditions

Halt and report if any of the following hold:

- Any role slot is empty after best-effort elicitation.
- `user_contributed_references` is empty for any slot (V2 violation).
- Fewer than 3 surviving `domain_values` after inclusion-test filtering.
- More than 8 surviving `domain_values` (cap mirrors foundry V1–V8 sizing).
- Counterfactual swap audit reveals fewer than 3 flips out of 5 tests (the value layer is decoration).
- User can articulate a workflow unaided (skill is the wrong tool; use `$generate-eou-candidates` directly).
- The app is governance scaffolding only with no real craft domain.

## Output path

`foundry/captured-workflows/cw-{slug}.yml` (one file per run; `{slug}` derived from `$app`).

Trace at `foundry/runs/generate-captured-workflow-from-references/{run_id}.yml` per ECP-0014 trace obligation.

## Procedure

### Step 1 — Validate inputs

Refuse early if any role slot is empty or `user_contributed_references` is empty per slot. These are V1 and V2 defenses; do not silently degrade.

### Step 2 — Per-reference justification

Each reference entry must have a `why`. If missing, prompt the user (or propose then require user confirmation in LLM_assisted mode).

### Step 3 — Counterfactual deconstruction → hidden_judgments

For each reference, ask: "What choices did the maker face? What judgments resolved them? What would have killed this work?" Surface the judgment predicates that explain the choices. Each judgment links to a candidate `domain_value` via `governed_by_value`.

### Step 4 — Negative-space analysis → failure_modes

Across the reference set and especially across the anti-references, surface failure patterns. Each failure mode links to a `domain_value` it violates (or to the literal `"multiple"` for meta-failures that don't map cleanly).

### Step 5 — Comparative analysis → decision_boundaries

Where references make consistently-different choices, name the decision boundary. Each boundary links to the `domain_value` that governs it (and optionally a `secondary_value` when multiple values are implicated).

### Step 6 — Convergence → artifact_target

Use reference convergence plus `constraints` to define what the app will produce, at what scale, with what shape.

### Step 7 — Synthesis → captured_workflow prose

Write the operating logic implied by Steps 3–6. Keep it tight; the prose is the human-readable summary, not the data layer.

### Step 8 — Pattern detection → candidate domain_values

Across the reference set, detect trade-offs that were repeatedly resolved the same way. For each, propose a `domain_value` in **contested form** ("X over Y" where Y must be a real opposing value, not a strawman). For each, run the 6-test inclusion check (`prevents_domain_failure`, `resolves_rule_conflict`, `exposes_hidden_judgment`, `resists_false_success`, `protects_invariant`, `removal_makes_practice_dangerous`); ≥1 true required.

### Step 9 — Priority ordering + canonical_or_personal

Surviving `domain_values` MUST be priority-ordered as a total order (exactly the integers `{1, ..., N}` for N values, no ties, no gaps). For each, mark `canonical_or_personal` (`field_canonical`, `user_personal`, `user_diverges_from_canonical`); when non-canonical, require `justification_if_diverges`.

### Step 10 — Confidence calibration

For each section (`artifact_target`, `hidden_judgments`, `failure_modes`, `decision_boundaries`, `domain_values`), record confidence as `low`, `medium`, or `high`. Be honest — `medium` is the default for taste-extraction outputs; `high` requires strong evidence.

### Step 11 — Bundle output + multi-gate approval

Write `cw-{slug}.yml` per the schema. Require user approval at **four separate gates**:
1. `reference_set_approved_by`
2. `constraints_approved_by`
3. `domain_values_approved_by`
4. `bundle_approved_by`

Same identity may fill multiple gates (e.g., a solo founder), but the gates are separately recorded so future governance can distinguish per-gate approval if needed.

## What this skill REFUSES to do

1. Refuse to produce `eou_candidate` or `candidate_set` artifacts. That is `$generate-eou-candidates`' job (D5.1 separation of judgment kinds).
2. Refuse to write outside `foundry/captured-workflows/` and the skill's own run-trace directory. Specifically refuse to touch `foundry/eous/`, `foundry/meta-eous/`, `foundry/registry.yml`, `foundry/self-evolution/`, `schemas/`, `engine/`.
3. Refuse to invent canonical practitioner claims without source citation. The skill never asserts "X is canonical in domain Y" — that is `domain_authority_claim`, listed in `forbidden_outputs`.
4. Refuse to mark `captured_workflow` at any `lifecycle_stage` other than `candidate`. The artifact stays at candidate permanently per the schema.
5. Refuse to produce a `domain_value` that contradicts a foundry V1–V8 invariant. Per D5.5, domain values can STRENGTHEN but cannot WEAKEN foundry values.

## Mechanism, not content

This skill contains zero domain assertions. The procedure above works for cooking, code, cinema, music, writing, therapy, teaching, investing — any craft domain. All domain content lives in the produced `captured_workflow` artifact and in the user's reference choices. The skill prose stays mechanism-only; if a future edit smuggles a domain assumption (e.g., "extract craft choices" presupposes that all domains have "craft"), audit the prose and remove the assumption.

## Constraints

- The output `captured_workflow` is `lifecycle_stage: candidate` permanently. It is never promoted higher.
- `risk_level: medium` (per ECP-0015 risk_level_decision) — errors propagate to every downstream EOU's success criteria via `domain_values` invocation; audit cadence is per major version.
- Single-output specialization of rule-95 generating-EOU pattern — the skill produces ONE `captured_workflow` per run (`max_candidates: 1`); the multi-element structure is INSIDE the artifact (5 role slots × ≤5 refs; 3–8 domain_values; etc.).
- Trace is mandatory per ECP-0014; record at `foundry/runs/generate-captured-workflow-from-references/{run_id}.yml`.

## Scope Note

**Upstream:** top of the Stage 0 pipeline. Receives user goal, reference set, constraints from the user directly (or from a starter pack if opted in).

**Downstream:** produces `foundry/captured-workflows/cw-{slug}.yml`, consumed by `$generate-eou-candidates` (when present + approved, scoring consults `domain_values` per Rule 96), by `$audit-candidate-eou-set` (Set Value Coverage Test), and by `$eou-audit` (Value Operationalization Test on specs at `pilot` or higher).

**Related:** `$generate-eou-candidates` (downstream consumer); `$audit-candidate-eou-set`, `$eou-audit` (downstream auditors that enforce Rule 96).

**Pipeline:** `user goal + references → generate-captured-workflow-from-references → captured_workflow → generate-eou-candidates → audit-candidate-eou-set → human review → eou-specify → eou-audit`

**Optionality:** Stage 0 is OPTIONAL. Apps without a captured_workflow use `$generate-eou-candidates` directly with workflow prose, exactly as before.
