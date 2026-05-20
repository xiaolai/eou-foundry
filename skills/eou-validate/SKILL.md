---
name: eou-validate
description: |
  Validate the structural integrity of Foundry schemas, registry entries, EOU specs, generating-EOU envelopes, and recursive-governance constraints. Produces a validation report; does not repair found violations (that is the job of $eou-specify in repair mode or $eou-refactor).
  <example>
  Context: Owner wants to know if the foundry tree passes structural validation before opening a PR.
  user: "$eou-validate"
  assistant: "I'll run scripts/validate_foundry.py and parse the output into a categorized validation report under foundry/audits/validation/. Failures are listed but not auto-repaired."
  </example>
  <example>
  Context: After a schema change, owner wants to confirm no specs drifted.
  user: "$eou-validate --strict-no-legacy"
  assistant: "I'll run validation with legacy engine copies treated as errors (not warnings). Useful pre-release to catch lingering pre-v0.5.0 layout."
  </example>
allowed-tools:
  - Read
  - Write
  - Grep
  - Bash
---

# Validate Foundry

Validate the structural integrity of the EOU Foundry at `foundry/`.

## Required reading (load in order)

1. `schemas/eou.schema.yml` — the authoritative EOU spec schema
2. `schemas/ecp.schema.yml` — the authoritative ECP schema
3. `foundry/constitution.yml`
4. `foundry/registry.yml`

## Stop conditions

Stop and record a `critical` finding if:
- Any schema file in `schemas/*.schema.yml` is absent — validation cannot proceed without schemas.
- `foundry/` directory does not exist in the working directory.

## Validation checks

Run each check in order. Record every violation — do not stop at first failure.

### 1. Schema presence
Verify all schema files in `schemas/*.schema.yml` exist. If any are absent, record a "schema file absent" critical finding and stop (cannot validate specs without schemas).

### 2. EOU spec completeness
For each spec in `foundry/eous/` and `foundry/meta-eous/`:
- Every field listed in `schemas/eou.schema.yml` `required_top_level` must be present.
- `classification` must include all six facets: `function`, `target_object`, `automation_mode`, `authority_level`, `risk_level`, `lifecycle_stage`.
- All enum values must match schema allowed values (see `valid_*` lists in `schemas/eou.schema.yml`).
- No placeholder strings: reject "target artifact", "What this EOU is meant to do", "Perform bounded operation".

### 3. Registry consistency
- Every spec with `lifecycle_stage: active` or `pilot` must have a registry entry in `foundry/registry.yml`.
- Every registry entry must have a matching spec file in `foundry/eous/` or `foundry/meta-eous/`.
- Flag orphan specs (no registry entry at active/pilot) and unregistered active EOUs.

### 4. Recursive governance constraints
- For each spec: `responsibility.executor` must not equal `responsibility.approver` (self-approval violation).
- For each spec with `function: generate`: `generation_envelope.forbidden_outputs` must include `active_eou`, `approved_eou`, and `constitution_change`.

### 5. Generation safety
For each spec with `function: generate`:
- `generation_envelope.allowed_outputs` must not include `active_eou`, `approved_eou`, or any variant of `constitution_change`.
- `generation_envelope.default_status` must be `candidate`.

## Run deterministic validator

```bash
python3 scripts/validate_foundry.py
```

Include the output in the validation report.

## Output

Write the validation report to `foundry/audits/validation/{YYYYMMDD}.validation.yml`:

```yaml
validation_date:
checks_run:
  - check_name:
    status:  # pass | fail | skipped
    findings:
      - severity:   # critical | high | medium | low
        eou_id:     # or "foundry-wide"
        description:
        required_fix:
summary:
  total_findings:
  by_severity: {critical: N, high: N, medium: N, low: N}
  verdict:  # PASS | FAIL | CONDITIONAL_PASS
```

## Constraints

- This skill validates the entire Foundry at `foundry/`, not a single EOU. Use `$eou-audit` to audit a specific EOU spec.
- Do not modify any spec, schema, registry, or governance file — produce the validation report only.
- Treat missing required fields as failures, not warnings.
- Zero findings for a Foundry with more than 5 specs is statistically improbable — record it as a `low`-severity finding: "No violations found; verify checks ran against all specs."

## Scope Note

**Upstream:** no specific input — runs against the whole `foundry/` tree. Typically invoked before opening a PR or release.

**Downstream:** produces a validation report under `foundry/audits/validation/`. Failures may seed `$eou-diagnose` (if a structural failure traces to an EOU) or `$eou-refactor`.

**Related:** `$eou-audit` (sibling — judgment-heavy audit; this skill is mechanical/structural); `$foundry-audit` (sibling — system-wide, includes vocabulary and governance drift).

**Pipeline:** `pre-release | pre-PR → eou-validate → (failures) eou-diagnose | eou-refactor`
