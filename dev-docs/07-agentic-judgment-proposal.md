# Agentic Judgment via Well-Defined Domain Values (Proposal)

A forward-looking design proposal that emerged from the Stage 0 design discussion. **Not adopted doctrine.** The core claim: if a foundry app has a well-defined `domain_values:` layer in its Stage 0 captured workflow, EOUs in that app can be authorized to resolve contested cases by invoking those values — gaining agentic judgment capability bounded by the user-authored constitutional layer.

This document exists so a future reader does not re-litigate the question. It depends on the Stage 0 `captured_workflow` and `domain_values` proposals being adopted first; both are still in the design conversation that produced this file, not yet written as separate dev-docs.

## Origin

This emerged from a Stage 0 design conversation. While debating how Stage 0 should capture domain-specific values (analogous to V1–V8 in `06-values-over-rules.md` but per-app), the question surfaced:

> If "value over rules" can be well-defined per domain, then agentic judgment becomes possible. What would this change about the EOU Foundry?

This document is the answer. It is design discussion, not policy.

## Dependencies

This proposal cannot be adopted until:

1. **Stage 0 is adopted.** A `captured_workflow` artifact exists, with a `domain_values:` section that survives the inclusion test (six tests from `06-values-over-rules.md` §"Inclusion test").
2. **Domain values are load-bearing.** Downstream skills (`$generate-eou-candidates`, `$audit-candidate-eou-set`, `$eou-audit`) consult `domain_values` and let them affect outcomes — not decoration.
3. **The value layer's anti-theater protections work.** Counterfactual value-swap audit (described below) survives empirical test on at least one app.

If any dependency fails, agentic judgment cannot be safely enabled. The proposal stays deferred.

## The core claim

Current EOUs are rule-following machines. When two rules pull opposite directions, the EOU escalates to a human. The foundry has no internal mechanism for resolving rule conflicts.

If domain values are well-defined — priority-ordered, contested-form, user-approved — then an EOU can resolve a rule conflict by **invoking** the higher-priority value, recording the invocation in trace, and proceeding. The judgment is bounded by the constitutional layer the human approved during Stage 0.

Analogy: a judge applying law. The legislature defines values (statute); the judge applies them; the judge has bounded judgment authority but never invents law. An agentic EOU has the same shape — bounded judgment within a constitutional frame.

## What "agentic judgment" means here

An EOU with agentic judgment can:

1. Detect a rule conflict during execution
2. Look up the value(s) in `domain_values` whose `decides_when.conflict` entries match the conflict signature
3. Choose the path the higher-priority value dictates
4. Record in trace: which value, which rule conflict, which alternative was rejected, why the rejected alternative would have been a real choice

The judgment is **agentic** because the EOU made it without human escalation. It is **bounded** because the EOU did not create authority — it applied a priority order the human approved. It is **inspectable** because the invocation is recorded in trace per V3.

## Structural changes to the foundry

| Component | Change | Status |
|-----------|--------|--------|
| `VALID_FUNCTIONS` in `schemas/eou.schema.yml` | Add `judge` as 12th canonical verb. Distinct from `audit` (detects failure), `refactor` (changes artifact), `approve` (accepts responsibility). | Requires vocabulary ECP |
| `classification.judgment_authorized` | New boolean flag, orthogonal to `authority_level`. Defaults `false`. | Requires schema ECP |
| Trace schema (`schemas/run-trace.schema.yml`) | Add `value_invocations[]` array. Each entry: `value_id`, `rule_conflict`, `chosen_path`, `rejected_alternative`, `justification_against_rejected`, `timestamp` | Requires schema ECP |
| `validation.judgment` | Promote from prose field to first-class structured field. Predicates machine-checkable against `value_invocations`. | Requires schema clarification |
| Failure taxonomy (`engine/failure-taxonomy.yml`) | Add F14–F17 (defined below) | Doctrine update |
| D4.1 audit layers | Three becomes four: output / run / EOU / **judgment**. Judgment audit asks: "Across runs, are invocations consistent with declared priority? Load-bearing or post-hoc?" | Doctrine update |
| D5.1 separation chain | Five steps: `generate → audit → judge → revise → approve`. Generators surface contested cases; judging EOUs resolve them; revising EOUs apply resolution. | Doctrine update |
| `engine/maturity-model.yml` | New axis: `judgment_maturity` (L1 invocation-naive → L4 audit-verified invocation patterns). Orthogonal to `lifecycle_stage`. | Engine update |

