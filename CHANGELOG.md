# EOU Foundry Plugin Changelog

## 0.8.0 — Agentic judgment: domain_values become load-bearing at runtime (ECPs 0018, 0019, 0020)

Minor release. Stage 0 (v0.7.0) made the per-app `domain_values` layer real and statically consumed (Rule 96). v0.8.0 makes it operationally enforced at runtime — EOUs with `classification.judgment_authorized:true` may invoke domain_values to resolve contested cases during execution, and a new fourth audit layer (`$audit-judgment`) checks invocation discipline including counterfactual-swap audit. The agentic-judgment package was previously documented as deferred in `dev-docs/07-agentic-judgment-proposal.md`; v0.8.0 implements it.

Per the V2 (Human Responsibility) discipline, agentic judgment is opt-in per EOU and gated by app-level governance — high/critical risk requires per-EOU ECP; low/medium may use blanket authorization via `judgment_blanket_authorization` in `governance.yml`. Apps that do not opt in continue to operate exactly as today.

ECP-0018 — Vocabulary + schema + trace foundation:
- `schemas/eou.schema.yml` adds optional `classification.judgment_authorized` (boolean, default false). Validator enforces three new invariants: forbidden on `function:generate` (D6.1 — generators may not create authority); requires the app to have an approved `captured_workflow` with ≥3 `domain_values`; at risk_level high|critical at lifecycle_stage pilot+ requires per-EOU ECP approval.
- `schemas/run-trace.schema.yml` adds optional `value_invocations[]`. Each entry has 10 required fields — invocation_id, timestamp, captured_workflow_id, captured_workflow_version, domain_value_id, priority_at_invocation, rule_conflict, chosen_path, rejected_alternative, justification_against_rejected.
- `validate_value_invocations_in_trace()` enforces entry shape and a strawman regex against `rejected_alternative` (anti-theater first-line defense).
- `engine/governance.yml` documents the optional `judgment_blanket_authorization` block (apps may declare to grant blanket judgment_authorized at risk_level ≤ medium without per-EOU ECP; high/critical never blanket-authorized).
- `dev-docs/04-vocabulary-principles.md` self-audit gains V-10 entry — `judgment_authorized` is a classification facet (not noun, not verb), four-warrant entry documented.

ECP-0019 — Doctrine + failure taxonomy + maturity axis:
- `dev-docs/03-doctrine.md` D4.1 updated from three audit layers to four (adds judgment audit). D5.1 separation chain updated from four steps to five (insertion of `judge` between audit and revise; the judge step is structurally distinct from audit and revise but composes with existing functions via the `judgment_authorized` flag rather than partitioning the verb space).
- `engine/failure-taxonomy.yml` adds F14_SILENT_JUDGMENT_FAILURE (most dangerous agentic-judgment failure — opaque agency), F15_VALUE_HIERARCHY_FAILURE (lower-priority value invoked when higher would have governed), F16_VALUE_DRIFT_FAILURE (invocation pattern diverges from declared priority without amendment ECP), F17_VALUE_HALLUCINATION_FAILURE (domain_value_id not in captured_workflow).
- `engine/maturity-model.yml` adds `judgment_maturity` axis (J0_NO_AUTHORIZATION → J1_INVOCATION_NAIVE → J2_INVOCATION_PRESENT → J3_AUDIT_VERIFIED → J4_DRIFT_MONITORED) — orthogonal to lifecycle_stage. An EOU may be `lifecycle_stage:active` (L4_AUDITABLE on rule-following axis) but `judgment_maturity:J1` (invocation-naive). The axes are independent capability tiers.

