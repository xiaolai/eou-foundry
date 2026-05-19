# EOU Foundry Architecture

This document describes the canonical architecture of the EOU Foundry: the faceted classification model, the governance pipeline, and the generating-EOU safety design.

---

## Part 1 — Faceted classification

### Core correction from V1

The original design treated EOU type as a single flat label: `deterministic`, `judgment`, `decision`, `generating`. That was too crude. A single label collapses four independent axes — what the unit does, how it runs, how much authority it has, and how mature it is — into one, making it impossible to express nuance like "a judgment-mode audit with limited authority at the draft stage."

The V2 model uses **faceted classification**:

```yaml
classification:
  function:         generate | specify | validate | diagnose | promote | refactor | audit | propose
  target_object:    string   # what this EOU acts on
  automation_mode:  deterministic | LLM_assisted | human_executed | hybrid
  authority_level:  suggest_only | draft_only | write_candidate | write_inactive | mutate_active | approve | publish
  risk_level:       low | medium | high | critical
  lifecycle_stage:  candidate | draft | simulated | pilot | active | monitored | stable | deprecated | retired
```

No single facet decides authority or risk on its own. The combination does.

A compliant label looks like:

```text
function: audit
target_object: candidate EOU set
automation_mode: LLM_assisted
authority_level: write_inactive
risk_level: medium
lifecycle_stage: draft
```

A non-compliant label looks like:

```text
type: audit_eou
```

Do not use a single vague type label. Authority and risk must be explicit facets, not inferred from a name.

### Core principle

An EOU is an operational hypothesis:

```text
Given inputs X,
context Y,
procedure Z,
and validation tests T,
this unit can produce output O
within acceptable risk R.
```

The Foundry manages those hypotheses.

### Function vocabulary

| Value | Meaning |
|-------|---------|
| `generate` | Produces candidate outputs (EOU specs, regression cases, ECPs, refactor options). Subject to Rule 95 generation-envelope constraints. |
| `specify` | Turns an approved candidate into a complete, schema-conformant EOU spec at draft stage. |
| `validate` | Checks structural integrity of schemas, registry, and specs. Produces a validation report; does not repair. |
| `diagnose` | Classifies a failure using the F-code taxonomy and recommends minimum-blast-radius repairs. |
| `promote` | Evaluates an EOU against maturity gates and recommends a lifecycle transition. |
| `refactor` | Produces structural refactor options for an EOU based on audit findings. |
| `audit` | Inspects and evaluates an EOU spec, candidate set, or the whole Foundry for quality and compliance. |
| `propose` | Creates a formal EOU Change Proposal from a diagnosed failure or refactor option. |
| `activate` | Executes an approved lifecycle transition (typically to `active`). Requires human-approved recommendation on record. State-changing — does not evaluate. |
| `implement` | Executes an approved ECP: applies changes, updates the EOU spec and registry, moves ECP to `implemented/`. Requires approved ECP. State-changing. |
| `retire` | Executes retirement of an EOU: sets `lifecycle_stage: retired`, documents successor or owner decision. Requires human approval. State-changing. |

```mermaid
flowchart TD
    WF["messy workflow"] -->|generate| CAND["candidate set"]
    CAND -->|audit| SEL["selected candidates"]
    SEL -->|specify| SPEC["EOU spec"]
    SPEC -->|audit| AR["audit findings"]
    SPEC -->|validate| VR["validation report"]
    SPEC -->|promote| REC["lifecycle recommendation"]
    REC -->|activate| ACTIVE["EOU spec\nlifecycle_stage: active"]
    REC -->|retire| RET["EOU spec\nlifecycle_stage: retired"]
    AR -->|diagnose| DIAG["diagnosis + F-code"]
    DIAG -->|propose| ECP["ECP"]
    DIAG -->|refactor| RO["refactor options"]
    ECP -->|implement| SPEC
    RO -->|specify| SPEC
```

### Authority level vocabulary

| Level | What it permits |
|-------|----------------|
| `suggest_only` | Read and report; no writes |
| `draft_only` | Write draft artifacts in scratch space only |
| `write_candidate` | Write candidate artifacts to candidate directories |
| `write_inactive` | Write to non-active governance files (audits, validation reports) |
| `mutate_active` | Modify active EOU specs or governance files — requires ECP |
| `approve` | Set approval status — requires named human approver |
| `publish` | Publish or deploy — requires named human approver |