## New failure taxonomy entries

| Code | Name | Catches |
|------|------|---------|
| F14 | Silent Judgment Failure | EOU made a contested choice without invoking any value — opaque agency |
| F15 | Value Hierarchy Failure | EOU invoked a lower-priority value over a higher-priority one for the same conflict |
| F16 | Value Drift Failure | Invocation pattern over time diverges from declared priorities — the system is silently rewriting its own constitution |
| F17 | Value Hallucination | EOU invoked a value not declared in `domain_values` |

F14 is the most dangerous. It looks like rule-following but is actually unaccountable judgment. The judgment-audit layer must detect "where in this run should a value have been invoked but was not?"

## V1 attack surface: value theater

Just as the foundry already names "validator theater" under V1 in `06-values-over-rules.md`, agentic judgment introduces **value theater** — invoking a value as a tag to justify a choice the value did not drive. The EOU records `value_invoked: "story over spectacle"` when the choice was made for unrelated reasons.

Mitigations:

1. **Concrete rejected alternative.** Schema requires `rejected_alternative` to be a real artifact, not "a worse version."
2. **Strawman audit.** Does the rejected alternative resemble something a real practitioner would have produced?
3. **Invocation balance.** One-sided patterns (always invokes V1, never V8) flag for review. A real value layer gets exercised across the priority order.
4. **Counterfactual value-swap audit.** Rerun the EOU with `domain_values` reordered and check whether outputs actually change. If they don't, value invocations were theater — the EOU was running on hidden rules and labeling them.

The counterfactual swap is the strongest defense. If you change the constitution and nothing changes, the constitution was not governing.

## What gets simpler — counterintuitively

**Rules can become stricter without becoming more bureaucratic.**

V5 (Living Judgment) currently fights bureaucracy by leaving the soul unprogrammed. Rules stay loose so judgment has room. The cost: every contested case escalates, automation stays shallow.

With domain values explicit, the soul moves to the constitutional layer. The rule layer can become tight — every rule has a clear interpretation, and contested interpretations resolve via value invocation rather than ambiguity.

**Stricter rules + flexible constitutional layer = deeper automation + preserved judgment.**

V5's protection now lives at the value layer; the rule layer is freed to be precise. This is the deepest shift. The foundry could automate substantially more without becoming "bureaucratic automation" (V5's named anti-pattern) precisely because the constitutional layer is explicit.

## V2 reconfiguration (not reduction)

Human responsibility does not shrink; it relocates.

| Before | After |
|--------|-------|
| Human approves every rule-application result | Human authors the value layer (Stage 0) |
| Human escalation for every contested case | Human reviews judgment-audit patterns |
| Human owns each EOU's outcome | Human owns the constitutional choice |

Total responsibility is constant. Position shifts upward. This is consistent with V2's spirit: humans must own the high-impact decisions. Constitutional choice IS the highest-impact decision. The agent owns the execution; the human owns the constitution.

Risk: humans might rubber-stamp Stage 0 (skim the value layer, approve everything). That risk is more catastrophic under agentic judgment than under rule-following — rubber-stamping now approves the soul, not a single output. Mitigation: Stage 0's user-contribution requirement (≥1 contribution per reference-set role slot, justification for any `user_diverges_from_canonical` value) is no longer just "anti-abdication for literacy users" — it becomes a constitutional gate for every app, expert or novice.

## Stage 0 reframed

