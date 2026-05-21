---
name: 97-value-invocation
description: Require EOUs with classification.judgment_authorized:true to record every contested-case resolution as a value_invocations[] entry in run trace; require invocations to respect declared priority; require rejected_alternative to be a concrete artifact (not strawman); require counterfactual-swap audit to produce ≥3 output changes out of 5 swap-tests; classify violations under F14–F17.
---

# Value Invocation Rule

**EOUs with `classification.judgment_authorized:true` MUST record every contested-case resolution as a `value_invocations[]` entry in run trace, MUST respect declared domain_values priority, and MUST survive counterfactual-swap audit.** Without this rule, agentic capability becomes silent capability — invocations happen but cannot be audited, contested cases get resolved without trace, and the constitutional layer drifts by precedent. Rule 97 closes the loop that ECP-0018 opens (schema for invocations) and ECP-0019 frames (failure codes F14–F17). The `$audit-judgment` skill (ECP-0020) enforces Rule 97 per audit run; the validator enforces the declarative subset.

## When this rule applies

IF an EOU has `classification.judgment_authorized:true` AND the app has an approved `captured_workflow` with ≥3 `domain_values`, THEN this rule applies to every run of that EOU at `lifecycle_stage: simulated` or higher.

EOUs at `lifecycle_stage: candidate` or `draft` MAY produce `value_invocations`, but Rule 97 enforcement is advisory at those stages (the same MUST requirements apply with reduced severity per the violation table). Apps without an approved `captured_workflow` cannot have `judgment_authorized:true` (ECP-0018 validator blocks this), so the rule's premise is structurally guarded.

## MUST requirements

1. **Every contested case MUST produce an invocation OR an escalation.** A contested case is any decision the EOU must make where two or more `domain_values` would resolve it differently. For each contested case, the run trace MUST contain either (a) a `value_invocations[]` entry with all 10 required fields per `schemas/run-trace.schema.yml`, OR (b) an `escalations_triggered[]` entry referencing the case and the human approver invoked.

2. **Invocations MUST respect declared priority.** When two `domain_values` would resolve the case differently, the higher-priority value MUST be invoked. Lower-priority invocations on contested cases require an explicit override `justification` field in the invocation entry.

3. **`rejected_alternative` MUST be a concrete artifact.** Not abstract description ("a worse version"). The validator rejects entries where `rejected_alternative` matches the regex `/strawman|weaker|worse|generic/i`; the audit-judgment skill performs the deeper plausibility check.

4. **`domain_value_id` MUST resolve.** Every invocation cites a `domain_value.id` from the app's captured_workflow. Hallucinated ids that do not resolve are F17 violations (severity blocking).

5. **Counterfactual-swap audit MUST produce ≥3 output changes out of 5 swap-tests.** The `$audit-judgment` skill runs the swap audit periodically. Below this threshold, invocations are likely decorative (F14 or F15 pattern depending on the specific invocations involved).

## Detection mechanism

Two-layer enforcement:

- **`scripts/validate_foundry.py`** — `validate_value_invocations_in_trace()` (ECP-0018) checks structural shape: 10 required fields per entry, strawman regex on `rejected_alternative`. `validate_value_invocation_discipline()` (ECP-0020) extends this with `domain_value_id` resolution against the captured_workflow. Both run at every `validate_foundry.py` invocation; they catch the declarative subset.
- **`$audit-judgment` skill** (ECP-0020) — runs F14 (silent), F15 (hierarchy), F16 (drift), F17 (hallucination) checks plus counterfactual-swap audit. Produces `foundry/audits/judgment-audits/{eou_id}.judgment-audit.yml`. Run on-demand or as part of `$foundry-audit` portfolio sweep.

The validator catches mechanically-checkable issues. The skill catches judgment-heavy issues. Together they cover Rule 97; alone neither suffices.

## Violation indicators

