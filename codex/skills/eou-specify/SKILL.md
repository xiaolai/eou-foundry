---
name: eou-specify
description: Convert an approved candidate into a formal EOU spec using Foundry V2 faceted classification and governance constraints.
---

# Specify EOU

Convert or repair `$candidate` into a formal EOU spec.

## Required reading

1. `schemas/eou.schema.yml` — required fields, types, and allowed values
2. `foundry/constitution.yml` — governance invariants the spec must satisfy
3. `foundry/governance.yml` — authority-level definitions and lifecycle rules

## Procedure

**Step 1: Determine mode**

- If `$candidate` resolves to a path with no existing spec file → **CREATE** mode: build a new spec from the candidate data.
- If a spec file already exists at the resolved path → **REPAIR** mode: read the existing spec and fill in missing or invalid fields without changing fields that are already correct.

**Step 2: Load source material**

Read `$candidate` to extract: purpose, operational context, known failure modes, authority level, and blast radius.

**Step 3: Map all required fields**

Populate each group in order:

```
classification:
  function:          # execute | generate | audit | validate | govern
  target_object:     # the artifact or decision this EOU acts on
  automation_mode:   # fully_automated | LLM_assisted | hybrid | human_only
  authority_level:   # read_only | write_candidate | write_inactive | write_active | approve | publish
  risk_level:        # low | medium | high | critical
  lifecycle_stage:   # candidate | draft | pilot | active | deprecated | retired

purpose:
  statement:         # one sentence — what this EOU does
  non_goals:         # explicit list of what it must not do

operating_hypothesis:  # "Given [inputs], this EOU can [action] without [boundary violation]."

inputs:
  required:          # files or data this EOU cannot run without
  optional:          # files that improve output quality if present
  forbidden_assumptions:  # things the EOU must not silently assume

context_manifest:
  source_of_truth:   # canonical files (registry, constitution, schemas)
  supporting:        # reference files (taxonomy, patterns, maturity model)
  forbidden:         # files this EOU must not read or mutate

execution:
  steps:             # ordered, concrete, bounded steps — no "perform bounded operation"
  decision_points:   # named branch conditions with explicit resolution criteria
  stop_conditions:   # observable states that halt execution before completion
  allowed_tools:     # explicit tool list
  prohibited_actions: # explicit prohibitions

outputs:
  primary:           # concrete file path(s) — no placeholder labels
  secondary:         # supplementary artifacts
  trace:             # always: runs/{run_id}/trace.yml

success_criteria:
  must_pass:         # binary, verifiable conditions
  should_pass:       # quality checks that are not hard blockers

validation:
  deterministic:     # machine-checkable: field presence, schema conformance, count limits
  judgment:          # audit-level checks that require human or LLM review
  red_team:          # adversarial scenarios to test boundary robustness

failure_modes:
  known:             # named failure patterns
  warning_signs:     # observable signals that a known failure is occurring
  repair_actions:    # concrete responses to each warning sign

escalation:
  require_human_when:   # observable conditions that mandate human review
  require_approval_for: # actions that cannot proceed without human sign-off

responsibility:
  executor:          # Claude | script | human (pick one primary; hybrid: name the split)
  reviewer:          # who reviews outputs
  approver:          # who approves lifecycle transitions
  cannot_delegate:   # non-delegable authorities

blast_radius:
  allowed_scope:     # directories or files this EOU may write to
  forbidden_scope:   # directories or files this EOU must never touch

versioning:
  supersedes:        # prior EOU IDs replaced by this spec
  changelog:         # list of version entries
```

**Step 4: Validate completeness**

Check every field group is populated. Reject placeholder strings ("target artifact", "What this EOU is meant to do", "Perform bounded operation"). If the source candidate does not contain enough information to fill a field, write `TBD: [specific question]` and list it under `open_questions`.

**Step 5: Set lifecycle and write**

- Set `lifecycle_stage: draft` — never `active`, `approved`, or `pilot` without audit evidence.
- Write the spec to `foundry/eous/{eou_id}.yml` (standard EOU) or `foundry/meta-eous/{eou_id}.yml` (meta/generating EOU).

## Constraints

- Do not set `lifecycle_stage` to `active`, `pilot`, or `approved` without explicit audit and human approval evidence in the file.
- In REPAIR mode, do not change fields that are correctly populated — only fill gaps.
- Generating EOUs (function: generate) require an additional `generation_envelope` section scoped to the specific outputs this EOU produces; do not copy a generic envelope from another EOU.
