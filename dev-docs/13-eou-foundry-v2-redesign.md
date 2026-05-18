# EOU Foundry V2 Redesign

This document is the canonical design note for the recursive EOU Foundry after the independent architectural review of generating EOUs.

## Core correction

The previous design treated `generating` as a single EOU type parallel to deterministic, judgment, execution, audit, and decision units. That was too crude.

The canonical model now uses **faceted classification**:

```yaml
classification:
  function: execute | audit | generate | decide | govern | validate | refactor
  target_object: string
  automation_mode: deterministic | LLM_assisted | human_executed | hybrid
  authority_level: suggest_only | draft_only | write_candidate | write_inactive | mutate_active | approve | publish
  risk_level: low | medium | high | critical
  lifecycle_stage: candidate | draft | simulated | pilot | active | monitored | stable | deprecated | retired
```

This separates what the unit does from how it runs, how much authority it has, how risky it is, and where it sits in its lifecycle.

## New core principle

An EOU is an operational hypothesis:

```text
Given inputs X,
context Y,
procedure Z,
and validation tests T,
this unit can produce output O
within acceptable risk R.
```

The Foundry manages those hypotheses.

## Generating EOUs

A generating EOU produces **candidates**, not authority.

Examples:

```text
generate-eou-candidates
generate-regression-cases
generate-eou-refactor-options
propose-ecp
```

A generating EOU may create:

```text
candidate EOU specs
candidate regression cases
candidate refactor options
candidate ECPs
candidate schemas
candidate protocols
```

It may not create:

```text
active EOUs
approved EOUs
production schemas
human approval records
constitution changes
weakened validators
published output
```

## Generating EOU constraints

Every generating EOU must declare:

```yaml
generation_envelope:
  allowed_outputs: []
  forbidden_outputs: []
  max_candidates: 7
  default_status: candidate
  required_for_each_candidate: []

generation_budget:
  max_candidates: 7
  max_new_schemas: 2
  max_new_validators: 3
  max_open_questions: 10
  must_rank_candidates: true
  must_select_minimal_set: true

registry_diff:
  required: true
  questions: []

minimality_test:
  questions: []

operational_value_test:
  required_answer:
    - prevents_failure
    - improves_decision
    - exposes_hidden_judgment
    - improves_traceability

counter_generation:
  required: true
  requires_for_each_candidate:
    - arguments_against
    - minimality_result
```

## Candidate set audit

Generated EOU candidates must be audited as a set, not only one by one. A candidate set can fail even if each candidate looks plausible.

The audit asks:

```text
Does the set overproduce?
Does it duplicate existing EOUs?
Does each unit have a distinct success criterion?
Does it include validation and human approval where needed?
Are high-risk decisions separated from generation?
Does the set include rejected candidates and a minimal subset?
```

## Minimality rule

Before accepting a generated EOU, ask whether the need can be satisfied by:

```text
a rule
a schema field
a validator
a regression case
a stop condition
a checklist
a human approval gate
```

A new EOU is not progress by itself. The Foundry rewards fewer, sharper, more inspectable EOUs.

## Recursive self-improvement boundary

The Foundry can recursively improve itself, but only through governed change:

```text
observe failure
→ diagnose failure
→ generate candidate refactor / ECP
→ audit candidate
→ simulate
→ regression test
→ human approval
→ staged deployment
→ registry update
```

It cannot silently approve or deploy its own changes.

## Canonical files added

```text
schemas/eou.schema.yml
schemas/registry-entry.schema.yml
schemas/run-trace.schema.yml
schemas/audit-report.schema.yml
schemas/incident.schema.yml
schemas/ecp.schema.yml
schemas/regression-case.schema.yml
schemas/constitution.schema.yml

foundry/constitution.yml
foundry/registry.yml
foundry/maturity-model.yml
foundry/failure-taxonomy.yml
foundry/refactoring-patterns.yml
foundry/governance.yml
foundry/runtime-contract.yml

foundry/eous/
foundry/meta-eous/
foundry/self-evolution/
foundry/incidents/
foundry/runs/
foundry/audits/
```

## Canonical anti-patterns

Reject:

```text
generate → activate
self-approval
schema drift
process inflation
validator weakening without ECP
approval by the same unit that generated the output
new EOUs without evidence of need
high pass rate as a proxy for quality
```

Accept:

```text
generate → argue against → rank → minimal subset → audit → simulate → approve → activate
```

The Foundry is successful only if it becomes better at detecting and correcting its own false confidence.
