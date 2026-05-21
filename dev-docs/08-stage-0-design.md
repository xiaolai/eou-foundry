# Stage 0 Design — Reference-Grounded Workflow Capture (Proposal)

A forward-looking design proposal that emerged from a Stage 0 design conversation. **Not adopted doctrine.** The core claim: the foundry's current pipeline assumes the user can articulate a workflow, hidden judgments, failure modes, and decision boundaries before `$generate-eou-candidates` runs (`03-doctrine.md` D2.4 steps 1–5). For most real users in unfamiliar domains, this assumption fails. Stage 0 is the pre-pipeline phase that synthesizes those inputs from what users can always provide: a goal, structured reference works, constraints, and explicit user contributions.

This document captures the design so a future reader can review and ECP the proposal without re-litigating the design discussion. The downstream implication of this work — that well-defined domain values enable agentic judgment — is captured separately in `07-agentic-judgment-proposal.md`.

## Origin

This emerged from a design conversation triggered by the observation that the existing foundry skeleton assumes domain literacy users typically lack. The original example was video/cinema, but the design was generalized to any craft domain (cinema, code, music, writing, cooking, therapy, teaching, investing) before being captured here.

The first draft of Stage 0 (a four-skill chain: `$domain-research` → `$domain-orient` → `$reference-deconstruct` → `$preference-elicit`) was rejected on constitutional grounds — it violated V7 (minimality), V8 (semantic integrity, by inventing top-level verbs without warrant), and strained V1/V2/V5. The current proposal is the rework that survived re-inspection against `06-values-over-rules.md`.

## The problem

Per `03-doctrine.md` D2.4, the construction sequence for any EOU set begins:

```text
1. Capture messy workflow.
2. Identify desired artifact.
3. Identify hidden judgments.
4. Identify failure modes.
5. Identify decision boundaries.
6. Propose minimal candidate EOUs.   ← $generate-eou-candidates begins here
```

Step 6 (`$generate-eou-candidates`) requires steps 1–5 as input. For users who already work in a domain, those inputs are tacit and can be elicited by conversation. For users entering an unfamiliar craft, steps 1–5 cannot be produced from inside their current knowledge. The foundry has no mechanism to bridge the gap.

The visible failure: literacy-gap users either (a) abandon the foundry because they cannot start, or (b) produce shallow workflows that bake their ignorance into the resulting EOU set. The hidden failure: even domain experts often have not articulated their constitutional layer (which values govern when rules conflict), so their produced EOUs lack the soul of their craft. Stage 0 addresses both.

## The core claim

What the user can always provide (universal across craft domains):

1. **A goal as outcome category** — "I want to make/build/produce X"
2. **Reference works they react to** — concrete artifacts in the domain
3. **Negative reactions** — works they reject (often easier than positive picks)
4. **Constraints** — audience, scale, budget, time, risk tolerance, desired effect

What Stage 0 synthesizes from those inputs:

1. A captured workflow (D2.4 step 1)
2. An artifact target (step 2)
3. Hidden judgments (step 3)
4. Failure modes (step 4)
5. Decision boundaries (step 5)
6. A `domain_values` block — the constitutional layer governing how the above resolve under conflict

Items 1–5 are what D2.4 already names. Item 6 is the addition: a per-app analog of `06-values-over-rules.md` that turns the captured_workflow from a rule bag into a constitutional artifact.

## Universal input shape

```yaml
user_goal: string                       # outcome category
reference_set:                          # 5 role slots, each with justification
  aspirational:                         # what user wants to make
    - {ref, why}
  anti_reference:                       # similar surface, wrong soul
    - {ref, why}
  boundary_case:                        # edge of the field
    - {ref, why}
  mainstream_baseline:                  # median of the field
    - {ref, why}
  outlier:                              # "I dislike this but it succeeds" — mandatory
    - {ref, why}
constraints:                            # audience, scale, budget, time, risk, desired_effect
  audience: ...
  scale: ...
  budget: ...
  time: ...
  risk_tolerance: ...
  desired_effect: ...
negative_constraints:                   # what user rejects explicitly
  - ...
user_contributed_references:            # >= 1 per role slot — V2 enforcement
  aspirational: [...]
  anti_reference: [...]
  boundary_case: [...]
  mainstream_baseline: [...]
  outlier: [...]
```

The 5-role reference structure is universal mechanism, not domain content. Per the V5 (Living Judgment) discipline, each role slot prompts judgment — slot-as-judgment-prompt, not slot-as-form-field. The mandatory outlier slot ("I dislike this but it succeeds") is the V1 (Epistemic Integrity) defense against encoding the user's blind spots as policy.

## Universal output shape — captured_workflow.yml

