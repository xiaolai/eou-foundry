# Executable Operating Units (EOUs)

This document generalizes the workshop beyond book production.

The book workshop is one instance of a broader problem:

```text
messy human workflow
→ structured executable operating units
→ auditable production system
```

An **EOU** is not merely a checklist, prompt, SOP, script, or template. A good EOU is a bounded work unit that can be:

```text
understood
executed
delegated
audited
improved
versioned
partially automated
```

A weak EOU says:

```text
Write a chapter.
```

A strong EOU says:

```text
Given this chapter card, book kernel, fair-clue register, claim type,
evidence burden, metaphor/analogy constraints, and protocol target,
produce a chapter scaffold that satisfies the recognition-reversal contract,
then run audit tests and record unresolved gaps.
```

The core question is not only **how to automate work**. It is:

> How do we translate tacit, messy, non-programmatic human workflows into units that are executable enough to scale, inspectable enough to trust, and flexible enough to remain intelligent?

---

## 1. Central difficulty

Real-world workflows usually look like this:

```text
messy intention
→ tacit judgment
→ partial memory
→ informal examples
→ exceptions
→ taste
→ improvisation
→ undocumented corrections
→ final artifact
```

An EOU needs this:

```text
input
→ context
→ constraints
→ decision rules
→ execution steps
→ outputs
→ validation
→ failure handling
→ revision loop
```

Therefore the central challenge is:

> Human workflows are often result-shaped. EOUs must be process-shaped.

People usually remember the desired end state. They often do not know how to specify the operating logic that reliably produces it.

---

## 2. Difficulty: extracting tacit judgment

Most valuable workflows are not difficult because of visible steps. They are difficult because of hidden judgment.

In the book workshop, the visible step is:

```text
compile chapter
```

The real judgment is:

```text
Is the reversal earned?
Is the clue fair?
Is the metaphor serving the governing mode?
Is the claim overreaching?
Is this prose becoming generic?
Does the chapter change the reader's standard of evidence?
```

These are **judgment predicates**, not ordinary procedural steps.

Strategy:

> Do not begin by writing procedures. Begin by extracting judgment tests.

A serious EOU contains both:

```text
what to do
how to know whether it was done well
```

For the book workshop, this is why the audit system matters more than the compiler.

```text
compiler = produces output
audit system = preserves judgment
```

---

## 3. Difficulty: wrong decomposition

People often divide workflows by visible activity labels:

```text
research
write
edit
publish
```

That is too crude.

EOUs should be divided by **decision boundary**, not by activity label.

Weak decomposition:

```text
Write chapter.
Edit chapter.
Audit chapter.
```

Better decomposition:

```text
Extract main reversal.
Validate fair clue.
Check evidence burden.
Compile chapter scaffold.
Convert scaffold to prose.
Audit chapter contract.
Audit metaphor / analogy use.
Run placeholder and schema validation.
Revise against audit.
```

Principle:

> An EOU boundary should appear where the success criterion changes.

If the success criterion changes, the workflow probably needs a separate EOU.

Example:

```text
Generate prose ≠ verify evidence burden.
```

Writing favors flow. Auditing favors suspicion. Combining them creates self-deception.

---

## 4. Difficulty: confusing output with execution

A polished output does not prove that the workflow was executed correctly.

In EOU design:

```text
final artifact ≠ process validity
```

A generated chapter may look good while violating the engine:

```text
no fair clue
no real reversal
unsupported bold claim
decorative metaphor
generic AI rhetoric
no protocol
```

Strategy:

> Every EOU needs a trace layer.

A trace layer records:

```text
which inputs were used
which rules were applied
which validations passed
which validations failed
which assumptions remain unresolved
which human judgment was required
```

For the book workshop:

```text
chapter card
→ generated scaffold
→ audit report
→ revision log
→ final prose
```

An EOU without trace is merely an output machine.

---

## 5. Difficulty: context packaging

Messy workflows depend on context scattered across memory, documents, conversations, examples, and habits.

An EOU cannot execute well unless it knows what context to load.

