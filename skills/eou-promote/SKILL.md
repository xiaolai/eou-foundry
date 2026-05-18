---
name: eou-promote
description: "Evaluate whether an EOU should be promoted, deprecated, or retired based on evidence, maturity model, audits, and owner approval."
argument-hint: EOU_ID
arguments:
  - eou_id
allowed-tools:
  - Read
  - Write
  - Grep
---

# Promote or Retire EOU

Evaluate `$eou_id` against `foundry/maturity-model.yml`, `foundry/registry.yml`, audits, traces, and regression history.

Do not promote if trace, owner, validation, or approval evidence is missing.

Output recommendation only unless explicit human approval is present.
