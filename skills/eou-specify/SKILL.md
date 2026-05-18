---
name: eou-specify
description: "Convert an approved candidate into a formal EOU spec using Foundry V2 faceted classification and governance constraints."
argument-hint: CANDIDATE_PATH_OR_ID
arguments:
  - candidate
allowed-tools:
  - Read
  - Write
  - Grep
---

# Specify EOU

Create or repair a formal EOU spec from `$candidate`.

Read `schemas/eou.schema.yml`, `foundry/constitution.yml`, and `foundry/governance.yml` first.

The spec must include faceted classification, operating hypothesis, context manifest, stop conditions, validation, failure modes, escalation, responsibility, blast radius, and versioning.

Do not mark the EOU active unless there is explicit audit and approval evidence.