Weak EOU:

```text
Compile this chapter.
```

Better EOU:

```text
Before compiling:
1. Load book/kernel.yml.
2. Load book/toc.yml.
3. Load the target chapter card.
4. Load fair-clues.yml.
5. Load analogy-bank.yml if the chapter uses an analogy.
6. Load evidence-standard.yml.
7. Load the relevant protocol card.
```

Strategy:

> Every EOU needs a context manifest.

A context manifest answers:

```text
What must be known before execution?
What must not be assumed?
Which files are source of truth?
Which materials are optional?
Which materials are stale?
```

Without a context manifest, AI agents hallucinate structure, humans rely on memory, and the workflow becomes non-repeatable.

---

## 6. Difficulty: ambiguity and exception handling

Real workflows include cases such as:

```text
What if the evidence is missing?
What if the chapter card is incomplete?
What if the metaphor is powerful but misleading?
What if a bold claim is attractive but unsupported?
What if the workflow produces fluent garbage?
```

Most SOPs fail because they describe only the happy path.

A serious EOU must include:

```text
normal path
warning conditions
failure modes
escalation rules
stop conditions
repair actions
```

Example:

```yaml
EOU: compile-chapter

stop_if:
  - chapter card lacks main_claim
  - fair clue is missing
  - protocol is undefined
  - evidence burden is B but no counterclaim exists

repair:
  - do not draft prose
  - repair chapter card first
  - run audit after repair

escalate_to_human_if:
  - claim is ethically sensitive
  - evidence is contradictory
  - metaphor risks distorting the argument
```

A good EOU should know when **not** to execute.

---

## 7. Difficulty: preserving useful human judgment

The goal is not to remove humans from the process.

The goal is to remove avoidable ambiguity while preserving high-value judgment.

Parts that should be executable:

```text
validate YAML
check required fields
detect unresolved placeholders
compile chapter scaffold
generate audit report
export manuscript
```

Parts that should remain judgment-heavy:

```text
Is this metaphor too strong?
Is the argument original enough?
Is the chapter emotionally honest?
Is the final reversal earned?
Is this claim worth making?
```

Strategy:

> Separate deterministic execution from judgment execution.

Classify EOUs into three types:

```text
Type A: Deterministic EOU
Can be run by script.
Example: validate required fields.

Type B: Judgment EOU
Requires an LLM or human evaluator.
Example: audit whether the reversal is earned.

Type C: Decision EOU
Requires owner responsibility.
Example: decide whether to keep a bold claim.
```

Many systems fail because they pretend Type B and Type C are Type A.

That creates fake automation.

---

## 8. Difficulty: schema drift

Schema drift happens when the workflow's components silently disagree.

Example:

```yaml
# card uses
result:

# compiler expects
learner_result:
```

The validator may still say OK. The output may contain placeholders. The process looks successful while failing.

Strategy:

> Define schemas before scaling EOUs.

For every EOU, define:

```text
input schema
output schema
validation schema
error schema
trace schema
```

For the book workshop, chapter cards, device cards, analogy cards, mirror artifact cards, and protocol scene cards should all depend on canonical schemas.

The compiler, validator, Claude skill, and dev-docs should not each invent their own interpretation.

---

## 9. Difficulty: lifecycle mismatch

A workflow at the architecture stage should not be judged by the same standards as a workflow near publication.

Possible lifecycle stages:

```text
idea
→ architecture
→ scaffold
→ draft
→ audit
→ revision
→ production
→ maintenance
```

Validation must vary by stage.

Weak validator:

```text
Every book must have complete analogies, complete evidence, complete manuscript.
```

Better validator:

```yaml
stage: architecture
required:
  - kernel
  - argument graph
  - rough toc

stage: scaffold
required:
  - chapter cards
  - fair clues
  - protocol cards

stage: draft
required:
  - manuscript chapters
  - no unresolved placeholders
  - audit reports

stage: production
required:
  - citations resolved
  - final export
  - consistency audit
```

Strategy:

> Every EOU must declare its lifecycle stage.