ECP-0020 — Audit-judgment skill + Rule 97 + counterfactual-swap mechanism:
- `engine/meta-eous/audit-judgment.yml` new — function:audit, target_object:value_invocations, authority_level:write_inactive, risk_level:medium, lifecycle_stage:candidate, `judgment_authorized:false` (audit-judgment AUDITS invocations; it does not invoke).
- `skills/audit-judgment/SKILL.md` + Codex mirror new. 7-step procedure: load + verify preconditions; F17 id-resolution check; F15 hierarchy check; F16 drift analysis (≥3 runs required); F14 silent-judgment check; counterfactual-swap audit (up to 5 sampled swap-tests; ≥3 output changes = load-bearing PASS, <3 = HIGH-severity F14 theater pattern); compose judgment-audit report at `foundry/audits/judgment-audits/{eou_id}.judgment-audit.yml`.
- `rules/97-value-invocation.md` new. 5 MUST requirements — every contested case produces invocation OR escalation; invocations respect declared priority; rejected_alternative is concrete (not strawman); domain_value_id resolves; counterfactual swap produces ≥3 changes out of 5. Complements Rule 96 — Rule 96 governs static spec consumption; Rule 97 governs runtime invocation discipline.
- `scripts/validate_foundry.py` gains `validate_value_invocation_discipline()` walker enforcing the declarative subset of Rule 97 — domain_value_id resolution against captured_workflow at every value_invocations entry. The judgment-heavy checks (F14 silent, F15 hierarchy, F16 drift, counterfactual swap) live in the skill, not the validator.
- `AGENTS.md` skill table gains `$audit-judgment` row + behavioral constraints note.

Quality and V-discipline:
- Vocabulary correction — `F17_VALUE_HALLUCINATION` renamed to `F17_VALUE_HALLUCINATION_FAILURE` for P1 uniform-granularity with F1–F16 (initial draft omitted the `_FAILURE` suffix; renamed across all 6 vocab layers).
- Closure correction — `rule_98_judgment_blanket_authorization` renamed to `judgment_blanket_authorization` (P4 closure — the original name referenced a non-existent Rule 98; the blanket-authorization block is ECP-0018 validator apparatus, not a separately-numbered governance rule).
- Regression fixtures — `self-evolution/regression/cases/` gains rc-f14, rc-f15, rc-f16, rc-f17 (V3+V6 gap closed). rc-f17 is active (validator catches it via the f17-hallucinated-dv-id fixture); rc-f14/15/16 are candidate (await `$audit-judgment` first-run activation).
- End-to-end fixture — `tests/fixture-foundry/foundry/eous/sample-judgment-eou.yml` + run trace exercise the full agentic-judgment chain (judgment_authorized:true → value_invocations with valid dv-001 invocation → all 4 walkers pass). V1 empty-cage risk closed.
- NLPM score — every NL artifact in the plugin at 100/100 under strict mode (50 artifacts assessed). Vague-quantifier sweep removed 20+ findings across the plugin, including in historical dev-docs.

Optionality: agentic judgment is opt-in per EOU. EOUs with `judgment_authorized:false` (or absent) behave exactly as today. Rule 97 enforcement only fires when an EOU has `judgment_authorized:true` AND the app has an approved captured_workflow. No retroactive burden on existing apps or existing EOUs.

Forward-looking dev-docs updated:
- `dev-docs/07-agentic-judgment-proposal.md` Status flipped from "Deferred" to "Implemented in 0.8.0 via ECPs 0018-0020."

## 0.7.0 — Stage 0: reference-grounded workflow capture + per-app constitutional layer (ECPs 0015, 0016, 0017)

Minor release. Introduces Stage 0 — the literacy-bridge and constitutional-bootstrap layer that synthesizes the inputs to `$generate-eou-candidates` from a user goal, structured reference set, and constraints. Optional for every app (apps without a `captured_workflow` continue unchanged); when adopted, the new `domain_values` constitutional layer governs downstream EOU candidate scoring, set audit, and per-spec audit per the new Rule 96.

ECP-0015 — Captured-workflow noun + schema + validator walker:
- `schemas/captured-workflow.schema.yml` new. Required: id, schema_version, created_at, inputs (with 5-role reference_set + user_contributed_references ≥1 per slot), artifact_target, captured_workflow prose, hidden_judgments, failure_modes, decision_boundaries, domain_values (3–8 in priority total order with inclusion test, contested-form "X over Y" formulation, canonical_or_personal marker, conditional justification_if_diverges), confidence, human_approval (4-gate).
- Canonical storage path: `foundry/captured-workflows/cw-{slug}.yml`. Lifecycle constraint — artifact remains at `lifecycle_stage: candidate` permanently; never promoted.
- `validate_captured_workflows()` new walker enforces structural shape including: all 5 reference role slots non-empty (outlier slot mandatory per V1 defense), user contribution ≥1 per slot (V2 anti-abdication), domain_values count in [3,8], priority total order, inclusion-test booleans (≥1 true), contested-form pattern with strawman-list check, confidence enum, all 4 human_approval gates + approved_at, id-matches-filename.
- `dev-docs/04-vocabulary-principles.md` noun catalog updated with four-warrant entry (literary D2.4 step 1; user literacy-gap case; structural P4 closure; domain V1-V8 analog).
- Fixture at `tests/fixture-foundry/foundry/captured-workflows/cw-example.yml`.

