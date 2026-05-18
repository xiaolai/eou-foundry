# EOU Foundry Plugin Changelog

## 0.1.0 — Initial plugin release (bootstrap)

> **Bootstrap exception.** This is the first published version of the
> plugin. There is no prior version to be governed by ECP, so this
> release was not itself proposed through an ECP — it cannot have been.
> All subsequent changes (≥ 0.2.0) **must** be reviewed through a
> proper ECP cycle per `rules/92-ecp.md` and `templates/governance.yml.template`.

This release extracts the EOU Foundry from the seeded book-workshop
monolith (formerly at `/Users/joker/EOU-Foundry/`) and republishes it
as an installable plugin. Architecturally the change separates:

- **The engine** (this plugin) — schemas, governance rules, validators,
  audit skills, ECP infrastructure, engine theory docs.
- **An instance** (the consuming project's `foundry/` directory) —
  constitution, registry, EOUs, incidents, audits, run traces,
  application-level ECPs.

What ships:

- `schemas/` — 8 canonical schemas (eou, ecp, constitution, registry-entry,
  regression-case, incident, audit-report, run-trace).
- `engine/` — EOU contract, foundry V2 design, EOU system theory.
- `skills/` — 9 Foundry skills: `/eou-foundry:{eou-specify, eou-audit,
  eou-diagnose, eou-refactor, eou-promote, foundry-audit, ecp-propose,
  generate-eou-candidates, audit-candidate-eou-set}`.
- `rules/` — 7 Foundry-level rules covering EOU schema, constitution
  precondition, ECP requirement, recursive governance, no-self-approval,
  generating-EOU constraints.
- `commands/init.md` — `/eou-foundry:init` scaffolds a new application
  directory with a fresh `foundry/`.
- `templates/` — universals (maturity-model, failure-taxonomy,
  refactoring-patterns, runtime-contract), instance starters
  (constitution, governance, registry), 10 meta-EOU specs, EOU and
  generating-EOU card templates.
- `scripts/` — `validate_foundry.py`, `validate_recursive_case.py`,
  `_common.py` helpers, `clean_generated.py`.
- `dev-docs/` — 5 architecture history docs (11, 13, 14, 15, 16).

## Pre-release history (informational, not version-tagged)

Before the plugin extraction, the Foundry lived inside a monolithic
repo that also contained the book-workshop application. That tree's
`foundry/self-evolution/changelog.md` named its first internal version
"0.2.0" as a bootstrap exception. That history is consumed by this
plugin's 0.1.0 release — the new bootstrap exception above replaces it.