| Signal | Severity | F-code | Required action |
|--------|----------|--------|-----------------|
| Run with contested case AND no invocation AND no escalation | blocking at pilot+; high at simulated; medium at draft/candidate | F14 | Update EOU to surface contested cases; add regression case for the specific pattern |
| Invocation with lower-priority value when higher value would have resolved (no override justification) | high | F15 | Re-examine priority order; if priority needs revision, propose captured_workflow amendment ECP; if invocation was wrong, add regression case for the EOU |
| Invocation pattern over ≥3 runs deviates from declared priority by >20% on top-three values (no amendment ECP) | high | F16 | Triage drift — reset invocation behavior (regression suite) OR formalize as captured_workflow amendment via ECP. Drift must never continue undocumented per D5.5 |
| Invocation with `domain_value_id` not in captured_workflow's current domain_values list | blocking | F17 | Validate id at invocation time; investigate prompt or training-data contamination; add regression case for the hallucinated id pattern |
| Counterfactual-swap audit produces <3 output changes out of 5 swap-tests | high | F14 (theater pattern) | Re-investigate whether invocations are decoration or load-bearing; human reviewer required for ≤1 change out of 5 |
| `rejected_alternative` matches strawman regex (empty, "a weaker version", "a worse one", etc.) | medium | F14 (pre-theater warning) | Update invocation to record a concrete rejected artifact; reviewer spot-checks plausibility |

## Exemptions

- **EOUs with `judgment_authorized:false`.** Rule 97 does not apply (the rule's premise is false).
- **Apps without an approved captured_workflow with ≥3 domain_values.** `judgment_authorized:true` is itself blocked by ECP-0018 validator in this case; Rule 97 has no live target.
- **EOUs at `lifecycle_stage: candidate` or `draft`.** Rule 97 enforcement begins at `simulated`. Earlier stages may produce invocations but the requirements are reduced-severity (per the violation table).
- **Counterfactual-swap audit for non-deterministic LLM_assisted EOUs** requires ≥2 baseline control runs at original priority to measure natural output variance. Without baseline, the swap audit cannot distinguish swap-driven changes from natural variance; emit "swap audit not yet evaluable" rather than a finding.

## Relationship to foundry V1–V8

Per `dev-docs/03-doctrine.md` D5.5, app-level `domain_values` can STRENGTHEN but cannot WEAKEN foundry V1–V8. Rule 97 enforces the same principle at runtime — an invocation that cites a `domain_value` whose effect would weaken V1 (epistemic integrity), V2 (human responsibility), V3 (inspectable evidence), V4 (bounded authority), V5 (living judgment), V6 (failure memory), V7 (minimality), or V8 (semantic integrity) MUST be escalated to a human approver. The `escalations_triggered[]` entry replaces the `value_invocations[]` entry in such cases; the EOU itself does not perform the resolution.

## Relationship to Rule 96

Rule 96 governs **static spec discipline** — every spec at `lifecycle_stage: pilot` or higher in an app with an approved captured_workflow MUST operationalize at least one top-three `domain_value` in `success_criteria.must_pass`. Rule 97 governs **runtime invocation discipline** — every contested case at runtime MUST produce an invocation that respects priority and survives counterfactual swap.

The two rules together close the constitutional loop: specs must CITE values (Rule 96); runs must INVOKE them respecting declared priority and producing `value_invocations[]` entries that satisfy MUST requirements 1–5 above (Rule 97). Without both, the constitutional layer is half-enforced.

| Rule | Enforces | Skill | Layer |
|------|----------|-------|-------|
| 96 | Static spec discipline | `$eou-audit` (Value Operationalization Test) | spec-time |
| 97 | Runtime invocation discipline | `$audit-judgment` | run-time |

## Limits of mechanical enforcement (sophisticated theater)

The validator's strawman regex and the audit-judgment skill's counterfactual-swap audit catch **decorative** theater (citation without effect). They do not catch **sophisticated** theater — consistent fabrication where invocations are internally consistent and survive swap (because the fabricated reasoning is structured). Per V2 (Human Responsibility), humans remain the final defense against sophisticated theater. The `$audit-judgment` report includes a "reviewer-required-for" section flagging invocations that are mechanically clean but warrant judgment-based review.

## Cross-references

- `06-values-over-rules.md` — V1 (Epistemic Integrity) attack surface that this rule defends
- `08-stage-0-design.md` — Stage 0 captured_workflow design (the constitutional substrate)
- `07-agentic-judgment-proposal.md` — agentic-judgment package design (the conceptual frame)
- `96-domain-values-consumption.md` — companion rule (static spec discipline)
- `schemas/eou.schema.yml` — `classification.judgment_authorized` field (ECP-0018)
- `schemas/run-trace.schema.yml` — `value_invocations[]` entry shape (ECP-0018)
- `engine/failure-taxonomy.yml` — F14–F17 definitions (ECP-0019)
- `engine/maturity-model.yml` — judgment_maturity J0–J4 axis (ECP-0019)
- ECPs 0018 / 0019 / 0020 — coordinated agentic-judgment package
