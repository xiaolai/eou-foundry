# EOU Foundry V2

EOU Foundry V2 is a recursive governance system for designing, supervising, and improving Executable Operating Units.

## Core idea

An EOU is an operational hypothesis:

```text
Given inputs X,
context Y,
procedure Z,
and validation tests T,
this unit can produce output O
within acceptable risk R.
```

The Foundry manages those hypotheses through trace, audit, diagnosis, ECPs, regression tests, and human-owned approval.

## Faceted classification

EOUs are not classified by one vague type. They use facets:

```yaml
classification:
  function: execute | audit | generate | decide | govern | validate | refactor
  target_object: string
  automation_mode: deterministic | LLM_assisted | human_executed | hybrid
  authority_level: suggest_only | draft_only | write_candidate | write_inactive | mutate_active | approve | publish
  risk_level: low | medium | high | critical
  lifecycle_stage: candidate | draft | simulated | pilot | active | monitored | stable | deprecated | retired
```

This prevents category errors such as treating a generating unit as if it had approval authority.

## Generating EOUs

Generating EOUs are proposal-producing units. They may generate candidate EOUs, candidate tests, candidate refactors, candidate schemas, or candidate ECPs.

They may not activate, approve, publish, weaken validators, mutate active governance, or rewrite the constitution.

The canonical path is:

```text
generate candidates
→ argue against them
→ rank them
→ keep minimal subset
→ audit candidate set
→ simulate
→ approve
→ activate
```

## Three audits

Every serious EOU system needs three audit layers:

```text
Output audit — is the artifact valid?
Run audit    — was the EOU executed correctly?
EOU audit    — is the EOU itself well designed?
```

## Recursive self-evolution

The Foundry may improve itself, but only through explicit, testable, reversible, owner-approved change.

The Foundry must never optimize for appearing correct. It must become better at finding where it is wrong.
