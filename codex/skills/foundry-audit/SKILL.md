---
name: foundry-audit
description: Audit the EOU Foundry itself for schema drift, self-approval risk, generation overreach, weak validators, and missing governance evidence.
---

# Foundry Audit

Audit the whole Foundry. Read all governance files first, then execute each check category in order.

## Required reading

- `foundry/constitution.yml`
- `foundry/registry.yml`
- `foundry/governance.yml`
- `schemas/*.schema.yml`
- `foundry/eous/*.yml`
- `foundry/meta-eous/*.yml`
- `foundry/self-evolution/`

## Check categories

### 1. Faceted classification completeness
Every EOU spec must declare all six facet fields: `function`, `target_object`, `automation_mode`, `authority_level`, `risk_level`, `lifecycle_stage`. Flag any spec with missing or placeholder values.

### 2. Generating EOU envelope safety
For each EOU with `function: generate`: verify `generation_envelope.forbidden_outputs` contains `active_eou`, `approved_eou`, and `constitution_change`. Flag any envelope that permits outputs outside its stated scope.

### 3. Self-approval risk
For each EOU: verify `responsibility.executor` ≠ `responsibility.approver`. A single role cannot both produce and approve outputs. Flag any EOU where this boundary is absent or ambiguous.

### 4. Registry / spec consistency
Every EOU in `registry.yml` with `lifecycle_stage: active` or `pilot` must have a corresponding spec file in `foundry/eous/` or `foundry/meta-eous/`. Every spec file at those stages must be registered. Flag orphan specs and unregistered active EOUs.

### 5. Schema drift
Load each schema from `schemas/*.schema.yml`. For each active or pilot EOU spec, validate it against the schema. Flag missing required fields and type mismatches.

### 6. ECP discipline
Any EOU spec that changed `authority_level`, `blast_radius.forbidden_scope`, or removed a validator since its last version must have a corresponding approved ECP. Check `foundry/self-evolution/ecp/` for evidence. Flag spec changes without an approved ECP.

### 7. Regression memory
For each active EOU: at least one regression fixture must exist in `foundry/self-evolution/regression/cases/`. Flag EOUs with zero regression coverage.

### 8. Authority and blast radius
For each EOU: `authority_level` must match `blast_radius.allowed_scope`. An EOU with `authority_level: write_candidate` must not have `allowed_scope` containing active governance files. Flag mismatches.

### 9. High-risk escalation
For each EOU with `risk_level: high` or `critical`: `escalation.require_human_when` must be non-empty and `responsibility.approver` must be a named human role (not "Claude" or "script"). Flag violations.

### 10. Operational value
For each EOU: `purpose.statement` must name a concrete failure prevented or decision improved — not a process description. Flag EOUs with purpose statements that describe what the EOU does without naming what failure it prevents.

## Output

Write the audit report to `foundry/audits/foundry-audits/{YYYYMMDD}.foundry-audit.yml`:

```yaml
audit_date:
findings:
  - check:         # check category name
    severity:      # critical | high | medium | low
    eou_id:        # or "foundry-wide"
    description:   # what was found
    required_fix:  # specific change required
summary:
  total_findings:
  by_severity:
    critical:
    high:
    medium:
    low:
  pass_rate:       # checks passed / total checks
  verdict:         # PASS | FAIL | CONDITIONAL_PASS
```
