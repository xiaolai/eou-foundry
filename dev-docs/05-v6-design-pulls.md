# V6 Design Pulls

A log of what we absorbed from the V6 architecture proposal, what we deferred, and what we rejected — with the specific ECPs each absorbed item became. The goal is to prevent re-litigation: when a future reader opens the V6 package and asks "why didn't we adopt the profile split?", this is where the reasoning lives.

## Source

The V6 proposal lives in an external package (`eou_foundry_v6_artifacts.zip`), produced by a parallel design conversation that took our V2 dev-docs (01–04) through 13 iterations. Canonical V6 artifacts:

- `architecture_v6_staged_governed_effect_system.md` — full V6 spec
- `v6_minimal_doctrine_layer.md` — 7-category doctrine (D1–D7)
- `independent_architect_audit.md` — the audit that pushed V4 → V5 → V6, explicitly recommending staged rollout

Our review and Codex's adversarial review both concluded: V6 is strong as theory-of-control, weak as migration-aware operating system. The biggest blind spot — *"no empirical operating base, heavy ontological closure"* (Codex) — colors every absorption decision below.

---

## Absorbed (shipped or shipping)

| V6 idea | Where it landed | Notes |
|---|---|---|
| **Candidate brief as governed artifact** | ECP-0013 (v0.6.0) — `schemas/candidate-set.schema.yml`, canonical path `foundry/self-evolution/candidate-sets/`, `validate_candidate_sets()` walker | V6 framed candidates as briefs (design artifacts, non-executable). We adopted the *set* as the schematized artifact; per-candidate `status: candidate` + `arguments_against` enforced at the set level. The full V6 candidate-brief profile (separate `profile: candidate_brief` schema) is deferred — see below. |
| **Active-EOU trace obligation, enforced** | ECP-0014 (v0.6.0, hard-cut) — `validate_active_trace_obligation()`, no-trace-justification escape with TODO-rejection | V6 made trace mandatory in invariants but did not specify enforcement. We hard-cut the gate at v0.6.0: no warning phase, no migration window. The no-trace-justification mechanism IS the migration path; writing one is the forcing function. |
| **Lifecycle/evidence triangle** | ECPs 0007 + 0009 + 0010 (v0.6.0) — run-trace schema, dependency DAG + maturity-evidence, activation evidence | Three coupled checks that turn lifecycle claims from self-declarations into evidence-bound assertions. Closer to V6's "lifecycle stages are evidence-gated trust states" doctrine than the V6 spec itself, which describes the gates in prose without naming the evidence artifacts. |
| **Engine-as-reference, not snapshot** | ECP-0003 (v0.5.0) — `engine/` canonical, `inherits_from` merge model, override layer | V6 implies this through "L1 Registry and minimal vocabulary" living in one place but doesn't make it operational. We made the engine/app split structural: apps reference engine artifacts, validator refuses weakening merges. This is the V6 idea Codex flagged as missing operationalization. |
| **Owner attestation expiry (partial)** | Bootstrap escape in ECP-0010 — `bootstrap_expires_at` forces re-evaluation | V6 proposed full `owner_attestation` schema with `expires_at`. We absorbed the *expiry-forces-re-evaluation* pattern via the legacy bootstrap escape, not via a separate owner-attestation artifact. Lighter touch; same forcing function for the immediate case (apps migrating to v0.6.0 evidence requirements). Full owner-attestation as a separate artifact remains deferred. |
| **Smallest memorable doctrine form** | Top of `03-doctrine.md` (the 8 imperatives) | Stolen verbatim. "Bound the unit. Expose the judgment. Trace the run. Audit the evidence. Separate authority. Govern change. Prune the portfolio. Discipline the vocabulary." Worth its weight. |
| **D1–D7 organization of doctrine** | `03-doctrine.md` restructured under 7 categories | Re-bucketing, not rewrite. Content preserved; mental model clearer. |
| **Run-vs-Foundry distinction (doctrine)** | `03-doctrine.md` D3.3 | A run is DAG-like; the Foundry over time is a state machine. Doctrine update only — no code reification. See V-12 in `04-vocabulary-principles.md`. |

