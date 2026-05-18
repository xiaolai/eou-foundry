---
name: generate-eou-candidates
description: "Generate a minimal, ranked candidate EOU set from a messy workflow using Foundry V2 constraints. Candidates are proposal-only and cannot be activated."
argument-hint: WORKFLOW_DESCRIPTION_OR_FILE
arguments:
  - workflow
allowed-tools:
  - Read
  - Write
  - Grep
---

# Generate EOU Candidates

Generate candidate EOUs from `$workflow`.

## Required reading

1. `foundry/constitution.yml`
2. `foundry/governance.yml`
3. `foundry/failure-taxonomy.yml`
4. `foundry/meta-eous/generate-eou-candidates.yml`
5. `schemas/eou.schema.yml`

## Output rule

Write candidates only. Do not activate, approve, publish, mutate the registry, weaken validators, or change the constitution.

## Required output structure

The candidate set must include:

- source workflow
- generated candidates
- rejected candidates
- recommended minimal set
- open questions
- registry-diff notes
- operational-value notes

Each kept candidate must include:

- purpose
- non-goal
- distinct success criterion
- authority level
- risk level
- owner requirement
- activation requirements
- operational value
- arguments against creation
- minimality result

## Hard rule

Prefer fewer, sharper EOUs. If a need can be met by a rule, schema field, validator, regression case, stop condition, or human checklist, recommend that instead of a new EOU.