```yaml
id: cw-{slug}
schema_version: 1
created_at: ISO timestamp
inputs:
  goal: <user_goal>
  reference_set: {...}
  constraints: {...}
  negative_constraints: [...]
  user_contributed_references: {...}

artifact_target:
  description: <what the app will produce, derived from references>
  scale: <quantity, frequency, etc.>

captured_workflow:
  prose: <synthesized operating logic>
  steps: [...]                          # may be empty or sketched at this stage

hidden_judgments:                       # extracted via counterfactual deconstruction
  - id: hj-{slug}
    predicate: <"Is X earned?" / "Does Y meet the threshold defined in constraints?">
    governed_by_value: <value_id>       # forward reference into domain_values
    surfaced_from: [<reference_ids>]

failure_modes:                          # extracted via negative-space analysis
  - id: fm-{slug}
    failure: <description>
    value_violated: <value_id>
    surfaced_from: [<reference_ids or anti_references>]

decision_boundaries:                    # comparative analysis across references
  - id: db-{slug}
    decision: <"X vs Y">
    governed_by_value: <value_id>

domain_values:                          # the constitutional layer
  - id: dv-{slug}
    formulation: "<X over Y>"           # contested form; Y must be real
    priority: <int>                     # total order, no ties
    canonical_or_personal:
      - field_canonical | user_personal | user_diverges_from_canonical
    justification_if_diverges: required when user_diverges_from_canonical
    protects_against: [<failure_mode_ids>]
    decides_when:
      - conflict: "<rule A> vs <rule B>"
        resolution: <which side this value picks>
    inclusion_test_passes:              # from 06-values-over-rules.md
      prevents_domain_failure: bool
      resolves_rule_conflict: bool
      exposes_hidden_judgment: bool
      resists_false_success: bool
      protects_invariant: bool
      removal_makes_practice_dangerous: bool

confidence:                             # per-section, mirroring run_trace shape
  artifact_target: low | medium | high
  hidden_judgments: low | medium | high
  failure_modes: low | medium | high
  decision_boundaries: low | medium | high
  domain_values: low | medium | high

unstructured_notes:                     # escape hatch for things the schema didn't capture
  string

human_approval:                         # multiple gates
  reference_set_approved_by: <user>
  constraints_approved_by: <user>
  domain_values_approved_by: <user>
  bundle_approved_by: <user>
  approved_at: ISO timestamp
```

The artifact remains at `lifecycle_stage: candidate` permanently — captured_workflows are never promoted higher. Failures attribute back via incident records; the artifact can be superseded by a new version but is never claimed to be "active" or "stable."

## The mechanism (universal transform)

The skill operates on the input shape and performs five universal operations to produce the output shape:

| Operation | Yields |
|-----------|--------|
| Counterfactual deconstruction of references ("what choices did the maker face? what judgments resolved them?") | Hidden judgments |
| Negative-space analysis ("what would have killed this? what almost did?") | Failure modes |
| Comparative analysis across the reference set | Decision boundaries |
| Convergence onto a target shape | Artifact target |
| Synthesis of operating logic implied by the above | Captured workflow prose |
| Pattern detection across reference choices ("what trade-off did references repeatedly resolve the same way?") | Candidate domain values |

All operations are mechanism. None contain domain assertions. Same skill, any domain.

## Universality across domains (eight test domains)

| Domain | Goal | References | Captured workflow output | Top domain value |
|--------|------|------------|--------------------------|------------------|
| Video | "make YouTube videos" | 5 channels | 8–15 min pieces; X pacing, Y structure | Story over spectacle |
| Code | "build a SaaS backend" | 5 codebases | Service-per-context; RPC + queues | Correctness over speed |
| Music | "compose ambient" | 5 albums | Long-form; X tonal palette, Y density | Feeling over technique |
| Writing | "write nonfiction essays" | 5 essayists | Single-claim; X cadence, Y register | Truth over fluency |
| Cooking | "open a small restaurant" | 5 menus + chefs | 30-cover seasonal; X sourcing | Ingredient over technique |
| Therapy | "structure my coaching" | 5 case studies | Session arc; X intake, Y rupture-repair | Autonomy over insight |
| Teaching | "teach my discipline online" | 5 courses | Cohort-based; X session shape | Understanding over coverage |
| Investing | "manage personal portfolio" | 5 letters/strategies | Concentrated long; X risk gates | Preservation over growth |

Same input shape, same output shape, no domain logic in the skill itself. The skill is mechanism; captured_workflow holds all domain content.

## V-discipline mapping

