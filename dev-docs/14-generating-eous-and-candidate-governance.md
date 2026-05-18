# Generating EOUs and Candidate Governance

This document records the canonical correction to generating EOUs in Foundry V2.2.

## Core correction

`generate` is a **function facet**, not a complete EOU type.

A unit that generates candidate EOUs, regression cases, refactor options, schemas, or protocols must still declare:

```yaml
classification:
  function: generate
  target_object: candidate_eou_specs
  automation_mode: LLM_assisted
  authority_level: write_candidate
  risk_level: medium
  lifecycle_stage: draft
```

The `function` says what the unit does. The `authority_level` says what it is allowed to change. The `risk_level` says how dangerous failure is. The `lifecycle_stage` says how much trust the system should place in it.

Do not collapse those dimensions into a single label.

## Foundational rule

Generating EOUs may produce **candidates**. They may not create authority.

They may create:

```text
candidate EOU specs
candidate schemas
candidate regression cases
candidate refactor options
candidate protocols
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

The safe path is:

```text
generate candidates
→ argue against them
→ rank candidates
→ select the minimal useful set
→ audit the candidate set
→ specify selected EOUs
→ simulate
→ approve
→ activate
```

Never:

```text
generate → activate
```

## Generation envelope

Every generating EOU must declare a generation envelope.

```yaml
generation_envelope:
  allowed_outputs:
    - candidate_eou_spec
    - candidate_regression_case
    - candidate_refactor_option
    - candidate_schema
    - candidate_protocol
  forbidden_outputs:
    - active_eou
    - approved_eou
    - production_schema
    - validator_weakening
    - constitution_change
    - human_approval_record
  max_candidates: 7
  default_status: candidate
  required_for_each_candidate:
    - purpose
    - non_goals
    - success_criterion
    - failure_modes
    - operational_value
    - authority_level
    - risk_level
    - owner_requirement
    - activation_requirements
```

The envelope prevents a generating unit from becoming an uncontrolled procedure factory.

## Generation budget

Generation must be budgeted.

```yaml
generation_budget:
  max_candidates: 7
  max_new_schemas: 2
  max_new_validators: 3
  max_open_questions: 10
  must_rank_candidates: true
  must_select_minimal_set: true
  must_include_rejected_candidates: true
  must_include_arguments_against_each_candidate: true
```

Without a budget, generating EOUs tend to overproduce because structure is cheap to generate.

## Registry diff

Before proposing a new EOU, the generating unit must compare against the registry.

```yaml
registry_diff:
  required: true
  questions:
    - Does this duplicate an existing EOU?
    - Does it extend an existing EOU?
    - Should this be a refactor instead of a new EOU?
    - Should this be a regression case instead of a new EOU?
    - Should this be a stop condition or validator instead of a new EOU?
```

New EOUs should be the last resort.

## Minimality test

Before accepting a generated EOU candidate, ask whether the need can be satisfied by:

```text
a rule
a schema field
a validator
a regression case
a stop condition
a checklist inside an existing EOU
a human approval gate
```

A new EOU is justified only when it has a distinct success criterion and prevents a concrete failure or improves a concrete decision.

## Operational value test

A generated candidate must explain its operational value.

```yaml
operational_value:
  prevents_failure:
    failure_class: F7_VALIDATION_FAILURE
    concrete_example: Validator passed while manuscript contained TBD.
  improves_decision:
    decision: Whether a chapter may enter export.
    previous_problem: Approval was implicit.
  exposes_hidden_judgment:
    judgment: Whether a fair clue is genuinely fair.
    previous_problem: Twist could appear without clue.
  improves_traceability:
    trace_added: Activation requirements and owner requirement.
```

Reject candidates that cannot identify a prevented failure, improved decision, exposed judgment, or improved trace.

## Counter-generation

Every candidate should include an argument against itself.

```yaml
counter_generation:
  required: true
  for_each_candidate:
    - arguments_for
    - arguments_against
    - reason_to_reject
    - minimality_result
```

The Foundry should generate against itself. This is the main protection against process inflation.

## Candidate set audit

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

## Example: book-workflow candidate set

For the messy workflow:

```text
Turn a long discussion about a nonfiction book into a programmable book project.
```

A good minimal candidate set is:

```text
extract-book-kernel
generate-chapter-cards
compile-chapter-scaffold
audit-chapter
validate-book
approve-chapter-for-export
```

Optional candidates:

```text
metaphor-audit
analogy-audit
fair-clue-audit
device-audit
```

Rejected candidates:

```text
auto-approve-chapter
generate-all-prose
publish-without-human-review
```

## Example: investment-research candidate set

For the messy workflow:

```text
Research a public company before investing.
```

A minimal candidate set might be:

```text
extract-investment-thesis
audit-thesis-assumptions
decision-record-investment
```

Optional candidates:

```text
generate-disconfirming-tests
evaluate-downside-scenarios
postmortem-investment-decision
```

Because investment is high-stakes, the system must add constraints:

```text
generated investment EOUs may not recommend trades
position sizing cannot be delegated
decision records require a human owner
evidence gaps must be explicit
outputs are decision support, not financial advice
```

## Canonical invariant

```text
Generate candidates.
Argue against them.
Rank them.
Keep the minimal useful set.
Audit the set.
Specify selected units.
Simulate.
Approve.
Only then activate.
```

The Foundry should reward fewer, sharper, more inspectable EOUs that prevent real failures and improve real decisions.