Generating EOUs must not hold `mutate_active`, `approve`, or `publish`.

```mermaid
graph LR
    subgraph gen_safe["Safe for generating EOUs"]
        A["suggest_only"] --> B["draft_only"]
        B --> C["write_candidate"]
        C --> D["write_inactive"]
    end
    D --> E["mutate_active"]
    subgraph human_req["Requires named human approver"]
        F["approve"]
        G["publish"]
    end
    E --> F
    F --> G
```

### Canonical file structure

```text
schemas/
  eou.schema.yml
  ecp.schema.yml
  incident.schema.yml
  regression-case.schema.yml
  audit-report.schema.yml
  registry-entry.schema.yml
  run-trace.schema.yml
  constitution.schema.yml

foundry/
  constitution.yml
  registry.yml
  governance.yml
  maturity-model.yml
  failure-taxonomy.yml
  refactoring-patterns.yml
  runtime-contract.yml
  eous/                          # standard EOU specs
  meta-eous/                     # generating / governing EOU specs
  self-evolution/
    ecp/
      proposed/
      implemented/
    regression/
      cases/
    refactor-options/
  audits/
    eou-audits/
    foundry-audits/
    incidents/
    validation/

runs/                            # execution traces
```

```mermaid
graph LR
    SCH["schemas/ — ground truth"] --> VAL["validate_foundry.py"]
    SCH --> RUL["rules/"]
    SCH --> TMP["templates/meta-eous/"]
    VAL --> SKI["skills/ — Claude"]
    SKI --> COD["codex/skills/ — Codex mirror"]
```

### Canonical anti-patterns

Reject:

```text
generate → activate            (bypasses governance pipeline)
self-approval                  (same executor approves own output)
schema drift                   (specs, validators, docs disagree)
process inflation              (more EOUs than failures prevented)
validator weakening without ECP
new EOUs without evidence of need
high pass rate as proxy for quality
```

Accept:

```text
generate → argue against → rank → minimal subset → audit → specify → simulate → approve → activate
```

The Foundry is successful only if it becomes better at detecting and correcting its own false confidence.

---

## Part 2 — Generating EOU governance

### `generate` is a function facet, not a complete type

A unit that generates candidate EOUs, regression cases, refactor options, or ECPs must still declare all six facets. The `function` says what the unit does. The `authority_level` says what it is allowed to change. The `risk_level` says how dangerous failure is. The `lifecycle_stage` says how much trust the system places in it.

Do not collapse those dimensions into a single label.

### Foundational rule

Generating EOUs may produce **candidates**. They may not create authority.

They may create:

```text
candidate EOU specs
candidate schemas
candidate regression cases
candidate refactor options
candidate ECPs
```

They may not create:

```text
active EOUs
approved EOUs
production schemas
weakened validators
constitution changes
human approval records
published output
```

The safe path:

```text
generate candidates
→ argue against them
→ rank candidates
→ select the minimal useful set
→ audit the candidate set
→ specify selected EOUs
→ simulate
→ human approval
→ activate
```

Never: `generate → activate`

```mermaid
flowchart LR
    GEN["generate candidates"] --> ARG["argue against\ncounter_generation"]
    ARG --> RANK["rank by blast radius"]
    RANK --> MIN["select minimal set"]
    MIN --> ACAS["audit-candidate-eou-set"]
    ACAS --> CHK{set passes?}
    CHK -->|yes| SPE["eou-specify\ncandidate → draft"]
    CHK -->|revise| GEN
    SPE --> SIMS[simulate]
    SIMS --> APP[human approval]
    APP --> ACT(["activate\nlifecycle_stage: active"])
    GEN -. FORBIDDEN .-> ACT
```

### Generation envelope

Every generating EOU must declare a generation envelope:

```yaml
generation_envelope:
  allowed_outputs:
    - candidate_eou_spec
    - candidate_regression_case
    - candidate_refactor_option
    - candidate_ecp
  forbidden_outputs:
    - active_eou
    - approved_eou
    - constitution_change
    - validator_weakening_without_ecp
  max_candidates: 7            # constitution-authorized ceiling
  default_status: candidate    # must be "candidate"
  required_for_each_candidate:
    - arguments_against
    - minimality_result
    - classification.authority_level
    - classification.risk_level
```

