---
name: foundry-audit
description: "Audit the EOU Foundry itself for schema drift, self-approval risk, generation overreach, weak validators, and missing governance evidence."
allowed-tools:
  - Read
  - Write
  - Grep
---

# Foundry Audit

Audit the whole Foundry.

Read:

- `foundry/constitution.yml`
- `foundry/registry.yml`
- `schemas/*.schema.yml`
- `foundry/eous/*.yml`
- `foundry/meta-eous/*.yml`
- `foundry/self-evolution/`

Check:

- faceted classification completeness
- generating EOU envelopes
- no self-approval
- registry/card consistency
- schema drift
- ECP discipline
- regression memory
- authority and blast radius
- high-risk escalation
- operational-value discipline

Write a concrete audit report with required fixes.
