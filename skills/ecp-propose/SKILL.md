---
name: ecp-propose
description: "Create a formal EOU Change Proposal from a diagnosed failure or refactor option."
argument-hint: DIAGNOSIS_OR_REFACTOR_PATH
arguments:
  - target
allowed-tools:
  - Read
  - Write
  - Grep
---

# Propose ECP

Create an EOU Change Proposal from `$target`.

Read `schemas/ecp.schema.yml` and `foundry/constitution.yml`.

The ECP must include observed problem, failure class, proposed change, expected benefit, risks, required tests, simulation status, approval status, and rollback considerations.

Do not apply the ECP.