ECP-0016 — Producer skill `$generate-captured-workflow-from-references`:
- `engine/meta-eous/generate-captured-workflow-from-references.yml` new — function:generate, target_object:captured_workflow, authority_level:write_candidate, risk_level:medium, lifecycle_stage:candidate. Full rule-95 declaration: generation_envelope (allowed_outputs:[captured_workflow], forbidden_outputs explicitly includes eou_candidate and candidate_set for D5.1 separation), generation_budget (max_candidates:1 — single-output specialization documented), registry_diff, minimality_test, operational_value_test (5 reject_if conditions including "user can articulate workflow unaided"), counter_generation (per-bundle arguments_against template), blast_radius (forbids touching everything outside foundry/captured-workflows/ and its run-trace directory).
- `skills/generate-captured-workflow-from-references/SKILL.md` new + Codex mirror. 11-step procedure (validate → per-reference justification → counterfactual deconstruction → negative-space analysis → comparative analysis → convergence → synthesis → pattern detection → priority ordering → confidence calibration → bundle + 4-gate approval). Five explicit refusals documented. Mechanism-only — zero domain assertions.
- Separate-skill-vs-mode counter-generation argument resolved in favor of separate skill on 7 structural grounds (D5.1 separation, D2.4 step boundary, F12 drift prevention, lifecycle reuse, risk_level distinction, V4 bounded authority, optionality clarity).
- AGENTS.md skill-selection table updated.