| Foundry value | How Stage 0 honors it |
|---------------|------------------------|
| V1 Epistemic Integrity | `domain_values` formulations must be contested-form ("X over Y" with real Y); counterfactual swap audit; outlier reference slot mandatory to break blind spots; `confidence_per_section` honestly low for unfalsifiable inputs |
| V2 Human Responsibility | Multiple separate approval gates (reference_set, constraints, domain_values, bundle); user_contributed_references mandatory per slot; user must mark and justify any `user_diverges_from_canonical` value |
| V3 Inspectable Evidence | Every value invocation traces back to reference_ids that surfaced it; every domain value links to the failure modes it protects against |
| V4 Bounded Authority | The skill is `function: generate` at `authority_level: write_candidate`; produces inputs to step 6, never EOU candidates directly; `forbidden_outputs` explicitly blocks `eou_candidate` |
| V5 Living Judgment | Schema slots are judgment prompts (per-slot `why` field required); no slot can be filled without surfacing reasoning; domain values surface the soul, freeing rule-layer to be precise |
| V6 Failure Memory | captured_workflow can be referenced by incidents as partial cause; failed captures become regression cases for the skill itself |
| V7 Minimality | One new noun (captured_workflow), one new skill (or input-mode extension); no new functions, authority_levels, or lifecycle_stages |
| V8 Semantic Integrity | No new top-level verbs; `function: generate` already covers the case; new noun goes through warrant test (P6) via ECP |

## Architecture

```text
user goal
  └─ $generate-captured-workflow-from-references
       │  inputs: goal, reference_set (5 roles + justifications), constraints,
       │          negative_constraints, user_contributed_references (≥1 per role)
       │  outputs: foundry/captured-workflows/{slug}.yml
       │
       └─ human approval (multiple gates)
            │
            └─ $generate-eou-candidates
                 │  inputs (extended): existing inputs + captured_workflow.yml
                 │  reads: domain_values for arguments_against scoring
                 │
                 └─ $audit-candidate-eou-set
                      │  reads: domain_values for set-level audit (does the
                      │         recommended subset collectively serve the
                      │         priority-ordered values?)
                      │
                      └─ $eou-specify → $eou-audit → $eou-promote → activated
```

Apps that skip Stage 0 continue to work unchanged. The captured_workflow is an optional input to `$generate-eou-candidates`.

## Anti-theater protections

| Theater risk | Mitigation |
|--------------|------------|
| Strawman opposing values | Schema validation rejects formulations where Y is straw; field practitioners must demonstrably choose Y |
| Fabricated canonical practitioners | Reference list is user-curated; skill never invents references not provided by the user or starter-pack |
| Citation theater | URLs/sources resolve; recency window declared; sunset date on time-sensitive claims |
| Slot-filling without thought | Each role slot requires `why`; values require `inclusion_test_passes` with concrete bool per test |
| Blind-spot encoding | Outlier slot mandatory; `canonical_or_personal` marker forces conscious choice on divergence from field consensus |
| Decoration values | Counterfactual swap audit (also documented in `07-agentic-judgment-proposal.md`) — if changing value priority order doesn't change downstream candidate selection, values were decorative |
| Rubber-stamp approval | Multiple separate approval gates per section, not single bundle approval |

## What this proposal does NOT cover

- **Agentic judgment.** EOUs invoking values to resolve rule conflicts. See `07-agentic-judgment-proposal.md` (deferred until this proposal is adopted and the value layer survives empirical counterfactual-swap testing).
- **Curriculum / teaching.** Stage 0 does not teach domain vocabulary. If the user is so unfamiliar with their field that they cannot pick references, the skill returns `operational_value_test: fails` and recommends external learning. The foundry is not an LMS.
- **Field-specific starter packs.** Whether to ship pre-curated reference suggestions per domain (in `engine/starter-packs/{domain}.yml`) is an open question — see Open Questions below.
- **Multi-app reuse of captured_workflows.** Each app has its own captured_workflow. Cross-app value patterns may emerge but are out of scope.

## Six-layer sync impact

Per `AGENTS.md`'s vocabulary authority chain:

| Layer | Change |
|-------|--------|
| `schemas/eou.schema.yml` | No `VALID_FUNCTIONS` change (uses `generate`). New `target_object` value `captured_workflow` documented as governed-noun cross-reference. |
| `schemas/captured-workflow.schema.yml` | NEW — full structure including `domain_values` section |
| `scripts/validate_foundry.py` | New `validate_captured_workflows()` walker; checks structural shape, `inclusion_test_passes` bools, "X over Y" form, priority totality, user-contribution mandatory |
| `skills/generate-captured-workflow-from-references/SKILL.md` | NEW — mechanism-only |
| `codex/skills/generate-captured-workflow-from-references/SKILL.md` | NEW — mirror |
| `rules/` | One new rule: "Domain values govern domain rule conflicts; downstream skills must consult `domain_values` when present." Rule number TBD by next available slot. |
| `engine/meta-eous/generate-captured-workflow-from-references.yml` | NEW — meta-EOU spec |
| `engine/meta-eous/generate-eou-candidates.yml` | Modified — accepts optional `captured_workflow_input` |
| `engine/meta-eous/audit-candidate-eou-set.yml` | Modified — reads `domain_values` for set-level audit when captured_workflow present |
| `tests/fixture-foundry/foundry/captured-workflows/` | New directory with .gitkeep |
| Templates | Possibly new `templates/captured-workflow-template/` (deferred decision) |
| AGENTS.md skill-selection table | New row for the skill |
| CHANGELOG | Next minor version entry |

