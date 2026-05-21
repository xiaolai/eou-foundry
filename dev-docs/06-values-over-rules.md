# Values Over Rules

The EOU Foundry's constitutional value layer. Rules tell the Foundry what to do. Values tell the Foundry **why** the rule exists and **how to act when rules collide**.

A value belongs in this document only if it can decide trade-offs, resist gaming, and protect the system from false maturity. It is not aspirational language; it is interpretation authority for the rules below it.

## Inclusion test

A value belongs only if it answers at least one of:

1. What failure does this value prevent?
2. What rule conflict does this value resolve?
3. What hidden judgment does this value expose?
4. What kind of false success does this value resist?
5. Which architectural invariant does this value protect?
6. Would the Foundry become dangerous if this value were removed?

Speed, elegance, output volume, and automation do not pass this test as constitutional values. They can be local optimizations, but not governing values.

## Core target

The EOU doctrine already states the deepest target: optimize for **reduced hidden failure**, not for more automation, more output, faster execution, higher pass rates, fewer warnings, or less human involvement (see `03-doctrine.md` D1.1).

The value layer is built around one sentence:

> **The Foundry should make the system harder to fool without killing human judgment.**

---

## The value stack

Eight constitutional values, in priority order:

```text
V1  Epistemic integrity
V2  Human responsibility
V3  Inspectable evidence
V4  Bounded authority
V5  Living judgment
V6  Failure memory
V7  Minimality
V8  Semantic integrity
```

These are not slogans. Each one governs rule interpretation.

> **Naming note.** These values are `V1`–`V8`. The vocabulary self-audit in `04-vocabulary-principles.md` uses `V-01`–`V-12` (with hyphen). They are distinct namespaces — visually distinguishable, semantically unrelated.

---

## V1 — Epistemic Integrity

```text
Truth over appearance.
Validity over fluency.
Reality over compliance theater.
```

This is the highest value.

The Foundry must not help a system appear competent while hiding failure. A polished output, a passing validator, or a complete-looking spec is not enough.

**Protects against:**

```text
output worship
validator theater
pass-rate gaming
false maturity
beautiful but invalid artifacts
```

**Operational meaning:** if a rule makes the system look better while making hidden failure harder to detect, the rule is bad.

This value supports the doctrine's distinction between output and execution: a final artifact does not prove process validity, which is why every EOU needs trace (see `03-doctrine.md` D3.1, D4.1).

**Rule interpretation:**

```text
When speed conflicts with truth, choose truth.
When fluency conflicts with evidence, choose evidence.
When pass rate conflicts with failure detection, choose failure detection.
```

---

## V2 — Human Responsibility

```text
Ownership over abdication.
Approval over automation.
Accountability over delegation.
```

The Foundry may delegate execution, drafting, validation, diagnosis, and audit assistance. It must not delegate ultimate responsibility.

The human owner must remain responsible for:

```text
approval
publication
high-impact judgment
constitutional change
authority expansion
validator weakening
lifecycle activation
```

**Protects against:**

```text
self-approval
approval laundering
human responsibility disappearing into process artifacts
AI-generated authority
automation-as-abdication
```

The foundations make this explicit: AI can draft, audit, and suggest, but the human owner must decide whether to accept, reject, revise, publish, or discard.

**Rule interpretation:**

```text
If a rule allows responsibility to become unclear, strengthen ownership.
If a process artifact behaves like approval, reject it unless a human approval record exists.
```

---

## V3 — Inspectable Evidence

```text
Trace over trust.
Evidence over assertion.
Auditability over convenience.
```

Every serious EOU claim must leave evidence.

The Foundry should be able to answer:

```text
What inputs were used?
What context was loaded?
What decision points fired?
What validations passed or failed?
What warnings appeared?
What assumptions remain unresolved?
Who approved the result?
```

**Protects against:**

```text
untraceable execution
non-repeatable workflows
audit gaps
hidden assumptions
unfalsifiable outputs
```

Trace is not decoration. The doctrine says that without trace, failure cannot be diagnosed; without diagnosis, improvement is fake (see `03-doctrine.md` D3.1).

**Rule interpretation:**

