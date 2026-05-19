# EOU Foundry Plugin Changelog

## 0.5.1 — Validator catches up to rules (ECP-0004)

Bug-fix release. An external two-pass architecture audit found that the
plugin's rules declared hard constraints that the validator never
enforced, that the v0.5.0 release shipped documented features no code
read, and that the ECP schema/rule/validator disagreed on approval
field names. This release makes the validator enforce what the rules
say is enforced.

What changed:

- `scripts/validate_foundry.py`:
  - Rule 94 enforcement: `responsibility.executor` cannot equal
    `responsibility.approver`. This was declared as a "hard schema
    constraint" in rule 94 line 12 but never checked.
  - Rule 91 enforcement: `responsibility.approver` cannot be a role
    label (e.g. "human owner") for EOUs at active/monitored/stable
    lifecycle stages or with approve/publish authority.
  - Constitutional owner: `application.owner` cannot be empty, missing,
    a TODO marker, or a role label when any EOU is registered as active.
  - Constitution merge weakening protection extended from list fields
    (invariants/forbidden/generation_invariants) to `change_rules`
    (dict; engine keys cannot be dropped or weakened) and `purpose`
    (cannot be emptied) and `optimize_for`/`do_not_optimize_for_alone`.
  - Registry classification fields are now enum-checked against the
    same `VALID_*` sets used for EOU specs, and the registry's
    classification must match the loaded spec exactly.
  - New `validate_incidents()`: walks `foundry/incidents/*.yml` and
    checks them against `incident.schema.yml` required fields.
  - New `validate_engine_artifacts()`: defensive check that the plugin's
    own `engine/*.yml` artifacts are well-formed and contain expected
    top-level keys. Catches an ecp-0001-class failure upstream.
  - New `validate_overrides()`: implements the `foundry/overrides/`
    feature documented in v0.5.0. Per-file engine overrides may add or
    refine values but cannot null out engine keys.
  - `validate_ecps()` now walks both `foundry/self-evolution/ecp/` and
    `foundry/self-evolution/upstream/`. ECPs in approved/implemented
    status require `approval.rollback_considerations` per rule 92.
    Accepts both `approval.approver` and legacy `approval.approved_by`
    (deprecation warning on legacy).
  - Candidate-set artifacts (rule 95) under `ecp/proposed/` matching
    `*-candidates-*.yml` are now skipped by ECP validation; they have
    their own schema and were silently failing.

- `schemas/ecp.schema.yml`: bumped to `ecp.schema.v3`. Documents
  `approval.approver` and `approval.rollback_considerations` as
  required; documents `approval.approved_by` as a deprecated alias.

- `engine/eou-contract.md`: dropped the pre-split
  `applications/book-workshop/...` path prefix from the path
  conventions section. Apps declare their own placeholder roots.

Migration notes:

- Apps with EOUs at active lifecycle and a role-label approver
  (`"human owner"`, etc.) will fail validation. Replace with a named
  human identity in `responsibility.approver`.
- Apps whose `application.owner` is still `"TODO ..."` will fail
  validation once any EOU is registered active. Set the owner first.
- Implemented or approved ECPs filed before this release need
  `approval.rollback_considerations` added. Brief revert plan suffices.
- Registries with `function: execute` (or other invalid enum values)
  will fail; replace with a valid `VALID_FUNCTIONS` entry that matches
  the spec.
- The previously documented `foundry/overrides/` directory now works.

Tracking:

- ECP: `book-workshop/foundry/self-evolution/upstream/landed/ecp-0004-validator-and-schema-alignment-from-audit-roundtable.yml`
- Audit source: post-v0.5.0 architecture audit roundtable (Claude Opus + Codex GPT-5.5, adversarial composition)

## 0.5.0 — Engine as reference, not copy (ECP-0003)

**Breaking change.** Applications consuming this plugin no longer hold
local copies of engine artifacts; they reference them from the plugin.
This fixes the layering violation where every scaffolded app's
`foundry/` tree contained snapshots of plugin engine state at init time.

What moved:

- `templates/{failure-taxonomy,maturity-model,refactoring-patterns,runtime-contract,governance}.yml.template`
  → `engine/{failure-taxonomy,maturity-model,refactoring-patterns,runtime-contract,governance}.yml`
  (no `.template` suffix; these are now canonical engine files).
- `templates/meta-eous/` → `engine/meta-eous/`.
- New file: `engine/constitution-defaults.yml` extracted from the body
  of `templates/constitution.yml.template`.

What changed:

- `templates/constitution.yml.template` shrunk to a small preamble that
  uses `inherits_from: eou-foundry@>=0.5.0` to inherit engine defaults.
- `scripts/init_app.sh` no longer copies engine artifacts into the new
  app. It scaffolds only `constitution.yml` and `registry.yml`, plus
  empty runtime dirs. Adds `foundry/overrides/` for app-specific engine
  overrides; adds `foundry/self-evolution/upstream/landed/` for merged
  upstream ECPs.
- `scripts/validate_foundry.py`:
  - Reads engine artifacts and meta-EOUs from the plugin's `engine/`
    directory.
  - Supports `inherits_from` on `foundry/constitution.yml`; merges
    engine defaults with the app constitution, refusing any merge that
    weakens engine invariants.
  - Emits deprecation warnings (not errors) for legacy local copies in
    consuming applications. v0.5.x is the migration window; v1.0.0 will
    reject legacy local copies.
- `schemas/constitution.schema.yml` bumped to v3; documents
  `inherits_from`.
- `rules/91-foundry-constitution.md` documents the inherits_from
  convention and the engine-vs-app split.
- `dev-docs/historical/` added; receives pre-split engineering records
  (12 and 12a) that describe the foundry engine, not workshop content.

What apps need to do:

1. Pull plugin v0.5.0.
2. Run `python3 $(claude plugin path eou-foundry@xiaolai)/scripts/validate_foundry.py`
   from the app root. Deprecation warnings list each legacy local copy.
3. Delete the legacy local copies named in the warnings: `foundry/failure-taxonomy.yml`,
   `foundry/maturity-model.yml`, `foundry/refactoring-patterns.yml`,
   `foundry/runtime-contract.yml`, `foundry/governance.yml`, and the
   contents of `foundry/meta-eous/` if it has no app-specific divergence.
4. Replace the full-body `foundry/constitution.yml` with an `inherits_from`
   reference plus app-specific declarations. The new
   `templates/constitution.yml.template` is the reference shape.
5. If the app had legitimate engine-artifact customizations, move them to
   `foundry/overrides/<file>.yml`. The validator merges overrides over
   engine defaults.

Tracking incidents and ECP:

- `book-workshop/foundry/incidents/inc-0012-foundry-engine-duplicated-in-application.yml`
- `book-workshop/foundry/self-evolution/upstream/proposed-to-plugin/ecp-0003-engine-as-reference-not-copy.yml`

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
  generating-EOU spec templates.
- `scripts/` — `validate_foundry.py`, `validate_recursive_case.py`,
  `_common.py` helpers, `clean_generated.py`.
- `dev-docs/` — 3 design docs: 01-foundations, 02-architecture, 03-doctrine.

## Pre-release history (informational, not version-tagged)

Before the plugin extraction, the Foundry lived inside a monolithic
repo that also contained the book-workshop application. That tree's
`foundry/self-evolution/changelog.md` named its first internal version
"0.2.0" as a bootstrap exception. That history is consumed by this
plugin's 0.1.0 release — the new bootstrap exception above replaces it.