Stage 0 was framed as a literacy bridge. Under this proposal, Stage 0 is also **the prerequisite for the foundry to take on agentic execution at all.**

Without explicit domain values:
- The foundry can only do rule-following EOUs (current mode)
- Every contested case must escalate
- Judgment lives in human heads — ungoverned, untraceable

With explicit domain values:
- The foundry can do agentic EOUs
- Contested cases resolve via traceable value invocation
- Judgment lives in artifacts — governed, auditable

The literacy gap was the visible problem. Agentic capability is the hidden gain. Stage 0 turns the foundry from a workflow-formalization tool into a constitutional substrate for autonomous craft systems.

## What this would NOT solve

Honest limits:

- **Value quality.** Bad values produce bad judgments. The value layer is only as good as the user's Stage 0 work. Garbage in, garbage out — but at least the garbage is inspectable.
- **Edge cases.** Contested cases not covered by any domain_value in the layer still escalate. Mechanism: agent records "no applicable value found"; human either decides ad hoc or adds a value (constitutional amendment via ECP).
- **AI accountability.** Accountability still lives with the human who authored the value layer and the human who approved each EOU's `judgment_authorized` flag. Agentic execution moves WHERE accountability sits, not WHETHER it sits.
- **Domain suitability.** Domains in regulated fields (medical, legal, fiduciary) may forbid agentic execution regardless of value clarity. Per-domain `risk_level` governs. The framework allows but doesn't force.

## Net effect: two-tier EOU partition

EOUs partition into two classes under this proposal:

1. **Rule-following EOUs.** `judgment_authorized: false`. Behave as today. No invocation surface. The existing pipeline applies unchanged.
2. **Agentic EOUs.** `judgment_authorized: true`. May invoke domain values to resolve contested cases. Trace records invocations. Judgment audit checks patterns over time.

Tier 2 is unavailable without Stage 0 + domain values. Stage 0 is the gate. Apps that skip Stage 0 stay in Tier 1.

The existing foundry keeps working for Tier 1. Tier 2 emerges only for apps that have done constitutional work.

## Open questions

| Question | Why it matters |
|----------|---------------|
| Can `judge` be expressed as a `function` (parallel to `audit`, `validate`), or is it actually a `judgment_authorized` modifier on existing functions? | Determines whether V8 warrants a new verb or just a flag. If a flag, the vocabulary surface stays smaller. |
| How does a generating EOU handle contested candidates? | D6.1 forbids generators from creating authority. Can a generator pre-invoke a value, or must it surface alternatives as separate candidates? |
| When `domain_values` change (constitutional amendment via ECP), do prior agentic decisions remain valid? | The "ex post facto" question — affects regression-case validity and historical trace audit. |
| Can agentic EOUs invoke foundry V1–V8 directly, or only domain values? | Domain values can strengthen but not weaken foundry values (per D5.5). Direct V1–V8 invocation would be a separate, broader authority surface. |
| What's the minimum `domain_values` count for `judgment_authorized` to be approvable? | A one-value layer is trivially total-ordered but probably not load-bearing. |
| Should `judgment_authorized: true` require a separate ECP per EOU, or is per-app blanket approval acceptable? | Per-EOU is V4-strongest but costly. Per-app is operationally tractable but concentrates risk. |

## Six-layer sync impact (if adopted)

Per `AGENTS.md`, vocabulary changes must propagate through six layers. The minimum touch surface for this proposal:

| Layer | Change |
|-------|--------|
| `schemas/eou.schema.yml` | `VALID_FUNCTIONS` gains `judge`; classification gains `judgment_authorized` |
| `schemas/run-trace.schema.yml` | Add `value_invocations[]` |
| `schemas/captured-workflow.schema.yml` | Already proposed in Stage 0; this proposal piggybacks |
| `scripts/validate_foundry.py` | Add `VALID_FUNCTIONS` entry, validate `value_invocations` shape, run counterfactual-swap audit on demand |
| `skills/` | Possibly one new skill (`$eou-judgment-audit`) or extension of `$eou-audit` to cover the new layer |
| `codex/skills/` | Mirror |
| `rules/` | One or two new rules: "domain values govern domain rule conflicts," "value invocations require concrete rejected alternatives" |
| `engine/meta-eous/` | New meta-EOU for the judgment-audit layer; existing meta-EOUs gain `judgment_authorized: false` explicitly |
| `engine/failure-taxonomy.yml` | Add F14–F17 |
| `engine/maturity-model.yml` | Add `judgment_maturity` axis |