---

## Deferred (good idea, wrong time)

Each deferred item has a **rot watch** — a condition under which the deferral should be revisited.

| V6 idea | Why deferred | Rot watch |
|---|---|---|
| **Profile-based schema split** (`base.schema.yml` + 4 profiles: candidate-brief, core, governed, meta) | Breaks every existing EOU spec across all consuming apps. The current `function == "generate"` conditional handling does ~80% of what profiles would. | If a third app ships and the `function`-conditional branching in `validate_eou_card()` becomes unwieldy (>200 LOC of branching), the profile split becomes the next major. Codex flagged this explicitly: "function-conditional logic in validator is already a branching monolith." |
| **`simulate` as 12th canonical function** | Currently absorbed inside the ECP pipeline as a phase, not a foundry-wide verb. Under our own P3 vocabulary principle (gates-or-produces), it has structural warrant (produces `simulation_report` consumed by `audit` of ECP package). But pipeline-membership override (P3) lets it stay subordinate to `propose`/`audit` for now. | If we ship a third independent use of simulation outside the ECP pipeline (e.g., simulating a candidate set before audit, or simulating an EOU run before activation), it earns top-level verb status. |
| **L0–L6 layered architecture reification** | Useful mental model; doesn't need code restructure. Our existing 6-layer vocabulary-authority-chain (schemas → validator → skills → codex skills → rules → templates) is a different decomposition but operationally equivalent. | If a contributor (human or AI) consistently confuses what belongs where, the layer model becomes structural documentation. Until then, prose. |
| **`effect_contract` block in core schema** | Codex pressure-tested this: even as additive, it creates silent migration pressure once doctrine says "every executable EOU must produce a governed effect." Existing EOUs become semantically "legacy" even when validator passes. A derived/computed `effect_contract` (synthesized from `outputs` + `classification.function`) sidesteps the issue but requires derivation rules we haven't designed. | If V-12 (run-vs-Foundry) gets reified in code, the same migration carries `effect_contract`. Pair them. |
| **Full F-code extensions (F2c, F3v, F4r, F6r, F12r)** | Most are specializations of existing F-codes. F6 already has structural/coverage subtypes. Premature specialization adds maintenance burden without new diagnostic resolution. | If an incident class repeatedly resists clean F-code assignment, the missing subcode earns its place. Logged as a watchlist; not as a roadmap commitment. |
| **Full owner-attestation as separate artifact** | The ECP-0010 bootstrap escape captures the most-needed property (expiry forces re-evaluation). A separate `owner-attestation.schema.yml` with periodic re-attestation cycles is heavier than current need. | If owner-rot in active EOUs becomes a recurring incident class, this becomes the structural fix. |

---

## Rejected (defensibly, or with compromise)

| V6 idea | Why rejected | Compromise (if any) |
|---|---|---|
| **Term-warrant as governed artifact** (`schemas/term-warrant.schema.yml`, per-term review process) | The V6 audit explicitly warned against "governance artifacts replacing executable units." Adding a term-warrant artifact for every vocabulary change is exactly that pattern. Our existing AGENTS.md vocabulary-authority-chain (6-layer sync rule) is process discipline, which Codex correctly noted is not the same as governance. | **Compromise:** lightweight append-only `foundry/vocabulary/decisions.log.yml` for vocabulary-changing decisions (not yet shipped; lower priority). Costs ~30 LOC; no new artifact governance machinery. |
| **F-code extensions F2c, F10a, F12v** as separate codes | Same premature-specialization argument as the deferred F-codes. | **Compromise:** keep F10a (approval boundary) and F12v (vocabulary drift) as *subcodes* under existing parents, not as separate top-level codes. Mirrors the F6a/F6b pattern. |
| **Replacing 03-doctrine.md wholesale with V6's D1–D7** | Current doctrine is battle-tested against four established frameworks (OntoClean, DDD, ISO 25964, BPMN). V6's organization is cleaner but content is roughly equivalent. | **Compromise:** keep all current content; re-bucket under D1–D7. Done in v0.6.0 doc update. |
| **V6's full schema family** (all V6's schemas at once) | Theory of control, not migration-aware. Adopting whole-cloth would require migrating every app's existing EOU specs to a new shape simultaneously. | **Compromise:** absorb individual schemas as needed (ECP-0013 candidate-set, the existing run-trace, no-trace-justification). Each one is independently shippable; the whole family is not. |