ECP-0017 — Downstream consumption rule (Rule 96) + meta-EOU updates:
- `rules/96-domain-values-consumption.md` new. When an approved captured_workflow exists, downstream EOU-pipeline skills MUST consult its domain_values; specs at `lifecycle_stage: pilot` or higher MUST operationalize at least one top-three priority domain_value for the spec's target_object.
- `engine/meta-eous/generate-eou-candidates.yml` adds captured_workflow to inputs.optional + new execution step for domain-value scoring of candidate `arguments_against`.
- `engine/meta-eous/audit-candidate-eou-set.yml` adds captured_workflow to inputs.optional + new Set Value Coverage Test (verifies recommended subset operationalizes priority≤3 values).
- `engine/meta-eous/audit-eou.yml` adds captured_workflow auto-discovery + new Value Operationalization Test (severity by lifecycle_stage: blocking at active+, high at pilot, medium at draft/candidate).
- Six SKILL.md files updated (3 Claude + 3 Codex mirrors).
- `validate_domain_values_consumption()` new walker — for each spec at pilot+, if approved captured_workflow exists and target_object is not exempt, string-match success_criteria.must_pass for any top-three domain_value id; flag violations.
- `engine/governance.yml` adds `rule_96_exempt_target_objects` (registry, ECP, candidate_set, run_trace, incident, regression_case, no_trace_justification, captured_workflow, foundry governance object) — exempt target_objects governed by foundry V1–V8, not by app domain_values.
- Multi-tenant resolution: spec belongs to captured_workflow with longest common path prefix; per-instance scopes (e.g., book-workshop's BOOK_PATH) supported.
- Bootstrap exemption: specs predating captured_workflow approval exempt for one minor version (detection via versioning.changelog timestamps or git commit date fallback).
- AGENTS.md Behavioral constraints adds Rule 96 enforcement clause.
- Citation-theater defense (counterfactual-swap audit) explicitly deferred to the agentic-judgment ECP package; until then, $eou-audit reviewers spot-check value invocations.

Forward-looking dev-docs (proposals only, deferred):
- `dev-docs/07-agentic-judgment-proposal.md` — agentic-EOU capability tier (`judge` verb, `judgment_authorized` flag, F14–F17 failure codes, judgment-audit layer, value theater + counterfactual-swap defense). Status — deferred; requires Stage 0 to land and survive empirical counterfactual-swap testing.
- `dev-docs/08-stage-0-design.md` — full Stage 0 design including universality across 8 craft domains, V-discipline mapping, open questions, and ECP package shape.
- `dev-docs/canary/cooking-restaurant-captured-workflow.yml` — hand-drafted canary that validated the design pre-implementation. Inclusion test: 5/5 values × 6/6 criteria pass. Counterfactual swap: 4 clean choice flips out of 5 tests (threshold ≥3). Verdict — PASS.

Optionality: Stage 0 is optional. Apps without a captured_workflow continue to use `$generate-eou-candidates` with workflow prose exactly as before. Rule 96 enforcement only fires when an approved captured_workflow exists. No retroactive burden on existing apps.

## 0.6.0 — Lifecycle/evidence triangle + closure gaps (ECPs 0007, 0009, 0010, 0013, 0014)

Minor release. Implements the three coupled ECPs from the audit
roundtable that turn lifecycle claims from self-declarations into
evidence-bound assertions, plus two closure gaps surfaced by adversarial
review of the V6 architecture proposal. Breaking for applications with
active EOUs that claim higher maturity than their evidence supports OR
that have not declared trace output / no-trace-justification.

ECP-0013 — Candidate-set schema and validation (V6 closure gap):
- `schemas/candidate-set.schema.yml` new. Required fields: id, generated_by,
  generated_at, target_class (eou_spec | ecp | regression_case |
  refactor_option), candidates, audit_outcome, audit_status (pending_audit
  | audited | rejected_in_full).
- Canonical storage path: `foundry/self-evolution/candidate-sets/cs-{generating_eou}-{YYYYMMDD}-{hhmm}.yml`.
  Pre-v0.6.0 layout (`foundry/self-evolution/ecp/proposed/{slug}-candidates-{YYYYMMDD}.yml`)
  is deprecated; the ECP/candidate-set skip-pattern workaround in
  validate_ecps is no longer required (kept for legacy compatibility).
- `validate_candidate_sets()` new walker enforces: every candidate has
  `status: candidate` and non-empty `arguments_against`; `audit_outcome`
  declares all seven required keys (accepted, merged, demoted_to_rule,
  demoted_to_validator, demoted_to_stop_condition, rejected,
  minimal_recommended_subset); `audit_status: audited` requires either
  `minimal_recommended_subset` or `rejected` to be non-empty (an audited
  set must explicitly say what survived and what didn't).
- `engine/meta-eous/generate-eou-candidates.yml` updated to declare the
  canonical output path; `engine/meta-eous/audit-candidate-eou-set.yml`
  updated to consume from it.
- Skills (Claude + Codex) and `rules/95-generating-eous.md` updated.

ECP-0014 — Active-EOU trace gate enforcement (hard-cut):
- `validate_active_trace_obligation()` new function. For each EOU at
  lifecycle_stage in {active, monitored, stable}, requires ONE OF:
  (a) `outputs.trace` is a non-empty list whose entries reference paths
  under `runs/`, OR (b) `foundry/audits/no-trace/{eou_id}.yml` exists,
  parses, has non-empty `reviewed_by` (NOT matching /^TODO/i), and has
  `expires_at` in the future. Hard-cut at 0.6.0 — no warning phase, no
  deprecation window. The no-trace-justification mechanism IS the
  migration path; apps that cannot meet the gate write an explicit
  exemption with a named human reviewer and expiry date.
- `validate_no_trace_justifications()` strengthened to reject TODO
  placeholder reviewers (anti-gaming clause).
- Scope: app-side EOUs only (`foundry/eous/`, `foundry/meta-eous/`).
  Engine canonical meta-EOUs are explicitly NOT walked — plugin governs
  its own engine via the foundry-audit skill.
- Structural check, not runtime: verifies the EOU spec commits to
  producing trace, OR is exempted. Does NOT verify run trace files
  exist on disk (that's a separate run-audit pass).
- `rules/93-recursive-governance.md` updated to reflect hard-cut
  enforcement and TODO-placeholder rejection.

Test infrastructure:
- `tests/regression-fixtures/active-no-trace/` — verifies ECP-0014
  hard-error on active EOU lacking both trace and justification.
- `tests/regression-fixtures/bad-candidate-set/` — verifies ECP-0013
  rejects malformed candidate-set artifacts.
- `.github/workflows/pr-ci.yml` adds a regression-fixtures step that
  asserts each fixture fails validation (catches silent validator
  regressions like ECP-0004's PR #4 class).



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
