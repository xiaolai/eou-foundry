# EOU Design and Maintenance Doctrine

This document is the current practical doctrine for designing, maintaining, and governing EOUs.

## Definition

An **EOU — Executable Operating Unit** — is a bounded operating unit that transforms specified inputs into specified outputs under explicit constraints, validation, authority, and responsibility.

The most important definition:

> An EOU is a testable operating hypothesis, not a prompt, checklist, SOP, or script.

It claims:

```text
Given inputs X,
under context Y,
using procedure Z,
with authority A,
and validation V,
this unit can produce output O
within acceptable risk R.
```

A good EOU is not judged by whether it produces something impressive. It is judged by whether its output is valid, traceable, auditable, and worth the operational cost.

## 1. Core standard

The EOU framework should optimize for:

```text
reduced hidden failure
```

Not merely:

```text
more automation
more output
faster execution
fewer warnings
higher pass rate
less human involvement
```

The strongest EOU systems do not just make work faster. They make it harder for the organization or individual to fool themselves.

A system is improving when it catches more of its own false confidence.

## 2. Mandatory EOU fields

Every serious EOU should contain these fields.

```yaml
eou:
  id: string
  version: string

  classification:
    function: execute | audit | generate | validate | decide | govern | refactor
    target_object: string
    automation_mode: deterministic | LLM_assisted | human_executed | hybrid
    authority_level: suggest_only | draft_only | write_candidate | write_inactive | mutate_active | approve | publish
    risk_level: low | medium | high | critical
    lifecycle_stage: candidate | draft | simulated | pilot | active | stable | deprecated | retired

  purpose:
    statement: string
    non_goals: []

  operating_hypothesis: string

  inputs:
    required: []
    optional: []
    forbidden_assumptions: []

  context_manifest:
    source_of_truth: []
    supporting: []
    forbidden: []

  execution:
    steps: []
    decision_points: []
    stop_conditions: []

  outputs:
    primary: []
    secondary: []
    trace: []

  validation:
    deterministic: []
    judgment: []
    regression: []

  failure_modes:
    known: []
    warning_signs: []

  escalation:
    require_human_when: []

  responsibility:
    executor: string
    reviewer: string
    approver: string
    cannot_delegate: []
```

This is the minimum viable EOU contract. If an EOU lacks purpose, non-goals, authority, stop conditions, validation, trace, and ownership, it is not yet mature.

## 3. Three essential questions

Before creating any EOU, ask three questions.

### What failure does this prevent?

Bad answer:

```text
It makes the process more organized.
```

Good answer:

```text
It prevents a generated chapter from entering export without evidence audit.
```

### What decision does this improve?

Bad answer:

```text
It helps the workflow.
```

Good answer:

```text
It helps decide whether a candidate EOU should be activated, rejected, or merged into an existing EOU.
```

### What hidden judgment does this expose?

Bad answer:

```text
It checks quality.
```

Good answer:

```text
It exposes whether the chapter's apparent reversal is earned by earlier fair clues rather than created by a cheap surprise.
```

If an EOU cannot answer these questions, it should remain a note, not an operating unit.

## 4. EOU creation should be conservative

A new EOU is not a free asset. It creates:

```text
schema burden
maintenance burden
registry burden
validation burden
training burden
audit burden
retirement burden
```

Default rule:

```text
Do not create a new EOU unless needed.
```

Before creating a new EOU, test whether the need can be satisfied by:

```text
a field in an existing EOU
a validation rule
a stop condition
a regression case
a checklist item
a context-manifest update
a human approval gate
a refactor of an existing EOU
```

The Foundry should reward fewer, sharper EOUs, not more, prettier EOUs.

## 5. Separate generation, audit, revision, and approval

Never let one unit do all four.

```text
generate = produce candidate output
audit = detect failures
revise = repair specific failures
approve = accept responsibility
```

Dangerous design:

```text
generate chapter
→ audit chapter
→ revise chapter
→ approve chapter
```

all inside one EOU.

