---
name: 96-domain-values-consumption
description: Require downstream EOU-pipeline skills to consult domain_values when an approved captured_workflow exists for the consuming app. Specs in such apps MUST operationalize at least one of the top-three priority domain_values for the spec's target_object.
---

# Domain Values Consumption Rule

**When an approved captured_workflow exists for the consuming app, downstream pipeline skills MUST consult its domain_values, and EOU specs MUST operationalize at least one top-three priority value for their target_object.** Without this rule, the per-app constitutional layer is decoration — the foundry teaches values-over-rules discipline (`06-values-over-rules.md`) but silently permits apps to ignore their analog. Rule 96 closes the consumption gap that ECP-0015 opened and ECP-0016 filled.

## When this rule applies

IF a `captured_workflow` exists at `foundry/captured-workflows/{slug}.yml` AND its `human_approval` block is populated at all four gates (reference_set, constraints, domain_values, bundle), THEN this rule applies to every EOU spec in the same scope.

Apps without a captured_workflow are exempt — Stage 0 is optional. Apps with an unapproved (incomplete `human_approval`) captured_workflow are also exempt; the captured_workflow is not consumption-ready until all four gates are populated.

## MUST requirements

1. **`$generate-eou-candidates`** MUST accept `captured_workflow` as an optional input. When present, the skill MUST score each candidate's `arguments_against` against the top-three priority `domain_values`. Candidates whose execution would clearly violate a priority-1 value MUST be flagged with explicit value citation.
2. **`$audit-candidate-eou-set`** MUST run the **Set Value Coverage Test** when a captured_workflow is present — for each domain_value of priority ≤ 3, verify that at least one candidate in the `minimal_recommended_subset` operationalizes the value via its `distinct_success_criterion`. Unserved top-priority values MUST be flagged in `audit_outcome.notes`.
3. **`$eou-audit`** MUST run the **Value Operationalization Test** for every spec in an app with a captured_workflow — at least one `success_criteria.must_pass` entry MUST reference a domain_value of priority ≤ 3 by `id` for the spec's `target_object`. Severity of violation: `blocking` at `lifecycle_stage: active` or higher; `high` at `pilot`; `medium` at `draft` or `candidate`.

## Detection mechanism

`validate_domain_values_consumption()` in `scripts/validate_foundry.py` walks `foundry/eous/` and `foundry/meta-eous/`. For each spec — load the parent app's `foundry/captured-workflows/` directory; if any captured_workflow has `human_approval` complete, extract the list of domain_value `id` entries with `priority ≤ 3`; scan the spec's `success_criteria.must_pass` for references to those ids; if no reference found AND the spec is at `lifecycle_stage: pilot` or higher AND `target_object` is not in `rule_96_exempt_target_objects`, emit a Rule 96 violation.

The threshold "priority ≤ 3" (top three values) mirrors the foundry's own V1–V3 partition (`epistemic_integrity`, `human_responsibility`, `inspectable_evidence`) which functions as the non-negotiable core of V1–V8. It bounds the operationalization burden — every spec must operationalize at least one of three, not all of three, not all eight. The threshold is hard-coded in this rule; future ECPs may parameterize per-app.

## Violation indicators

| Signal | Severity | Required action |
|--------|----------|-----------------|
| EOU spec at `active` or higher in app with approved captured_workflow has no value invocation in `success_criteria.must_pass` AND `target_object` is not exempt | blocking | Block promotion; require spec revision to operationalize a value |
| `$generate-eou-candidates` produces a candidate whose execution would clearly violate a priority-1 domain_value | blocking | Reject candidate; emit `arguments_against` citing the violated value |
| `$audit-candidate-eou-set` recommends a subset that abandons a domain_value of priority ≤ 3 | high | Require explicit justification in `audit_outcome.notes` |
| `$eou-audit` passes a spec without running the Value Operationalization Test in an app with captured_workflow | medium | Flag the audit run; re-run with Value Operationalization Test applied |
| Spec contains a value id reference that resolves to a domain_value of priority > 3 (lower-priority value) but no top-three reference | low | Acceptable but flagged — top-three coverage is required, not lower-tier |

## Exemptions

- **Apps with no captured_workflow.** Stage 0 is optional. Rule 96 does not apply.
- **Apps with unapproved captured_workflow.** All 4 `human_approval` gates must be populated. Otherwise the captured_workflow is not consumption-ready.
- **Foundry-infrastructure target_objects.** Specs whose `target_object` is in `rule_96_exempt_target_objects` (declared in `engine/governance.yml`) are exempt. These target_objects are governed by foundry V1–V8, not by app-level domain_values. Initial exempt set — `registry`, `ECP`, `candidate_set`, `candidate EOU set`, `run_trace`, `incident`, `regression_case`, `no_trace_justification`, `captured_workflow`, `foundry governance object`. Additions land via vocabulary ECP.
- **Bootstrap EOUs.** Specs whose creation predates the captured_workflow's `human_approval.approved_at` are exempt for one minor version after captured_workflow approval. Detection — the validator compares the spec's `versioning.changelog` earliest entry against `captured_workflow.human_approval.approved_at`; if the spec predates approval, the bootstrap exemption applies. Specs without changelog timestamps fall back to git commit date of the spec file. Bootstrap exemption expires at the next minor version after captured_workflow approval; specs not updated by then become Rule 96 violations.

## Multi-tenant resolution

A spec belongs to the captured_workflow whose path is closest (longest common prefix) to the spec's path. For apps with per-instance scope (e.g., `book-workshop`'s per-book `BOOK_PATH`), the spec inherits the per-instance captured_workflow at `books/{book_id}/captured-workflows/` if one exists, falling back to the app-level `foundry/captured-workflows/` if not. Apps using per-instance Stage 0 MUST declare `CAPTURED_WORKFLOW_PATH` alongside the existing path placeholder in their EOU spec `path_root` declaration.

## Relationship to foundry V1-V8

Per `03-doctrine.md` D5.5, app-level `domain_values` can STRENGTHEN but cannot WEAKEN foundry V1–V8. If a domain_value contradicts a foundry-level value, the foundry value wins. Rule 96 does NOT permit downstream skills to invoke a domain_value to relax V1 (epistemic integrity), V2 (human responsibility), V3 (inspectable evidence), V4 (bounded authority), V5 (living judgment), V6 (failure memory), V7 (minimality), or V8 (semantic integrity).

## Limits of mechanical enforcement (citation theater)

`validate_domain_values_consumption()` detects value references by string-matching domain_value `id` entries in `success_criteria.must_pass` text. A spec could cite an id as a string match without actually operationalizing the value — citation theater. This is the V1 attack surface named in `07-agentic-judgment-proposal.md`, applied at the spec level. The durable defense is **counterfactual-swap audit**, which is deferred until the agentic-judgment ECP package lands. Until then, the audit layer's judgment-based predicates in `$eou-audit` surface theater (an experienced reviewer can tell when a value citation is decorative). Reviewers SHOULD spot-check value invocations for decorative pattern.

## Cross-references

- `06-values-over-rules.md` — the foundry's V1–V8 layer this rule mirrors at app level
- `08-stage-0-design.md` — Stage 0 design rationale
- `07-agentic-judgment-proposal.md` — downstream implication (deferred)
- `schemas/captured-workflow.schema.yml` — the artifact this rule consumes
- `engine/governance.yml` — `rule_96_exempt_target_objects` list
- ECPs 0015 / 0016 / 0017 (coordinated Stage 0 release at v0.7.0)