```text
If an operation cannot be traced, it should not be trusted.
If a result cannot be audited, it should not be promoted.
If a decision cannot be reconstructed, it should not become precedent.
```

---

## V4 — Bounded Authority

```text
Permission over capability.
Scope over power.
Separation over collapse.
```

The fact that an EOU **can** do something does not mean it is **authorized** to do it.

This value protects the distinction between:

```text
generate  ≠ activate
validate  ≠ repair
audit     ≠ mutate
promote   ≠ change lifecycle state
propose   ≠ implement
approve   ≠ ordinary EOU function
```

The architecture explicitly says generating EOUs may produce candidates but may not create authority, active EOUs, approved EOUs, production schemas, weakened validators, constitution changes, approval records, or published output (see `02-architecture.md` Part 2).

**Protects against:**

```text
authority creep
hidden mutation
generate → activate
audit → implement
validator weakening without ECP
scope expansion by convenience
```

**Rule interpretation:**

```text
When an EOU's capability exceeds its authority, authority wins.
When evaluation and mutation collide, separate them.
When lifecycle change is involved, require approval record.
```

---

## V5 — Living Judgment

```text
Frame over soul.
Structure over chaos.
But judgment over bureaucracy.
```

The Foundry should formalize the **frame** of work, not kill the intelligence inside the work.

**Program:**

```text
schemas
authority boundaries
context manifests
stop conditions
trace requirements
audit requirements
governance pipelines
```

**Do not over-program:**

```text
taste
voice
strategic judgment
which claim matters most
final human discernment
```

The foundation document states this directly: *"Program the frame, not the soul."*

**Protects against:**

```text
SOP fetish
checkbox thinking
bureaucratic automation
over-formalizing creative or strategic work
operator stops thinking
```

**Rule interpretation:**

```text
If a rule prevents chaos without killing judgment, keep it.
If a rule makes the operator stop thinking, revise it.
If formalization destroys the value of the work, reduce the formalization.
```

---

## V6 — Failure Memory

```text
Learn from failure.
Do not merely survive it.
```

A serious failure should not vanish after repair. It should become:

```text
incident
diagnosis
ECP or no-change record
regression case when the failure is repeatable or traces to a validator gap
audit finding
portfolio lesson
```

**Protects against:**

```text
recurring failures
silent non-action
no-change invisibility
same mistake rediscovered
validators never improved after false pass
```

The doctrine says every serious failure should become an incident, and important failures should become regression memory; a failure that does not become memory will return (see `03-doctrine.md` D4.4).

**Rule interpretation:**

```text
If a failure is serious, record it.
If a failure is recurring, create regression memory.
If no change is made, record why.
If a validator falsely passed, improve the validator or record the risk.
```

---

## V7 — Minimality

```text
Necessary structure over impressive structure.
Operational value over bureaucracy.
Fewer sharper EOUs over more prettier EOUs.
```

Every EOU has cost:

```text
creation cost
maintenance cost
cognitive overhead
schema overhead
audit overhead
retirement cost
false-positive cost
false-negative cost
```

The doctrine explicitly warns that a new EOU is not a free asset; it creates maintenance, registry, validation, audit, and retirement burden (see `03-doctrine.md` D2.3, D6.5).

**Protects against:**

```text
process inflation
vocabulary sprawl
over-decomposition
retire-never syndrome
candidate generation without deletion pressure
```

**Rule interpretation:**

Before creating a new EOU, ask whether the need can be met by:

```text
a field
a validator
a stop condition
a regression case
a checklist item
a context update
a human approval gate
a refactor of an existing EOU
```

A new EOU is justified only when it prevents a concrete failure, improves a concrete decision, exposes hidden judgment, or improves traceability enough to exceed its maintenance cost.

---

## V8 — Semantic Integrity

```text
Clear words over convenient vagueness.
Vocabulary as governance.
Meaning before naming.
```

In the Foundry, vocabulary is not cosmetic. It governs what can be validated, delegated, audited, approved, and retired.

This value protects distinctions such as:

```text
noun vs field value
verb vs phase
approval vs recommendation
promotion vs activation
candidate set vs candidate-stage EOU spec
validate vs audit
implement vs propose
```

