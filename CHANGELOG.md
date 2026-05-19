# EOU Foundry Plugin Changelog

## 0.6.0 — Lifecycle/evidence triangle (ECPs 0007, 0009, 0010)

Minor release. Implements the three coupled ECPs from the audit
roundtable that together turn lifecycle claims from self-declarations
into evidence-bound assertions. Breaking for applications with active
EOUs that claim higher maturity than their evidence supports.

ECP-0007 — Run trace shape (stage 1):
- `schemas/run-trace.schema.yml` bumped to v3. Required: run_id, eou_id,
  eou_version, status (success/partial/failed/aborted), started_at,
  ended_at, executor_identity, inputs, context_loaded, steps_completed,
  warnings, outputs, validation, human_approval. Storage:
  `foundry/runs/{eou_id}/{run_id}.yml`.
- `schemas/no-trace-justification.schema.yml` new. Required: eou_id,
  impossibility_reason, reviewed_by, reviewed_at, expires_at. Storage:
  `foundry/audits/no-trace/{eou_id}.yml`. "We haven't gotten around to
  it" is not an impossibility reason.
- `scripts/runs.py` new — `record_run()` helper for EOU implementations.
- `scripts/init_app.sh` scaffolds `foundry/audits/no-trace/`.
- `rules/93-recursive-governance.md` documents trace evidence.

ECP-0009 — Dependency DAG + maturity evidence:
- `schemas/registry-entry.schema.yml` bumped to v3. `dependencies.eous`
  optional list shape introduced; entries that declare it form a DAG
  the validator walks.
- `scripts/validate_foundry.py` builds the DAG, refuses cycles and
  references to retired EOUs.
- New `validate_maturity_evidence()` reads `engine/maturity-model.yml`
  and refuses any registry entry whose `maturity` claim is below the
  level required by its `lifecycle_stage` (per the established
  `lifecycle_stage_to_maturity_mapping`).

ECP-0010 — Activation evidence:
- `schemas/registry-entry.schema.yml` introduces `activated_by`:
  either `{ecp_id, approver, activated_at}` or `{legacy_bootstrap:
  true, bootstrap_justification, bootstrap_expires_at}`.
- `validate_activation_evidence()` refuses status:
  active/monitored/stable without populated `activated_by`. Legacy
  bootstrap accepted during transition; bootstrap_expires_at enforces
  re-evaluation.
- `rules/89-eou-foundry.md` documents activation evidence + maturity
  evidence + dependency DAG.

Migration for consuming apps:
- Apps whose active EOUs lack `activated_by` will fail validation.
  Either backfill `activated_by` (with named approver + activation
  date), or use the legacy_bootstrap escape with an expiry date, or
  demote out of active stages.
- Apps whose maturity claims exceed evidence will fail. Either produce
  the evidence (regression cases for L4, run traces for L3) or demote
  the lifecycle_stage to match the actual evidence level.
- book-workshop migrated by demoting its 4 EOUs from active to draft
  (matching their actual L2_STRUCTURED evidence) — a transparent
  acknowledgment that the workshop EOUs are scaffold-level until
  trace + audit discipline is established.

Tracking:

- ECPs 0007, 0009, 0010 in
  `book-workshop/foundry/self-evolution/upstream/proposed-to-plugin/`

## 0.5.2 — Patch bundle: version pinning, path discovery, governance exception, foundry guard, validator move

Bug-fix patch bundling six approved ECPs from the post-roundtable
deferred-finding review.

What changed:

- **ECP-0005 (`scripts/validate_foundry.py`)**: parse and enforce the
  `inherits_from: "eou-foundry@<spec>"` version constraint against the
  installed plugin version. Supported spec syntax: `==X.Y.Z`, `>=X.Y.Z`,
  `~=X.Y` (compatible release), or bare `X.Y.Z` (≡ `==`). An app pinned
  to a constraint the installed plugin doesn't satisfy fails validation
  with a specific error. The version string in `inherits_from` is now
  a contract, not decoration.
- **ECP-0006 (`scripts/validate_foundry.py`)**: plugin path discovery
  unified. Priority: `EOU_FOUNDRY_PLUGIN_PATH` env var, then
  `claude plugin path eou-foundry@xiaolai` (Claude Code install), then
  fallback to `Path(__file__).parents[1]` for plugin self-test. The
  prior hardcoded user-specific fallback in book-workshop is removed in
  a companion workshop commit.
- **ECP-0008 (`scripts/`)**: `validate_recursive_case.py` deleted from
  plugin. The script validates a workshop-specific case study; it never
  belonged in the plugin. Workshop adds its own copy in the companion
  commit.
- **ECP-0011 (`rules/94-no-self-approval.md`)**: explicit "Audited
  exceptions" section names the CI auto-merge from the `xiaolai`
  maintainer identity as a recorded, conditioned, revocable exception
  to the general no-self-approval rule. Three conditions: CI must pass,
  audit logs retained, revocable by follow-on ECP.
- **ECP-0012 (`scripts/init_app.sh`)**: new apps now scaffold with a
  foundry guard hook. `.claude/hooks/foundry_guard.py` runs
  validate_foundry on any foundry/ write; scoped by `$CLAUDE_FILE_PATHS`
  so unrelated edits don't trigger it. Companion workshop commit
  retro-fits the same hook into book-workshop.

What did *not* ship in 0.5.2:
- The lifecycle/evidence triangle (run trace shape, dependency DAG +
  maturity evidence, activation evidence) is the 0.6.0 minor release.
  See ECP-0007, ECP-0009, ECP-0010.

Tracking:

- ECPs 0005, 0006, 0008, 0011, 0012 in
  `book-workshop/foundry/self-evolution/upstream/proposed-to-plugin/`
- Workshop-side ECP-0001 (promote_upstream temp clone) is workshop-internal
  and lands in workshop's `foundry/self-evolution/ecp/proposed/`.

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
