---
name: eou-diagnose
description: |
  Diagnose an EOU failure using the F-code taxonomy and recommend the smallest-blast-radius repair, producing either a diagnosis (path to $ecp-propose) or a no-change record.
  <example>
  Context: An incident has been filed; owner wants a structured diagnosis before deciding whether to open an ECP.
  user: "$eou-diagnose foundry/incidents/inc-0042.yml"
  assistant: "I'll classify the failure under one or more F-codes, rank repair options by blast radius, and emit either a diagnosis YAML (decision: change) or a no-change record under foundry/audits/incidents/."
  </example>
  <example>
  Context: User wants to diagnose from an audit finding rather than a full incident.
  user: "$eou-diagnose foundry/audits/eou-audits/eou-promote.audit.yml"
  assistant: "I'll diagnose the audit's findings; if evidence is insufficient for a change, I'll write a no-change record explicitly rather than silently doing nothing."
  </example>
argument-hint: INCIDENT_OR_AUDIT_PATH
arguments:
  - target
allowed-tools:
  - Read
  - Write
  - Grep
---

# Diagnose EOU Failure

Diagnose the failure described in `$target` and recommend the minimum repair path.

## Inputs

- `$target` (required) — path to an incident report or audit finding. Accepted paths: `foundry/audits/incidents/{id}.yml`, `foundry/audits/eou-audits/{id}.audit.yml`, or any structured YAML file containing an observable failure symptom.

## Required reading

1. `foundry/failure-taxonomy.yml` — F1–F12 class definitions and repair heuristics
2. `foundry/constitution.yml` — invariants that constrain repair options
3. `schemas/incident.schema.yml` — validate the input incident report against this schema if it is a structured YAML file

## Stop conditions

Halt and request clarification if:
- `$target` does not identify an EOU ID and one cannot be inferred from the content.
- The incident report contains no observable failure symptom — only a conclusion or label.
- `foundry/failure-taxonomy.yml` does not exist — failure classification cannot proceed without it.

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

Every diagnosis produces one of two outcomes:

- **Change warranted** — write the diagnosis report, then use `$ecp-propose` to open an ECP.
- **No change warranted** — write a no-change record to `foundry/audits/incidents/{incident_id}.no-change.yml` with fields: `incident_id`, `eou_id`, `diagnosis_summary`, `decision: no_change`, `rationale`, `reviewed_by`, `reviewed_at`, `reopen_condition`.

A no-change record is not a failure of the diagnosis process. It is evidence that the system reviewed and rejected a change rather than silently ignoring the incident.

Write the diagnosis report to `foundry/audits/incidents/{incident_id}.diagnosis.yml` with the following structure:

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
- Do not invent an `incident_id` — use the one from `$target` or generate from `{eou_id}-{YYYYMMDD}` if absent.
- Confidence ratings (`high/medium/low`) for failure class matches must be grounded in observable signals, not subjective judgment.

## Scope Note

**Upstream:** receives incident reports (`foundry/incidents/`) or audit failures (`foundry/audits/eou-audits/`).

**Downstream:** dual outcome — `decision: change` produces a diagnosis fed to `$ecp-propose`; `decision: no_change` produces a no-change record under `foundry/audits/incidents/`.

**Related:** `$eou-refactor` (sibling — also a path to ECP from audit findings, but produces structural options rather than F-code classification); `$generate-regression-cases` (sibling — converts incidents to durable test memory).

**Pipeline:** `incident | audit failure → eou-diagnose → (change) ecp-propose | (no_change) no-change record`
