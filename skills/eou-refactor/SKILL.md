---
name: eou-refactor
description: "Generate candidate EOU refactor options from an audit or incident. Does not apply changes directly."
argument-hint: EOU_ID_OR_AUDIT_PATH
arguments:
  - target
allowed-tools:
  - Read
  - Write
  - Grep
---

# Refactor EOU

Generate candidate refactor options for `$target`.

Use `foundry/refactoring-patterns.yml` and `foundry/constitution.yml`.

Each option must include:

- target failure
- proposed change
- expected benefit
- risk
- affected files
- tests required
- rollback plan
- arguments against the refactor

Do not apply changes. Produce an ECP if the option is worth pursuing.