This is a substantial sync burden. The ECP package would likely be three or four coordinated ECPs (vocabulary, schema, doctrine, engine), not a single ECP.

## Smallest validating step

Pick one existing meta-EOU in `engine/meta-eous/`. Identify one contested case it currently escalates. Hand-write the value invocation that WOULD resolve it under a hypothetical `domain_values` layer for the foundry itself (the foundry's V1–V8 are its own domain values for foundry-meta cases). Then test:

- Does the invocation actually decide the case, or is it labeling a hidden rule?
- If you swap the value priority order, does the choice flip?

If the invocation is load-bearing under counterfactual swap, the framework is real and ECPs can begin. If not, the value layer is still aspirational and the proposal stays deferred.

## Status

**Implemented in v0.8.0 via ECPs 0018, 0019, 0020.**

The deferral conditions were satisfied: (a) Stage 0 adopted at v0.7.0 with the `captured_workflow` noun, the `domain_values` constitutional layer, and Rule 96 downstream consumption; (b) the cooking canary (`dev-docs/canary/cooking-restaurant-captured-workflow.yml`) demonstrated 4 clean counterfactual-swap flips out of 5 tests, exceeding the ≥3 load-bearing threshold; (c) Rule 96 enforcement was empirically validated against four synthetic spec scenarios.

What v0.8.0 actually shipped:
- **ECP-0018** — `classification.judgment_authorized` (boolean flag, not new verb — P3 warrant decision), `value_invocations[]` in run-trace schema, validator enforcement (forbidden on `function:generate`; captured_workflow precondition; per-EOU ECP at risk_level high|critical at pilot+); `judgment_blanket_authorization` block in `governance.yml` for risk-tiered hybrid (low|medium may use blanket; high|critical always per-EOU ECP).
- **ECP-0019** — F14_SILENT_JUDGMENT_FAILURE, F15_VALUE_HIERARCHY_FAILURE, F16_VALUE_DRIFT_FAILURE, F17_VALUE_HALLUCINATION_FAILURE added to taxonomy. `judgment_maturity` axis (J0–J4) added to maturity model, orthogonal to lifecycle_stage. D4.1 updated from three audit layers to four (judgment audit). D5.1 separation chain updated from four steps to five (insertion of `judge` step).
- **ECP-0020** — `$audit-judgment` skill (Claude + Codex), Rule 97 (value invocation discipline), counterfactual-swap audit mechanism, `validate_value_invocation_discipline()` walker enforcing F17 id resolution.

Two-tier EOU partition is live: rule-following EOUs (default; `judgment_authorized:false`) behave exactly as before; agentic EOUs (`judgment_authorized:true`) may invoke domain_values to resolve contested cases, with all invocations traced and audited.

## Cross-references

- `06-values-over-rules.md` — the foundry's own value layer that this proposal mirrors at the domain level
- `03-doctrine.md` D4.1 — current three-audit-layer model that gains a fourth layer here
- `03-doctrine.md` D5.1 — current separation chain that grows from four to five steps
- `03-doctrine.md` D5.5 — constitution doctrine; domain values strengthen but cannot weaken foundry values
- `05-v6-design-pulls.md` — precedent for capturing deferred design proposals in dev-docs
- `engine/failure-taxonomy.yml` — current F1–F13 codes that F14–F17 would extend
- `schemas/eou.schema.yml` — current `VALID_FUNCTIONS` enum that `judge` would extend
