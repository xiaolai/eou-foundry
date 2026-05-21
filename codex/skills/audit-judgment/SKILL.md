---
name: audit-judgment
description: Audit value_invocations in run traces for EOUs with classification.judgment_authorized:true. Verifies invocations against the captured_workflow's declared priority (no F15), checks for drift over multiple runs (no F16), detects hallucinated value ids (no F17), catches silent decisions on contested cases (F14), and runs counterfactual-swap audit as the V1 anti-theater defense.
---

# Audit Judgment

Audit the value_invocations of `$target` — an EOU with `classification.judgment_authorized:true` — against Rule 97 and the F14–F17 failure taxonomy.

## What this skill does

Performs the fourth audit layer per D4.1 (post-ECP-0019). Audits agentic-judgment correctness, not output validity (that's `$eou-validate`), run correctness (run-trace validation), or EOU design (that's `$eou-audit`). The four layers compose; this skill is the agentic-judgment specialist.

## Inputs

- `$target` (required) — EOU ID resolved to `foundry/eous/{id}.yml` or `foundry/meta-eous/{id}.yml`, or a direct file path. Must have `classification.judgment_authorized:true`.
- Auto-discovered: `foundry/captured-workflows/cw-*.yml` (the app's constitution); `foundry/runs/{target}/` (run traces); optionally `foundry/audits/eou-audits/{target}.audit.yml` (prior $eou-audit findings).

## Required reading

1. `target_eou_spec` (the EOU under audit)
2. `foundry/captured-workflows/` (find the approved captured_workflow for the app)
3. `rules/97-value-invocation.md`
4. `engine/failure-taxonomy.yml` (F14–F17 definitions)
5. `engine/maturity-model.yml` (judgment_maturity J0–J4 axis)
6. `schemas/run-trace.schema.yml` (value_invocations entry shape)
7. `engine/meta-eous/audit-judgment.yml`

## Stop conditions

Halt and report without running checks if:

- Target EOU has `judgment_authorized:false` or absent — Rule 97 does not apply.
- No captured_workflow with complete `human_approval` exists for the app — judgment_authorized:true would itself be a validator failure per ECP-0018.
- Target EOU is at `lifecycle_stage: candidate` or `draft` — Rule 97 enforcement begins at `simulated` per the exemption clause.
- No run traces exist under `foundry/runs/{target}/` — judgment_maturity is J0 or J1; nothing to audit yet. Emit "judgment_maturity:J1_INVOCATION_NAIVE — no runs to audit" status.

## Procedure

### Step 1 — Load and verify preconditions

Load `target_eou_spec`. Verify `judgment_authorized:true`. If false → "rule does not apply"; return.

Load the app's captured_workflow (longest-prefix-match path per Rule 96 multi-tenant resolution). Verify `human_approval` complete at all four gates and `domain_values` count ≥3. If not → emit precondition failure (matches ECP-0018 validator).

### Step 2 — F17 check (value hallucination)

For each `value_invocations` entry across all run traces: verify `domain_value_id` resolves to an id in the captured_workflow's current `domain_values` list. Mismatched ids → F17 finding (severity blocking).

### Step 3 — F15 check (value hierarchy violation)

For each invocation: examine `rule_conflict` and `priority_at_invocation`. If a higher-priority `domain_value` would have resolved the same conflict differently (cross-reference the captured_workflow's `decides_when` blocks), flag F15 (severity high).

### Step 4 — F16 check (value drift)

Across ≥3 runs, compute invocation distribution per `domain_value_id`. Compare actual invocation frequency to declared priority weights (priority 1 = highest, expected highest invocation frequency on contested cases that it governs). Deviations >20% on top-three values → F16 finding (severity high). Skip with "drift not yet evaluable" if <3 runs.

### Step 5 — F14 check (silent judgment)

Scan run traces for execution steps that indicate contested cases (entries in `decision_points` flagged as contested or matching contested-case heuristics) but lack a corresponding `value_invocations` entry AND lack an `escalations_triggered` entry referencing the case. Each unrecorded contested case → F14 finding (severity blocking at pilot+; high at draft).

### Step 6 — Counterfactual-swap audit (V1 anti-theater defense)

For up to 5 sampled invocations (configurable via `generation_budget.max_swap_tests`):

1. Construct a swapped hypothetical captured_workflow where the invoked value's priority is swapped with a different value's priority. Alternate the swap target across swap-tests to cover priority pairs.
2. Re-run the producing EOU under the swapped captured_workflow (write_candidate authority; runs isolated to `foundry/runs/audit-judgment/swap-tests/{run_id}/` and never affect production).
3. For non-deterministic LLM_assisted target EOUs, also run ≥2 baseline control runs at the original priority to measure natural output variance.
4. Compare each swap-test output to the baseline.
5. If ≥3 of 5 swap-tests produce output changes that exceed baseline variance, invocations are load-bearing — PASS.
6. If <3 swap-driven changes, emit HIGH-severity F14 (theater pattern) — invocations may be decoration.

### Step 7 — Compose judgment-audit report

Write to `foundry/audits/judgment-audits/{target}.judgment-audit.yml`:

```yaml
audit_date:
target_eou:
target_eou_version:
captured_workflow_id:
captured_workflow_version:
runs_analyzed:           # list of run_ids
checks:
  - check_name: F17 | F15 | F16 | F14 | counterfactual_swap
    status: pass | fail | skip
    findings:
      - severity: blocking | high | medium | low
        invocation_id:    # for F14-F17 (or null for F14 silent case)
        description:
        required_fix:
counterfactual_swap_audit:
  swap_tests_run:
  swap_tests_with_output_change:
  baseline_variance_runs:
  verdict: PASS | FAIL
summary:
  total_findings:
  by_severity: {blocking: 0, high: 0, medium: 0, low: 0}
  verdict: PASS | FAIL | CONDITIONAL_PASS
  judgment_maturity_recommendation: J1 | J2 | J3 | J4
```

Record the audit run trace at `foundry/runs/audit-judgment/{run_id}.yml` per ECP-0014 trace obligation.

## What this skill REFUSES to do

1. **Refuse to invoke values.** audit-judgment audits invocations; it does not invoke. `judgment_authorized:false` on its own classification.
2. **Refuse to mutate the audited EOU.** Produces a report; never edits the target's spec.
3. **Refuse to mutate the captured_workflow.** If audit findings suggest captured_workflow amendment is needed (e.g., priority order is wrong), the report recommends an ECP; it does not author one.
4. **Refuse to promote judgment_maturity directly.** The audit verdict is one piece of evidence; promotion happens via `$eou-promote` per D5.2 gate evidence.
5. **Refuse to write outside the blast_radius allowed_scope** (`foundry/audits/judgment-audits/`, `foundry/runs/audit-judgment/`).

## Constraints

- Counterfactual-swap audit budget is configurable per audit invocation; default 5 swap-tests. Reduce for expensive LLM_assisted EOUs.
- Swap-test runs MUST be isolated to `foundry/runs/audit-judgment/swap-tests/` — never write to production directories under swap conditions.
- For non-deterministic LLM_assisted target EOUs, require ≥2 baseline control runs at original priority to distinguish swap-driven changes from natural variance.
- Audit verdict feeds into judgment_maturity promotion via $eou-promote — the skill suggests the next level (J1→J2, J2→J3, etc.) in the report but does not write the promotion itself.

## Scope Note

**Upstream:** the fourth audit layer per D4.1 (post-ECP-0019). Receives an EOU with `judgment_authorized:true` and its app's captured_workflow.

**Downstream:** writes `foundry/audits/judgment-audits/{target}.judgment-audit.yml`. The report is consumed by `$eou-promote` for judgment_maturity promotion evidence, by `$foundry-audit` for portfolio-level judgment health, and by human reviewers for sophisticated-theater detection that mechanical checks cannot catch (per V2).

**Related:** `$eou-audit` (third audit layer — design); `$eou-validate` (first audit layer — schema); `$foundry-audit` (portfolio audit including judgment-audit aggregation).

**Pipeline:** `EOU at judgment_authorized:true → accumulates value_invocations in run traces → audit-judgment audits invocations and runs counterfactual-swap → judgment-audit report → $eou-promote for judgment_maturity promotion`

**Rule 96 vs Rule 97:** Rule 96 governs **static spec discipline** (specs must cite domain_values in `success_criteria.must_pass`). Rule 97 governs **runtime invocation discipline** (runs must invoke values for contested cases; invocations must respect priority; counterfactual-swap must produce changes). `$eou-audit` enforces Rule 96; `$audit-judgment` enforces Rule 97.