Otherwise validation is either too strict too early or too weak too late.

---

## 10. Difficulty: evaluation is harder than generation

Generating something is now cheap.

Evaluating it remains expensive.

For EOU design:

> The audit layer must be more sophisticated than the generation layer.

A chapter compiler can be simple. A chapter auditor must be sharp.

Priority order:

```text
1. define evidence of success
2. define failure modes
3. define validation
4. only then generate output
```

Do not overinvest in generation while underinvesting in evaluation.

---

## 11. Difficulty: keeping EOUs small enough

An EOU should be executable.

Too large:

```text
Write the book.
```

Still too large:

```text
Develop the whole argument.
```

Better:

```text
Generate one chapter card from one act-level reversal.
Audit one analogy card for mapping and limits.
Compile one chapter scaffold from one chapter card.
Validate one book directory against its lifecycle stage.
```

Heuristics:

```text
If an EOU cannot be tested, it is too large.
If an EOU has more than one primary success criterion, split it.
```

---

## 12. Difficulty: over-programming living work

Not every human workflow should be fully formalized.

Writing, investing, parenting, research, and strategy all contain living judgment.

The danger is bureaucratic automation:

```text
everything becomes a form
everything becomes a checkbox
the process becomes rigid
the operator stops thinking
```

Strategy:

> Program the frame, not the soul.

For the book workshop, program:

```text
chapter contract
claim burden
fair clue tracking
audit requirements
export process
schema validation
```

Do not over-program:

```text
taste
voice
final judgment
which claim matters most
whether a metaphor has force
whether the book feels alive
```

An EOU should constrain the system enough to prevent chaos, but not so much that it kills intelligence.

---

## 13. Difficulty: responsibility ownership

A good EOU must answer:

```text
Who owns the result?
Who can approve it?
Who can override it?
Who is accountable if it fails?
```

This matters especially when AI executes part of the workflow.

The AI can draft. The AI can audit. The AI can suggest.

The human owner must decide:

```text
accept
reject
revise
publish
discard
```

Responsibility field:

```yaml
responsibility:
  executor: "Claude / script / human"
  reviewer: "human owner"
  approver: "human owner"
  cannot_delegate:
    - final claim approval
    - ethical judgment
    - publication decision
    - evidence sufficiency judgment
```

Without this field, automation quietly becomes abdication.

---

## 14. General EOU schema

```yaml
EOU:
  id: string
  name: string
  type: deterministic | judgment | decision | hybrid
  lifecycle_stage: idea | architecture | scaffold | draft | production | maintenance

  purpose:
    one_sentence: string
    non_goal: string

  inputs:
    required: []
    optional: []
    forbidden_assumptions: []

  context_manifest:
    source_of_truth: []
    supporting_materials: []
    stale_or_deprecated: []

  execution:
    steps: []
    decision_points: []
    allowed_tools: []
    prohibited_actions: []

  outputs:
    primary: []
    secondary: []
    trace: []

  success_criteria:
    must_pass: []
    should_pass: []

  validation:
    deterministic_checks: []
    judgment_checks: []
    red_team_checks: []

  failure_modes:
    known_failures: []
    warning_signs: []
    stop_conditions: []
    repair_actions: []

  escalation:
    ask_human_when: []
    require_approval_for: []

  responsibility:
    executor: string
    reviewer: string
    approver: string
    cannot_delegate: []

  versioning:
    version: string
    change_log: []
    supersedes: []
```

---

## 15. EOU ladder

Do not convert a messy workflow directly into executable code.

Use this ladder:

```text
messy workflow
→ narrative description
→ artifact inventory
→ decision map
→ EOU cards
→ schemas
→ validators
→ scripts
→ Claude skills
→ audits
→ versioned operating system
```

Example for the book workshop:

```text
Narrative description:
  I want to write a book from a messy conversation.

Artifact inventory:
  kernel, argument graph, chapter cards, fair clues, analogy bank,
  protocols, manuscript, audits, exports.

Decision map:
  What counts as a valid reversal?
  What counts as fair evidence?
  What counts as metaphor misuse?

EOU cards:
  new-book, compile-chapter, audit-chapter, evidence-audit,
  metaphor-audit, export-book.

Schemas and validators:
  make invalid states impossible or visible.

Scripts and skills:
  make the workflow executable.

Audit and revision:
  preserve judgment.
```