The vocabulary principles state that nouns are rigid artifacts, verbs are state-changing or artifact-producing acts, field values are not nouns, and terms require warrant before entering the vocabulary (see `04-vocabulary-principles.md` P1–P6).

**Protects against:**

```text
vague verbs
state-as-noun confusion
approval laundering
hidden mutation through language
terms without warrant
ontology sprawl
```

**Rule interpretation:**

```text
If a word hides authority, replace it.
If a term has no warrant, demote it.
If two terms share identity and scope, merge them.
If a lifecycle state is treated as a noun, correct it.
```

---

## Value priority order

When values conflict, apply them in this order:

```text
1. Epistemic integrity
2. Human responsibility
3. Inspectable evidence
4. Bounded authority
5. Living judgment
6. Failure memory
7. Minimality
8. Semantic integrity
```

**Why this order?**

Because the highest danger is not inefficiency. The highest danger is a system that looks valid while becoming harder to question.

### Worked conflict examples

| Conflict | Resolution |
|---|---|
| Minimality vs trace | Trace wins for executable EOUs. |
| Living judgment vs authority | Authority wins when blast radius is high. |
| Semantic integrity vs usability | Usability can simplify surface language, but canonical terms must remain precise. |
| Failure memory vs privacy/security | Do not delete failure memory casually, but sensitive memory may need controlled redaction. |
| Human responsibility vs automation | Human responsibility wins for approval, publication, and high-impact lifecycle decisions. |

---

## The value constitution (machine-readable)

```yaml
foundry_values:
  telos: >
    Make valuable human workflows executable enough to scale,
    inspectable enough to trust,
    and constrained enough to prevent hidden failure
    without destroying human judgment.
  values:
    - id: epistemic_integrity
      priority: 1
      formulation: Truth over appearance.
      protects_against:
        - output_worship
        - validator_theater
        - pass_rate_gaming
        - false_maturity
    - id: human_responsibility
      priority: 2
      formulation: Ownership over abdication.
      protects_against:
        - self_approval
        - approval_laundering
        - automation_as_abdication
    - id: inspectable_evidence
      priority: 3
      formulation: Trace over trust.
      protects_against:
        - untraceable_execution
        - unfalsifiable_outputs
        - audit_gaps
    - id: bounded_authority
      priority: 4
      formulation: Permission over capability.
      protects_against:
        - authority_creep
        - hidden_mutation
        - generate_to_activate
    - id: living_judgment
      priority: 5
      formulation: Program the frame, not the soul.
      protects_against:
        - sop_fetish
        - bureaucratic_automation
        - judgment_extinction
    - id: failure_memory
      priority: 6
      formulation: Failure becomes memory.
      protects_against:
        - recurring_failures
        - no_change_invisibility
        - false_pass_repetition
    - id: minimality
      priority: 7
      formulation: Necessary structure over impressive structure.
      protects_against:
        - process_inflation
        - retire_never_syndrome
        - over_decomposition
    - id: semantic_integrity
      priority: 8
      formulation: Clear words govern clear authority.
      protects_against:
        - vocabulary_sprawl
        - state_noun_confusion
        - vague_verbs
```

---

## What should NOT be constitutional values

These may be useful locally, but they should not outrank the core values:

```text
speed
convenience
output volume
automation rate
lower human involvement
higher pass rate
completeness
elegance
uniformity
novelty
```

**Why not?** Because each can become dangerous:

```text
speed can hide missing judgment
automation can hide abdication
pass rate can hide weak validators
completeness can create bureaucracy
uniformity can kill living judgment
```

These belong as local optimizations within an EOU or a workflow, never as governing constraints over the Foundry as a whole.

---

## Final answer

If "value over rules" stands, the EOU Foundry holds this value hierarchy:

```text
1. Truth over appearance.
2. Responsibility over abdication.
3. Evidence over assertion.
4. Permission over capability.
5. Judgment over bureaucracy.
6. Memory over recurrence.
7. Minimality over process inflation.
8. Semantic clarity over convenient vagueness.
```

The most compressed version:

```text
Make the system harder to fool.
Keep humans responsible.
Make every serious claim inspectable.
Limit authority.
Preserve living judgment.
Turn failure into memory.
Create only what earns its cost.
Use words that governance can enforce.
```
