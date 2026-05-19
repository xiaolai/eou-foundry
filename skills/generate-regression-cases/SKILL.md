---
name: generate-regression-cases
description: "Convert incident reports and audit failures into candidate regression cases that prevent re-occurrence. Cases are written as candidates; activation requires human owner approval."
argument-hint: INCIDENT_PATH_OR_GLOB
arguments:
  - source
allowed-tools:
  - Read
  - Write
  - Grep
---

# Generate Regression Cases

Convert `$source` (one or more incident reports or audit failures) into candidate regression cases.

## Inputs

- `$source` (required) — path to one or more incident reports or audit failure files. Accepts a direct file path or a glob (e.g., `foundry/audits/incidents/*.yml`). Every matched file must contain at least one observable failure symptom.

## Required reading

1. `foundry/failure-taxonomy.yml` — classify each failure by F-code
2. `foundry/constitution.yml` — invariants that constrain what counts as a valid regression case
3. `schemas/incident.schema.yml` — validate structured YAML incident files against this schema
4. `schemas/regression-case.schema.yml` — the schema for the output regression case files

## Stop conditions

Halt and report before generating cases if:
- `$source` resolves to no readable files.
- No observable failure symptom can be extracted from any source file — labels and conclusions without symptoms are not sufficient.
- `schemas/regression-case.schema.yml` does not exist — cannot validate output structure.

## Procedure

1. Load `$source`. If it is a glob, read all matching files.
2. For each incident or audit failure, extract the observable failure symptom.
3. Classify the failure using `foundry/failure-taxonomy.yml` (F1–F12).
4. Derive the regression case: the minimal input that reproducibly triggers the failure.
5. Construct the fixture path: `foundry/self-evolution/regression/fixtures/{case_id}/`.
6. Check `foundry/self-evolution/regression/cases/` for existing cases that cover this failure — skip if a duplicate exists; record the duplicate case ID instead.
7. For each new case, write the regression case file with all required fields.
8. Set `activation_status: candidate` on all generated cases — never `active`.

## Required fields per case (per `schemas/regression-case.schema.yml`)

```yaml
id:                   # regression-{eou_id}-{failure_class}-{YYYYMMDD}
source_incident_id:   # incident or audit ID this case was derived from
failure_class:        # F1-F12 code
eou_id:               # EOU that exhibited the failure
fixture_path:         # foundry/self-evolution/regression/fixtures/{case_id}/
failure_shape_assertion:  # observable output that indicates the failure is occurring (non-empty)
activation_status:    # candidate — never active without human approval
```

## Output

Write each case to `foundry/self-evolution/regression/cases/{case_id}.regression.yml`.
Create the fixture directory at `foundry/self-evolution/regression/fixtures/{case_id}/`.
Record the run in `runs/{run_id}/trace.yml`.

## Constraints

- Do not set `activation_status: active`. Cases are candidates until the human owner promotes them.
- Do not generate cases without a concrete source incident or audit failure.
- Each case must include at least one `failure_shape_assertion` — what observable output signals the failure is occurring. Cases asserting only pass are invalid.
- If a duplicate case exists for this failure, record the duplicate ID and skip generation.
