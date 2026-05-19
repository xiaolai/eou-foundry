# EOU Contract

Every EOU spec must conform to **`schemas/eou.schema.yml`** (v2). This document
is the prose explanation of that schema. The schema file is authoritative; if
the two ever drift, the schema wins.

## Faceted classification (mandatory)

An EOU is **not** classified by a single type label. Every EOU declares six
facets, each drawn from a fixed vocabulary:

```yaml
classification:
  function:         generate | specify | validate | diagnose | promote | refactor | audit | propose | activate | implement | retire
  target_object:    string   # what this EOU operates on, e.g. "chapter card"
  automation_mode:  deterministic | LLM_assisted | human_executed | hybrid
  authority_level:  suggest_only | draft_only | write_candidate | write_inactive | mutate_active | approve | publish
  risk_level:       low | medium | high | critical
  lifecycle_stage:  candidate | draft | simulated | pilot | active | monitored | stable | deprecated | retired
```

No single facet decides authority or risk on its own. The combination does.

## Required top-level fields

```yaml
id: string                     # matches the filename stem
name: string
version: string                # semver-ish; bumps require an ECP for active EOUs
classification: { ... }        # see above
purpose:
  statement: string            # one sentence, what this EOU is for
  non_goals: []                # what it is explicitly NOT for
operating_hypothesis: string   # "Given X, this EOU should produce Y within risk R"
inputs:
  required: []
  optional: []
  forbidden_assumptions: []
context_manifest:
  source_of_truth: []          # the canonical artifacts this EOU reads
  supporting: []               # secondary context
  forbidden: []                # what must NOT be used as context
execution:
  steps: []
  decision_points: []
  stop_conditions: []
  allowed_tools: []
  prohibited_actions: []
outputs:
  primary: []
  secondary: []
  trace: []                    # what records this run produces for later audit
success_criteria:
  must_pass: []
  should_pass: []
validation:
  deterministic: []            # scripts, validators, type checks
  judgment: []                 # human or LLM-judged tests
  red_team: []                 # adversarial checks
failure_modes:
  known: []
  warning_signs: []
  repair_actions: []
escalation:
  require_human_when: []
  require_approval_for: []
responsibility:
  executor: string
  reviewer: string
  approver: string
  cannot_delegate: []
versioning:
  supersedes: []
  changelog: []
blast_radius:
  allowed_scope: []
  forbidden_scope: []
```

## Generating EOUs — extra requirements

EOUs whose `classification.function == "generate"` are proposal-producing units.
They must additionally declare:

```yaml
generation_envelope:
  allowed_outputs: []          # MUST NOT include "active_eou", "approved_eou",
  forbidden_outputs: []        # "constitution_change", or "validator_weakening"
  max_candidates: int
  default_status: candidate    # MUST be "candidate"
  required_for_each_candidate: []
generation_budget:
  max_candidates: int          # <= generation_envelope.max_candidates
  ...
registry_diff:
  required: true
minimality_test: { ... }
operational_value_test: { ... }
counter_generation:
  required: true
```

Generating EOUs MUST have `authority_level` in
`{suggest_only, draft_only, write_candidate, write_inactive}`. They MAY NOT
hold `approve`, `publish`, or `mutate_active`.

## Path conventions inside an EOU spec

Paths inside an EOU spec are **app-root-relative** by default. The consuming
application's tree is the root: `foundry/`, `scripts/`, and any
application-specific top-level directories.

Where an application has a per-instance object scope (e.g., a workshop's
books), the spec may declare a placeholder. For book-workshop:

```yaml
path_root:
  app: "<app-root>"          # repo-relative inside the consuming app
  BOOK_PATH: "books/{book_id}/"   # workshop-specific instance scope
  description: "BOOK_PATH is workshop-specific; other apps may declare
    different placeholders. Fully qualified paths inside app scope are
    app-root-relative."
```

Plugin-relative paths (`engine/`, `schemas/`, `rules/`) are read from the
installed plugin, never duplicated into the app tree.

## Invariants (from the schema)

- Generated operating units default to candidate status.
- Generating EOUs may not activate, approve, publish, or weaken validators.
- Each EOU must declare owner/reviewer/approver and non-delegable decisions.
- High-risk and critical units require human approval.

## Test of a valid EOU

A valid EOU must be small enough to be tested. If it has more than one
primary success criterion, split it.

## Validation

`scripts/validate_foundry.py` enforces the schema against every file under
`foundry/eous/` and `foundry/meta-eous/`, plus the registry, ECPs, and
regression cases. If you change this contract, update the schema first, then
update or retire affected EOUs. Significant changes require an ECP (see
`92-ecp` rule and `governance.yml`).

## Superseded shape (do not use)

Earlier drafts used a single `type` field (`deterministic | judgment |
owner_decision | hybrid`) and a different lifecycle vocabulary (`idea |
architecture | scaffold | draft | audit | revision | production |
maintenance`). Both have been replaced by the faceted classification above.
Any spec still using the old shape is invalid and must be migrated before it
can be promoted past `candidate`.