---

## What V6 got right that we did not previously have words for

Worth naming because these are the most valuable absorptions, regardless of whether they shipped as code:

1. **"Output is evidence, not proof."** Our existing doctrine had falsifiable outputs; V6 sharpened the framing. Polished artifacts are evidence under examination, not certification of correctness.

2. **"The Foundry is harder to fool" as the success standard.** Our V2 doctrine had "reduced hidden failure" but V6's framing — *the system catches more of its own false confidence over time* — is the operational test for the standard.

3. **Governed effect as first-class concept.** Even though we deferred the `effect_contract` block, the *concept* — every executable EOU must produce a typed, named, traceable, falsifiable effect attributable to a run — clarifies what `outputs` and `success_criteria` together actually represent.

4. **Anti-self-deception system, not automation system.** From V6's D1: *"V6 is not primarily an automation system. It is an anti-self-deception system."* This is the line that should sit on the wall.

5. **Pipeline-membership override as legitimate naming pressure.** V6's audit of its own pipeline phases (simulate, observe) recognized that pipeline-phase verbs earn names by being required pipeline members, not by independently gating-or-producing. This is the override clause we eventually wrote into P3 of our vocabulary principles.

---

## What V6 got wrong that we did not previously see clearly

These are the failure modes of pure theory-of-control thinking, surfaced by Codex's adversarial review:

1. **"Process discipline isn't governance."** Saying "the rule exists in AGENTS.md and the maintainer follows it" is not the same as a validator that hard-fails when the rule is violated. V6's term-warrant proposal and our AGENTS.md sync rule both pattern this way; both can become hollow.

2. **"Run-time vs spec-time obligations get conflated."** V6's invariants ("every meaningful run produces trace") are run-time obligations; the validator can only check spec-time commitments (does `outputs.trace` declare a path?). Our ECP-0014 makes this distinction explicit: the gate is structural, not runtime. V6 elided it.

3. **"Migration-awareness is a separate competency from architectural correctness."** A clean schema family that requires every existing app to rewrite every EOU spec is not improvement; it is debt transfer. Codex's "no empirical operating base" critique points at this: V6's authors had no shipping apps, so migration cost was invisible to them.

4. **"The audit roundtable's own staged-rollout recommendation got ignored by V6's own authors."** The independent architect explicitly said "approve direction, REJECT full immediate implementation, REQUIRE staged rollout." V5 absorbed this; V6 partially regressed by re-introducing the full schema family. We absorb V5's staged-rollout principle, not V6's full-family ambition.

---

## When to revisit

This log gets re-read when:

- A new app's audit findings name a pattern that maps to a V6 deferred item (e.g., function-conditional branching becomes unmanageable → revisit profile split).
- A V6-aligned external proposal (another parallel design conversation, another LLM's review) lands on the user's desk. The decisions here are not permanent; they are the current calibration.
- An ECP is opened whose target is one of the deferred items. The ECP should cite this log as prior context.

This log is appended to, not overwritten. If we change our mind, we add a new entry dated and tagged; we do not edit the original. The history of "why we said no" is as valuable as the history of "what we shipped."
