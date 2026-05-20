---
name: 89-eou-foundry
description: Enforce faceted EOU classification (function + target + automation + authority + risk + lifecycle). Load when designing, auditing, or promoting EOUs in foundry/.
---

# EOU Foundry V2 Rules

**Declare all six EOU classification facets explicitly on every spec under `foundry/`.** Without faceted classification, authority and risk become inferred from a name, and the validator cannot tell a draft suggestion from an active state-changer.

The canonical EOU layer is `foundry/`.

An EOU is an operational hypothesis, not merely a prompt, checklist, SOP, or script.

## Faceted classification requirement

Every EOU must declare all six classification facets:

```text
function:         generate | specify | validate | diagnose | promote | refactor | audit | propose | activate | implement | retire
target_object:    the specific artifact or decision this EOU acts on
automation_mode:  deterministic | LLM_assisted | hybrid | human_executed
authority_level:  suggest_only | draft_only | write_candidate | write_inactive | mutate_active | approve | publish
risk_level:       low | medium | high | critical
lifecycle_stage:  candidate | draft | simulated | pilot | active | monitored | stable | deprecated | retired
```

A compliant label looks like:
> `function: audit, target_object: candidate EOU set, automation_mode: LLM_assisted, authority_level: write_inactive, risk_level: medium, lifecycle_stage: draft`

A non-compliant label looks like:
> `type: audit_eou` — a single label that obscures authority, automation assumptions, and risk.

Do not use a single vague type label to decide authority or risk. Authority and risk must be explicit facets, not inferred from a name.

## Canonical objective

Optimize for: reduced hidden failure, inspectability, truthfulness, schema coherence, traceability, and human responsibility.

Do not optimize for: speed, fluency, fewer warnings, higher apparent pass rate, or number of EOUs created.

When these objectives conflict with execution speed or apparent completeness, the canonical objective takes precedence.

## Function vocabulary

| Value | What it means | Evaluation or execution? |
|-------|--------------|--------------------------|
| `generate` | Produce candidate outputs (EOU specs, regression cases, ECPs, refactor options). Subject to Rule 95 envelope constraints. | execution — produces artifact |
| `specify` | Turn an approved candidate into a schema-conformant EOU spec at draft stage. | execution — produces artifact |
| `validate` | Deterministic structural check: schema conformance, field presence, registry consistency. Produces a validation report; does not repair. | execution — produces artifact |
| `diagnose` | Classify a failure using the F-code taxonomy; recommend minimum-blast-radius repairs. Produces a diagnosis report or no-change record. | execution — produces artifact |
| `promote` | Evaluate an EOU against maturity gates and recommend a lifecycle transition. Does **not** execute any transition. | evaluation — produces recommendation |
| `refactor` | Produce structural refactor options based on audit findings. Does not apply any option. | execution — produces artifact |
| `audit` | Judgment-heavy inspection of an EOU spec, candidate set, or the whole Foundry. Produces an audit report. | execution — produces artifact |
| `propose` | Create a formal ECP from a diagnosed failure or refactor option. | execution — produces artifact |
| `activate` | Execute a lifecycle transition approved by the human owner (typically to `active`). Requires named human approval on record. | execution — state-changing |
| `implement` | Execute an approved ECP: apply changes to the EOU spec or governance artifact, update registry, move ECP to `implemented/`. Requires approved ECP. | execution — state-changing |
| `retire` | Execute retirement of an EOU: set `lifecycle_stage: retired`, document successor or owner decision. Requires named human approval. | execution — state-changing |

`promote`, `audit`, and `validate` are evaluation functions — they inspect and report. All other functions either produce artifacts or change system state.

`activate`, `implement`, and `retire` are the only functions that change lifecycle state or apply structural mutations. They require a prior human-approved governance artifact (recommendation or ECP) on record.

## Activation evidence (ECP-0010)

An EOU at `lifecycle_stage` in `{active, monitored, stable}` MUST have a registry entry whose `activated_by` field is populated:

