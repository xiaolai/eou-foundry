---
name: eou-diagnose
description: Diagnose EOU failures using the Foundry failure taxonomy and recommend the smallest repair path.
---

# Diagnose EOU Failure

Diagnose the failure described in `$target` and recommend the minimum repair path.

## Required reading

1. `foundry/failure-taxonomy.yml` — F1–F12 class definitions and repair heuristics
2. `foundry/constitution.yml` — invariants that constrain repair options

## Procedure

1. Read `$target` (incident report or audit finding) and extract the observable failure symptom.
2. For each symptom, classify it against the F1–F12 taxonomy. One symptom may match multiple classes — list all that apply, ranked by confidence.
3. For each classified failure, identify the minimum repair action using this precedence (smallest blast radius first):
   - schema field addition or constraint
   - validator strengthening
   - stop condition
   - regression case
   - context manifest repair
   - ECP (structural EOU change)
   - human approval gate
   - EOU split / merge / retire
4. Rule out prompt-only explanations: if the failure recurs despite correct inputs, classify as structural (F3–F12), not F1 (prompt ambiguity).
5. Write the diagnosis report.

## Output

Write to `foundry/audits/incidents/{incident_id}.diagnosis.yml` with the following structure:

```yaml
incident_id:      # from $target or generated
eou_id:           # EOU under diagnosis
failure_classes:  # list of F-codes with confidence (high/medium/low)
symptoms:         # observable signals that led to each classification
repair_options:   # ordered list, smallest blast radius first
  - repair_type:  # schema_field | validator | stop_condition | regression_case | context_manifest | ecp | human_gate | eou_lifecycle
    description:  # one sentence — what changes
    blast_radius: # narrow | medium | wide
    requires_ecp: # true | false
recommended:      # index into repair_options of the recommended minimum fix
rationale:        # why that fix and not the next one up
```

## Constraints

- Do not treat every failure as a prompt problem (F1). Require observable evidence for F1 classification.
- Do not recommend retirement without evidence that the EOU's operational value is gone.
- Do not recommend ECP when a stop condition or validator would suffice.