Better design:

```text
compile-chapter
→ audit-chapter
→ revise-chapter-from-audit
→ approve-chapter-for-export
```

The same unit should not approve its own output.

## 6. Generating EOUs need special controls

A generating EOU is dangerous because it can create operational complexity.

It may generate:

```text
candidate EOUs
candidate schemas
candidate regression cases
candidate refactor options
candidate protocols
candidate ECPs
```

It may not generate:

```text
active EOUs
approved EOUs
production schemas
weakened validators
constitution changes
approval records
published output
```

The safe pattern:

```text
generate candidates
→ argue against candidates
→ rank candidates
→ select minimal useful set
→ audit candidate set
→ specify selected EOUs
→ simulate
→ approve
→ activate
```

Every generating EOU should have:

```yaml
generation_budget:
  max_candidates: 7
  must_rank_candidates: true
  must_select_minimal_set: true
  must_include_rejected_candidates: true
  must_include_arguments_against_each_candidate: true
```

Generation without deletion pressure becomes bureaucracy.

## 7. Candidate set audit

Generated EOUs must be audited as a set, not only individually.

A candidate set can fail even if every candidate looks plausible.

Candidate set audit should ask:

```text
Does this set contain too many EOUs?
Are responsibilities overlapping?
Is there at least one audit path?
Is there at least one validation path?
Is approval separated from generation?
Are high-risk decisions human-owned?
Does each unit have a distinct success criterion?
Does each candidate prevent a concrete failure or improve a concrete decision?
Is there a minimal recommended subset?
Are rejected candidates recorded?
```

This protects the Foundry from process inflation.

## 8. Lifecycle discipline

Do not treat all EOUs as equally trustworthy.

Use maturity levels:

```text
L0 — Tacit
L1 — Narrative
L2 — Structured
L3 — Executable
L4 — Auditable
L5 — Governed
L6 — Self-improving
```

Promotion must require evidence.

```text
L3 → L4 requires trace.
L4 → L5 requires registry entry, owner, and regression cases.
L5 → L6 requires ECP history and monitored improvement.
```

An EOU should never self-declare maturity.

## 9. Trace is mandatory

Every meaningful EOU run should produce a trace.

```yaml
run_trace:
  run_id: string
  eou_id: string
  eou_version: string
  status: completed | completed_with_warnings | failed | stopped
  inputs_used: []
  context_loaded: []
  steps_completed: []
  decision_points_triggered: []
  warnings: []
  outputs: []
  validation_results: []
  human_approval:
    required: true | false
    status: pending | approved | rejected | not_required
```

Without trace, failure cannot be diagnosed. Without diagnosis, improvement is fake.

## 10. Three audit layers

A mature EOU system needs three different audits.

### Output audit

Question:

```text
Is the produced artifact valid?
```

### Run audit

Question:

```text
Was the EOU executed correctly?
```

### EOU audit

Question:

```text
Is the EOU itself well designed?
```

Most systems only audit outputs. That is insufficient.

## 11. Failure taxonomy

Every failure should be named.

```text
F1 Input Failure
F2 Context Failure
F3 Schema Failure
F4 Scope Failure
F5 Instruction Failure
F6 Judgment Failure
F7 Validation Failure
F8 Tool Failure
F9 Trace Failure
F10 Responsibility Failure
F11 Lifecycle Failure
F12 Drift Failure
```

Named failures lead to targeted repairs.

```text
F3 Schema Failure → canonicalize schema.
F4 Scope Failure → split, merge, or redefine EOU.
F6 Judgment Failure → add judgment predicates or human audit.
F7 Validation Failure → improve validator and add regression case.
F10 Responsibility Failure → add owner and approval gate.
F12 Drift Failure → reconcile specs, scripts, docs, and validators.
```

## 12. Incidents and regression memory

Every serious failure should become an incident.