The envelope prevents a generating unit from becoming an uncontrolled procedure factory.

### Generation budget

Generation must be budgeted:

```yaml
generation_budget:
  max_candidates: 7            # per-run planned upper bound; <= envelope.max_candidates
  max_new_schemas: 2
  max_new_validators: 3
  max_open_questions: 10
  must_rank_candidates: true
  must_select_minimal_set: true
```

Without a budget, generating EOUs overproduce because structure is cheap to generate.

### Registry diff

Before proposing a new EOU, the generating unit must compare against the registry:

```yaml
registry_diff:
  required: true
  questions:
    - Does this duplicate an existing EOU?
    - Does it extend an existing EOU that should be refactored instead?
    - Should this be a regression case or stop condition rather than a new EOU?
```

New EOUs should be the last resort.

### Minimality test

Before accepting a generated EOU candidate, ask whether the need can be satisfied by:

```text
a rule
a schema field
a validator
a regression case
a stop condition
a checklist item inside an existing EOU
a human approval gate
```

A new EOU is justified only when it has a distinct success criterion and prevents a concrete failure or improves a concrete decision.

### Operational value test

A generated candidate must explain its operational value. Reject candidates that cannot identify at least one of:

```text
prevents_failure      — names a specific failure class and concrete example
improves_decision     — names the decision and the previous problem
exposes_hidden_judgment — names the judgment and why it was hidden
improves_traceability — names what trace is now captured that was not before
```

### Counter-generation

Every candidate must include an argument against itself:

```yaml
counter_generation:
  required: true
  requires_for_each_candidate:
    - arguments_against
    - minimality_result
```

The Foundry should generate against itself. This is the main protection against process inflation.

### Candidate set audit

A generated candidate set must be audited as a system, not only as individual units.

A candidate set can fail when:

```text
there are too many EOUs
responsibilities overlap
there is no audit path
there is no validation path
there is no approval gate
high-risk decisions are delegated to AI
no trace unit exists
generated units are not ranked by value
```

A candidate-set audit asks:

```text
Does the set contain the minimum viable operating system?
Does each unit have one distinct success criterion?
Are generation, audit, revision, validation, and approval separated?
Are high-risk decisions human-owned?
Does the set include traceability?
Are rejected candidates recorded?
Is there a recommended minimal subset?
```

---

## Part 3 — Recursive self-improvement

The Foundry can inspect and improve its own EOUs, but only through bounded governance.

### Required change pipeline

```text
observe failure or audit finding
→ diagnose (assign F-code, rank repair options)
→ propose ECP
→ simulate (populate ECP simulation field)
→ regression test (add regression case)
→ audit (produce audit.yml)
→ human approval (named human sets approval.status: approved)
→ deploy (move ECP to implemented/)
→ registry update
```

No step may be skipped. Each step produces a traceable artifact.

```mermaid
flowchart TD
    OBS["observe — failure or audit finding"] --> DIA["diagnose — F-code + ranked repairs"]
    DIA --> OUT{outcome}
    OUT -->|change warranted| PRO[propose ECP]
    OUT -->|no change| NOC["write no-change record\n.no-change.yml"]
    PRO --> SIM["simulate — populate ECP simulation field"]
    SIM --> REG["regression test — add regression case"]
    REG --> AUD["audit — produce audit.yml"]
    AUD --> APP["human approval\napproval.status: approved"]
    APP --> DEP["implement — apply ECP, move to implemented/"]
    DEP --> UPD[registry update]
    UPD --> DONE([done])
    NOC --> DONE
```

### Forbidden shortcuts

```text
observe → edit EOU spec directly
observe → edit → approve (self)
audit → deploy (skipping ECP and human approval)
```

No EOU may be the sole judge of changes to itself. The EOU that proposes a change and the EOU that audits it must have different `responsibility.executor` values.

### No-change outcome

Not every diagnosis leads to a change proposal. When diagnosis finds insufficient evidence for an EOU change, record a no-change decision:

```text
foundry/audits/incidents/{incident_id}.no-change.yml
```

Required fields: `incident_id`, `eou_id`, `diagnosis_summary`, `decision: no_change`, `rationale`, `reviewed_by`, `reviewed_at`, `reopen_condition`.