This is a substantial sync surface. The proposal is best implemented as a coordinated ECP package, not a single ECP.

## ECP package shape

| ECP | Scope | Status |
|-----|-------|--------|
| ECP-0015 | Add `captured_workflow` to noun catalog; add `schemas/captured-workflow.schema.yml`; add `validate_captured_workflows()` walker; canonical path `foundry/captured-workflows/{slug}.yml` | DRAFTED |
| ECP-0016 | Add `$generate-captured-workflow-from-references` skill + meta-EOU; or, alternatively, extend `$generate-eou-candidates` to accept reference_set input (one of two paths must be chosen) | NOT YET DRAFTED |
| ECP-0017 | Rule governing how downstream skills consume `domain_values`; updates to `$generate-eou-candidates`, `$audit-candidate-eou-set`, `$eou-audit` meta-EOUs | NOT YET DRAFTED |

The agentic-judgment ECP package (likely 3–4 more ECPs) remains deferred per `07-agentic-judgment-proposal.md`.

## Open questions

These must be answered before ECP-0016 can be drafted.

| Question | Current leaning | Why |
|----------|----------------|-----|
| Separate skill or mode of `$generate-eou-candidates`? | **Separate skill** | D5.1 separation of judgment kinds — taste extraction from references is structurally different from candidate proposal. Counter-generation argument required before ECP-0016. |
| Reference-set roles in schema or in skill prose? | **Schema** | Roles are universal mechanism, not domain content. Enforceable. Smaller V5 risk than prose because schema requires `why` per slot. |
| Starter packs ship or not? | **Opt-in only** | New directory `engine/starter-packs/{domain}.yml`. Loaded only when user requests. Maintenance burden bounded; users without starter packs still work. |
| Single human approval point or multiple? | **Multiple** | Reference_set, constraints, and domain_values each separately approved. Constitutional choice (domain_values) deserves separate attention from input gathering. |
| `risk_level` for captured_workflow? | **`medium`** | Below `high` because individual mistakes don't cause direct harm; above `low` because errors propagate into every downstream EOU. Audit cadence: per major captured_workflow version. |

Each leaning can flip with a counter-argument. The counter-generation argument required in ECP-0016 will force the first question to be resolved.

## Smallest validating step

Hand-draft a `captured_workflow.yml` for one domain — cooking is the recommended canary because trade-offs are tangible and immediate. Run two tests:

1. **Inclusion test** on each value in the `domain_values` block. Does each value answer ≥1 of the six inclusion questions from `06-values-over-rules.md`?
2. **Counterfactual swap.** Reorder priority of two values. Identify ≥3 downstream EOU decisions that WOULD flip. If none flip, values were decoration.

The canary is checked into `dev-docs/canary/cooking-restaurant-captured-workflow.yml` as a paired artifact. If the canary passes both tests, ECP-0015 is the next action. If it fails, the schema design needs revision before any ECP work.

## Status

**Proposed, not adopted.** ECP-0015 drafts the schema-and-walker subset. ECP-0016 and ECP-0017 are deferred pending counter-generation resolution and downstream-impact analysis. The agentic-judgment downstream implication (`07-agentic-judgment-proposal.md`) is doubly deferred.

When ECP-0015 lands, revisit this document with the empirical evidence from the first real captured_workflow produced. Update Open Questions with the answers that emerged in implementation.

## Cross-references

- `01-foundations.md` — central difficulty: messy intention → process shape (Stage 0 directly addresses this for literacy-gap users)
- `03-doctrine.md` D2.4 — 16-step construction sequence (Stage 0 synthesizes inputs to step 6)
- `04-vocabulary-principles.md` P6 — warrant test for the new `captured_workflow` noun
- `06-values-over-rules.md` — pattern for the inclusion test and value-layer discipline that the per-app `domain_values` block mirrors
- `07-agentic-judgment-proposal.md` — downstream implication (agentic EOUs become possible once domain values are well-defined)
- `schemas/eou.schema.yml` — `VALID_FUNCTIONS` (no change needed; Stage 0 uses `generate`)
- `schemas/candidate-set.schema.yml` — ECP-0013's pattern for adding a new governed noun (the model this proposal follows)
