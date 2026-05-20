---
name: 93-recursive-governance
description: Allow the Foundry to inspect and improve its own EOUs only through bounded governance (observe → diagnose → propose → simulate → regression → audit → human approval → implement). Forbid self-edit + self-approve.
---

# Recursive Governance Rule

**Route every structural Foundry change through the full governance pipeline — no shortcuts, no step skipped.** The pipeline is the only thing that prevents the Foundry from drifting away from its own constitution; collapsing it (observe→edit, audit→implement, propose→implement-without-approval) turns recursive self-improvement into recursive self-corruption.

The Foundry may recursively inspect and improve its own EOUs, but only through bounded governance.

## Required change pipeline

Every structural change to an EOU spec, schema, constitution, or governance rule must pass through this chain in order:

```text
observe → diagnose → propose (ECP) → simulate → regression test → audit → human approval → implement
```

No step may be skipped. Each step produces a traceable artifact:

| Step | Function | Artifact |
|------|---------|---------|
| observe | — | incident report (`foundry/audits/incidents/{id}.yml`) for operational anomalies; audit finding (`foundry/audits/eou-audits/{id}.audit.yml`) for inspection results |
| diagnose | `diagnose` | `foundry/audits/incidents/{id}.diagnosis.yml` or `foundry/audits/incidents/{id}.no-change.yml` |
| propose | `propose` | `foundry/self-evolution/ecp/proposed/{eou}-ecp-{YYYYMMDD}.yml` |
| simulate | — | ECP `simulation` field populated |
| regression test | — | `foundry/self-evolution/regression/cases/{id}.regression.yml` |
| audit | `audit` | `foundry/audits/eou-audits/{eou_id}.audit.yml` |
| human approval | — | ECP `approval.status: approved`, `approval.approver` set to named human identity |
| implement | `implement` | ECP moved to `foundry/self-evolution/ecp/implemented/`; EOU spec updated; registry updated |

## Trace evidence (ECP-0007 schema, ECP-0014 enforcement)

Active and higher-stage EOUs produce run traces. The constitution's
"every active EOU must produce trace or declare why trace is impossible"
invariant is enforced by `scripts/validate_foundry.py` from v0.6.0
onward (hard-cut, no warning phase). The validator checks every EOU at
`lifecycle_stage` in `{active, monitored, stable}` and requires either a
non-empty `outputs.trace` listing a path under `runs/`, OR a non-expired
`foundry/audits/no-trace/{eou_id}.yml` justification with a named human
reviewer. EOUs that satisfy neither hard-fail validation.

The invariant is enforced through two artifacts:

**Run trace.** Per `schemas/run-trace.schema.yml`, stored at
`foundry/runs/{eou_id}/{run_id}.yml`. Records what ran, when, with what
inputs, what context was loaded, which steps completed, what warnings
arose, what outputs were produced, what validation gates ran, and who
approved (if approval was needed). Use `scripts/runs.py`'s `record_run()`
helper from EOU implementations to emit compliant traces.

**No-trace-justification.** Per `schemas/no-trace-justification.schema.yml`,
stored at `foundry/audits/no-trace/{eou_id}.yml`. Used when traces are
genuinely impossible (e.g., delegated execution that can't be
instrumented). Requires `impossibility_reason`, `reviewed_by` (named
human, NOT a TODO placeholder — the validator rejects `reviewed_by`
matching `^TODO`), `reviewed_at`, and `expires_at` (typically six
months). Expired justifications fail validation; the EOU owner must
re-review and renew or accept demotion.

"We haven't gotten around to it" is **not** an impossibility reason.
The no-trace escape hatch is for structural impossibility, not
procedural laziness.

## Forbidden shortcuts

```text
observe → edit EOU spec directly
observe → edit itself → approve itself
audit → implement (skipping ECP and human approval)
```

No EOU may be the sole judge of changes to itself. The EOU that proposes a change (`function: propose`) and the EOU that audits it (`function: audit`) must have different `responsibility.executor` values.

## When this rule applies

Any change to:

- An EOU spec in `foundry/eous/` or `foundry/meta-eous/`
- A schema in `schemas/`
- `foundry/constitution.yml`, `foundry/governance.yml`, `foundry/registry.yml`
- A meta-EOU in `engine/meta-eous/`

## Violation indicators

A violation of this rule is present when any of the following is observed:

| Signal | Severity | Required action |
|--------|----------|-----------------|
| An EOU spec in `foundry/eous/` or `foundry/meta-eous/` was modified without a corresponding `diagnosis.yml` file in `foundry/audits/incidents/` | high | Revert spec change; open an incident; restart from observe step |
| A spec change appears in `foundry/self-evolution/ecp/implemented/` without a prior `{eou_id}.audit.yml` in `foundry/audits/eou-audits/` | critical | Treat as unauthorized deployment; revert immediately; flag for human review |
| An ECP's `approval.status` is `implemented` but `approval.approver` is blank or a role label | critical | Invalidate ECP; require named human re-approval before re-deploying |
| A spec was modified and `versioning.changelog` was not updated | medium | Update `versioning.changelog` before next promotion; block promotion until resolved |
| The same `responsibility.executor` appears in both the proposing EOU and the auditing EOU for a given change | high | Reassign auditing EOU to a different executor; re-run audit under non-colliding responsibility |