```yaml
activated_by:
  ecp_id: <ECP that approved this activation>
  approver: <named human identity per rule 91>
  activated_at: <ISO-8601 UTC>
```

OR, for apps that existed before this rule was enforced, a legacy bootstrap record:

```yaml
activated_by:
  legacy_bootstrap: true
  bootstrap_justification: <one-sentence reason; reference to git history is acceptable>
  bootstrap_expires_at: <ISO-8601 UTC; six months from declaration is the suggested maximum>
```

After `bootstrap_expires_at`, the EOU must either acquire proper activation evidence (ECP + approver + activated_at) or be demoted out of the active stages.

## Maturity evidence (ECP-0009)

A registry entry's `maturity` field must be at or above the level required by its `lifecycle_stage`, per `engine/maturity-model.yml`:

| lifecycle_stage | required maturity (minimum) |
|---|---|
| `candidate` | `L1_NARRATIVE` |
| `draft` | `L2_STRUCTURED` |
| `simulated` | `L2_STRUCTURED` |
| `pilot` | `L3_EXECUTABLE` |
| `active` | `L4_AUDITABLE` |
| `monitored` | `L5_GOVERNED` |
| `stable` | `L6_SELF_IMPROVING` |

`deprecated` and `retired` are governance states, not maturity claims; maturity-evidence checks are skipped for them.

A registry entry claiming maturity higher than its evidence supports is a self-declaration without backing. The validator refuses such mismatches.

## Dependency DAG (ECP-0009)

Registry entries may declare inter-EOU dependencies:

```yaml
dependencies:
  eous: [<other-eou-id>, ...]
  schemas: [<schema-file>, ...]
  constitution: true
```

The validator builds the DAG from `dependencies.eous` and refuses cycles or references to retired EOUs.

## Terminology: "generate"

The word "generate" has four distinct uses in the Foundry — do not conflate them:

| Usage | Meaning |
|-------|---------|
| `function: generate` | The EOU classification value. An EOU with this function produces candidate outputs and is subject to Rule 95 constraints (generation envelope, budget, counter-generation). |
| "generating EOU" | Shorthand for any EOU whose `classification.function` is `generate`. |
| "generated spec" | An EOU spec that was produced as a candidate output by a generating EOU. It starts at `lifecycle_stage: candidate`. |
| "generate" as action verb | General-purpose verb meaning "produce" (e.g., "generate a report", "generate the trace"). Not the same as the classification value. |

When writing EOU specs, rules, or skills: use the action verb "produce" instead of "generate" to avoid ambiguity with the `function: generate` classification value.

## Violation indicators

A violation of this rule is present when any of the following are observed:

| Signal | Severity | How to detect | Required action |
|--------|----------|---------------|-----------------|
| One or more of the six classification facets is absent from the spec | critical | Check for presence of `function`, `target_object`, `automation_mode`, `authority_level`, `risk_level`, `lifecycle_stage` | Block promotion; record as `classification_incomplete` |
| A facet value is not in the schema-allowed set (e.g., `function: execute`) | high | Compare against `schemas/eou.schema.yml` valid value lists | Flag in audit; block promotion; correct value before spec proceeds |
| A single type label (e.g. `type: audit_eou`) used instead of explicit facets | high | Detect presence of `type:` key at spec root without corresponding classification block | Flag in audit; replace with explicit facets before spec proceeds |
| `purpose.statement` describes process steps rather than naming a failure prevented or decision improved | medium | Check whether the statement contains "performs", "executes", "runs", "processes" without a corresponding failure or decision noun | Flag as `medium`; require author to rewrite `purpose.statement` before promotion |
| `authority_level` or `blast_radius` is absent on any EOU that writes or mutates files | high | Check file write operations in `execution.steps` against declared `authority_level` | Flag as `high`; block promotion until `authority_level` and `blast_radius` are declared |