This ladder is safer than jumping straight into automation.

---

## 16. Failure-first design

When designing EOUs, ask:

```text
How will this fail?
How will it look successful while failing?
How will we detect that?
```

For the book workshop, failure modes include:

```text
beautiful but generic prose
unsupported bold claims
decorative metaphors
stale chapter cards
schema mismatch
fake validation
missing fair clue payoff
AI-generated audit that flatters the draft
manuscript export with unresolved placeholders
```

Feature-first design creates bloated systems.

Failure-first design creates robust systems.

---

## 17. Compile / audit / revise separation

Every serious EOU system needs three modes:

```text
compile mode
audit mode
revise mode
```

They should not be merged.

Compile mode:

```text
Goal: produce structured output from structured input.
Risk: fluency hides weakness.
```

Audit mode:

```text
Goal: detect violations, gaps, overreach, missing evidence.
Risk: being too polite.
```

Revise mode:

```text
Goal: repair specific failures without damaging what works.
Risk: fixing locally while breaking global coherence.
```

For AI agents, these should often be different skills or subagents.

The same agent that writes elegantly may audit poorly.

---

## 18. Minimum executable judgment

Not all judgment can be fully automated, but much judgment can be partially operationalized.

Abstract judgment:

```text
This chapter is too generic.
```

Minimum executable judgment:

```text
Check:
- Does the chapter contain one unusual claim?
- Does it use book-specific terminology?
- Does it return to the central artifact?
- Does it avoid banned generic phrases?
- Could this appear in any AI education book?
```

EOUs do not need to eliminate judgment. They need to make judgment inspectable.

---

## 19. Falsifiable outputs

Every EOU output should be falsifiable.

Weak output:

```text
Chapter improved.
```

Better output:

```text
Chapter now passes:
- Fair Clue Test
- Single Reversal Test
- Evidence Burden Test

Still fails:
- Protocol Dramatization Test
```

A falsifiable output can be audited. A non-falsifiable output is just an opinion.

---

## 20. Process evidence

For every EOU run, preserve:

```text
input version
output version
audit result
changes made
open issues
human approval
```

Book-workshop equivalent:

```text
cards/
manuscript/
audits/
exports/
```

Other workflows might use:

```text
requests/
runs/
logs/
artifacts/
reviews/
approvals/
```

If the system cannot reconstruct how the output was produced, the EOU is not mature.

---

## 21. Core principle

The real difficulty is not programming.

The real difficulty is converting human know-how into:

```text
explicit boundaries
explicit inputs
explicit standards
explicit exceptions
explicit responsibility
```

Humans often operate through:

```text
taste
memory
habit
social context
implicit priorities
unspoken examples
```

Therefore EOU design is epistemological, not merely administrative.

The question is not only:

```text
What steps should happen?
```

The deeper question is:

```text
What counts as knowing that this work was done well?
```

---

## 22. Practical conversion sequence

For any messy workflow, use this sequence:

```text
1. Name the desired artifact.
2. Identify the hidden competence required.
3. List what usually goes wrong.
4. Extract the judgment tests.
5. Define the smallest executable unit.
6. Specify input/output schemas.
7. Add validation and failure modes.
8. Add trace and versioning.
9. Separate compile, audit, and revise.
10. Decide what must remain human-owned.
```

Compact form:

```text
artifact
→ hidden judgment
→ failure modes
→ EOU boundaries
→ schemas
→ validators
→ execution
→ audit
→ responsibility
```

This applies beyond books:

```text
writing
investing
research
education
parenting systems
company operations
AI workflows
personal knowledge management
software development
```

The mature goal is not automation for its own sake.

The mature goal is:

> Make valuable human workflows executable enough to scale, inspectable enough to trust, and flexible enough to remain intelligent.