```yaml
incident:
  id: inc-0007
  affected_eou: compile-chapter
  failure_class: F12_DRIFT_FAILURE
  summary: >
    Compiler emitted TBD because paired-scene card used `result`
    while compiler expected `learner_result`.
  root_causes:
    - No canonical schema.
    - Compiler and validator expected different fields.
  corrective_actions:
    - Canonicalize paired-scene schema.
    - Add placeholder validation.
    - Add regression case.
```

Then convert it into regression memory.

```yaml
regression_case:
  id: reg-placeholder-output-001
  target_eou: compile-book
  failure_observed: >
    Compiled manuscript contained TBD placeholders while validation passed.
  expected_behavior:
    validator_status: fail
    message_contains:
      - TBD
      - placeholder
```

A failure that does not become memory will return.

## 13. ECPs: controlled change

Any significant change should go through an **EOU Change Proposal**.

Require ECPs when changing:

```text
purpose
schema
validation
stop conditions
authority
risk level
maturity level
promotion rules
constitution
```

No silent mutation.

## 14. Constitution

A recursive Foundry needs a slow-changing constitution.

Core invariants:

```text
No EOU may approve its own change.
No active EOU may lack an owner.
Every active EOU must produce trace.
Every promoted change must pass regression tests.
Validation cannot be weakened without explicit approval.
Failure history cannot be deleted.
Warnings cannot be suppressed to improve apparent performance.
Human owner retains final authority over high-impact changes.
Uncertainty must be exposed, not hidden.
```

The constitution is the boundary against runaway recursion.

## 15. EOU portfolio management

A Foundry should manage the entire EOU portfolio, not just individual EOUs.

Portfolio audit should ask:

```text
How many active EOUs exist?
How many are unused?
How many duplicate each other?
How many lack owners?
How many lack traces?
How many have unresolved incidents?
How many are stuck in candidate or draft status?
How many have not been audited recently?
How many high-risk EOUs lack approval gates?
```

A healthy portfolio has:

```text
low duplication
clear ownership
active retirement
strong validation
few stale units
high trace coverage
known risk distribution
```

## 16. Economic discipline

Each EOU has cost.

Costs include:

```text
creation cost
maintenance cost
cognitive overhead
schema overhead
audit overhead
training cost
false-positive cost
false-negative cost
coordination cost
retirement cost
```

Simple test:

```text
Is the failure this EOU prevents more expensive than the cost of maintaining the EOU?
```

If not, reject or downgrade it.

## 17. Best-practice construction sequence

Use this sequence:

```text
1. Capture messy workflow.
2. Identify desired artifact.
3. Identify hidden judgments.
4. Identify failure modes.
5. Identify decision boundaries.
6. Propose minimal candidate EOUs.
7. Argue against each candidate.
8. Select minimal useful set.
9. Specify selected EOUs.
10. Add schemas and stop conditions.
11. Simulate or pilot.
12. Produce run trace.
13. Audit output, run, and EOU.
14. Record incidents.
15. Add regression cases.
16. Promote, refactor, or retire.
```

Do not jump from messy workflow directly to automation.

## 18. Red flags

An EOU system is unhealthy if:

```text
EOUs are created faster than they are audited.
Many EOUs lack owners.
Validators mostly check field presence.
Warnings do not change behavior.
Generated candidates become active too quickly.
Pass rates increase after validators are weakened.
Few failures become regression cases.
No one retires EOUs.
AI units approve their own outputs.
Trace is missing or ignored.
The system optimizes for less human involvement rather than better decisions.
```

These are signs of false operational maturity.

## 19. Compact doctrine

A strong EOU is:

```text
bounded
owned
falsifiable
traceable
risk-aware
authority-limited
lifecycle-aware
failure-aware
schema-aligned
auditable
retirable
```

A strong EOU system:

```text
separates generation from approval
treats output as evidence, not proof
records trace
names failures
creates regression memory
uses ECPs for change
maintains a constitution
retires stale units
audits the portfolio
optimizes for reduced hidden failure
```

The deepest principle:

> EOUs should not help the system appear more competent. EOUs should help the system become harder to fool.
