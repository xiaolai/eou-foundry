---
name: eou-audit
description: "Audit EOU specs for Foundry V2 faceted classification, authority limits, schemas, validation, failure modes, trace, blast radius, and responsibility ownership."
argument-hint: EOU_ID_OR_PATH
arguments:
  - target
allowed-tools:
  - Read
  - Write
  - Grep
  - Bash
---

# EOU Audit

Audit an EOU spec at `$target`, or all specs in `foundry/eous/` and `foundry/meta-eous/` when no target is given.

## Inputs

- `$target` (optional) — EOU ID resolved to `foundry/eous/{id}.yml` or `foundry/meta-eous/{id}.yml`, or a direct file path. When omitted, audits all specs in both directories.

## Required reading

1. `foundry/constitution.yml`
2. `foundry/governance.yml`
3. `foundry/failure-taxonomy.yml`
4. `schemas/eou.schema.yml`
5. Target EOU spec(s)

## Stop conditions

Stop and record a `critical` finding before proceeding if:
- `schemas/eou.schema.yml` does not exist — cannot validate spec completeness.
- `$target` is provided but does not resolve to any spec file in `foundry/eous/` or `foundry/meta-eous/`.

## Procedure

### Step 1 — Deterministic validation

```bash
python3 scripts/validate_foundry.py
```

Record any schema errors as `critical` findings before proceeding.

### Step 2 — Faceted classification (per EOU)

Verify all six classification facets are present and use schema-allowed values:

| Facet | Allowed values |
|-------|----------------|
| `function` | `generate \| specify \| validate \| diagnose \| promote \| refactor \| audit \| propose` |
| `automation_mode` | `deterministic \| LLM_assisted \| hybrid \| human_executed` |
| `authority_level` | `suggest_only \| draft_only \| write_candidate \| write_inactive \| mutate_active \| approve \| publish` |
| `risk_level` | `low \| medium \| high \| critical` |
| `lifecycle_stage` | `candidate \| draft \| simulated \| pilot \| active \| monitored \| stable \| deprecated \| retired` |

Finding: any missing or out-of-vocabulary value → severity `high`.

### Step 3 — Authority and blast-radius appropriateness

- `mutate_active` or higher requires `risk_level: high` or `critical`.
- `blast_radius.forbidden_scope` must be declared for `mutate_active` or higher.
- `authority_level` must not exceed what the EOU's `function` requires.

Finding: mismatched authority/risk → severity `high`.

### Step 4 — Required structural fields

Each EOU must declare: `purpose` (with `non_goals`), `inputs` (with `forbidden_assumptions`), `context_manifest`, `execution` (with `stop_conditions`), `outputs`, `success_criteria`, `failure_modes` (with `repair_actions`), `escalation`, `responsibility`, `versioning`, `blast_radius`.

Finding: any missing field → severity `medium`. Placeholder text (e.g. "Perform bounded operation", "target artifact") → severity `high`.

### Step 5 — Separation of concerns

- `deterministic` work (scripts, schema checks) must not be mixed with `LLM_assisted` judgment steps in a single EOU step.
- Self-approval: `responsibility.executor` must not equal `responsibility.approver`.

Finding: violation → severity `high`.

### Step 6 — Trace preservation

- `outputs` must include `trace: foundry/runs/{eou_id}/{run_id}.yml`.
- `execution.steps` must be specific enough to reconstruct what ran.

Finding: absent trace output → severity `medium`.

### Step 7 — Generating-EOU additional checks

For every EOU with `function: generate`:

- `generation_envelope.forbidden_outputs` must include `active_eou`, `approved_eou`, `constitution_change`.
- `generation_envelope.default_status` must be `candidate`.
- `generation_budget.max_candidates` must be declared.
- `minimality_test` and `operational_value_test` must be declared.
- `counter_generation.required` must be `true`.

Finding: any violation → severity `high`.

### Step 8 — Human-approval escalation

- Any EOU that affects publication, finance, health, legal, safety, or constitution must declare `escalation.require_human_when`.
- `responsibility.cannot_delegate` must list at least one item for EOUs with `authority_level: mutate_active` or higher.

Finding: absent escalation on high-stakes EOU → severity `high`.

## Output

Write one file per audited EOU to `foundry/audits/eou-audits/{eou_id}.audit.yml`:

```yaml
audit_date:
eou_id:
eou_version:
checks:
  - check_name:        # faceted_classification | authority_blast_radius | structural_fields | separation_of_concerns | trace | generating_eou | escalation
    status:            # pass | fail | skip
    findings:
      - severity:      # critical | high | medium | low
        field:         # YAML field path where the violation occurs
        description:
        required_fix:
summary:
  total_findings:
  by_severity: {critical: 0, high: 0, medium: 0, low: 0}
  verdict:             # PASS | FAIL | CONDITIONAL_PASS
```

When auditing the whole `foundry/` directory, write one file per EOU. Do not merge findings across specs.

## Constraints

- Do not modify any EOU spec — produce the audit report only.
- Treat missing required fields as failures, not warnings.
- Run `validate_foundry.py` before manual checks — its output is authoritative for schema errors.
