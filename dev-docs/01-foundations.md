# EOU Foundations

An **EOU — Executable Operating Unit** — is a bounded work unit that can be understood, executed, delegated, audited, improved, and versioned.

A weak EOU says:

```text
Do the analysis.
```

A strong EOU says:

```text
Given the incident report, failure taxonomy, and constitution,
classify the root cause using F-codes, rank repair options by blast radius,
and write a diagnosis report. Do not apply any repair.
```

The core challenge:

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

The visible step might be:

```text
compile chapter
```

The real judgment is:

```text
Is the argument earned?
Is the evidence sufficient?
Is the claim overreaching?
Does this output change the reader's standard of evidence?
```

These are **judgment predicates**, not ordinary procedural steps.

Strategy:

> Do not begin by writing procedures. Begin by extracting judgment tests.

A serious EOU contains both:

```text
what to do
how to know whether it was done well
```

For any EOU system, the audit layer matters more than the compiler. The compiler produces output; the audit layer preserves judgment.

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
Write document.
Edit document.
Audit document.
```

Better decomposition:

```text
Extract main argument.
Validate evidence burden.
Compile scaffold.
Audit contract.
Revise against audit.
```

Principle:

> An EOU boundary should appear where the success criterion changes.

If the success criterion changes, the workflow probably needs a separate EOU.

Writing favors flow. Auditing favors suspicion. Combining them creates self-deception.

---

## 4. Difficulty: confusing output with execution

A polished output does not prove that the workflow was executed correctly.

In EOU design:

```text
final artifact ≠ process validity
```

A generated document may look good while violating its own operating contract.

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

An EOU without trace is merely an output machine.

---

## 5. Difficulty: context packaging

Messy workflows depend on context scattered across memory, documents, conversations, examples, and habits.

An EOU cannot execute well unless it knows what context to load.

Weak EOU:

```text
Diagnose the failure.
```

Better EOU:

```text
Before diagnosing:
1. Load the failure taxonomy.
2. Load the constitution.
3. Load the incident report.
4. Load the EOU spec under diagnosis if available.
```

Strategy:

> Every EOU needs a context manifest.

A context manifest answers:

```text
What must be known before execution?
What must not be assumed?
Which files are source of truth?
Which materials are optional?
Which materials are forbidden?
```

Without a context manifest, AI agents hallucinate structure and the workflow becomes non-repeatable.

---

## 6. Difficulty: ambiguity and exception handling

Real workflows include cases such as:

```text
What if the evidence is missing?
What if the source document is incomplete?
What if the input is ambiguous?
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
execution:
  stop_conditions:
    - Required input file not found.
    - Source document contains no observable failure symptoms.
    - Authority boundary of this EOU would be exceeded.
  escalation:
    require_human_when:
      - Failure involves a constitutional invariant violation.
      - Self-approval risk is detected.
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
compile structured output
generate audit report
```

Parts that should remain judgment-heavy:

```text
Is this argument original enough?
Is this claim worth making?
Is the evidence sufficient?
Should this EOU be retired?
```

Strategy:

> Separate deterministic execution from judgment execution.

Classify automation_mode into:

```text
deterministic:    can be run by script; no LLM judgment needed
LLM_assisted:     requires LLM evaluation; human review recommended
human_executed:   must be performed by a human
hybrid:           deterministic steps and judgment steps explicitly separated
```

Many systems fail because they pretend `LLM_assisted` work is `deterministic`.

---

## 8. Difficulty: schema drift

Schema drift happens when the workflow's components silently disagree.

Example:

```yaml
# EOU spec uses
outputs:
  primary: foundry/audits/incidents/{id}.diagnosis.yml

# consuming skill reads from
foundry/audits/{id}.diagnosis.yml
```

The validator may still say OK. The output goes to the wrong path. The process looks successful while failing.

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

The schema, validator, skill, and docs should not each invent their own interpretation. The v0.5.0 engine-reference split (ECP-0003) makes this enforceable across applications: engine artifacts live canonically at `plugin/engine/`, applications inherit through `inherits_from`, and the validator refuses merges that drop or weaken engine keys.

---

## 9. Difficulty: lifecycle mismatch

A workflow at the draft stage should not be judged by the same standards as an active, governed workflow.

Lifecycle stages:

```text
candidate → draft → simulated → pilot → active → monitored → stable → deprecated → retired
```

Validation must vary by stage.

Strategy:

> Every EOU must declare its lifecycle_stage.

Otherwise validation is either too strict too early or too weak too late. An EOU at `candidate` status has no regression coverage and no audit history; applying `active`-level scrutiny to it wastes effort and generates noise.

---

## 10. Difficulty: evaluation is harder than generation

Generating something is now cheap.

Evaluating it remains expensive.

For EOU design:

> The audit layer must be more sophisticated than the generation layer.

A generator can be simple. An auditor must be sharp.

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
Audit the Foundry.
```

Better:

```text
Audit one EOU spec for faceted classification completeness.
Audit all generating EOUs for envelope safety.
Check registry / spec consistency.
Check ECP discipline for authority changes.
```

Heuristics:

```text
If an EOU cannot be tested, it is too large.
If an EOU has more than one primary success criterion, split it.
```

---

## 12. Difficulty: over-programming living work

Not every human workflow should be fully formalized.

Research, strategy, writing, and judgment-heavy decisions all contain living intelligence.

The danger is bureaucratic automation:

```text
everything becomes a form
everything becomes a checkbox
the process becomes rigid
the operator stops thinking
```

Strategy:

> Program the frame, not the soul.

Program:

```text
schema constraints
authority boundaries
stop conditions
audit requirements
trace requirements
governance pipeline
```

Do not over-program:

```text
taste
voice
final judgment
which claim matters most
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
What cannot be delegated?
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
  executor: Claude
  reviewer: Foundry maintainer
  approver: human owner
  cannot_delegate:
    - final approval to advance spec to active
    - weakening the generation_envelope forbidden_outputs list
```

Without this field, automation quietly becomes abdication.

---

## 14. EOU spec schema (V2, v0.6.0 shape)

```yaml
id: string                   # matches the filename stem
name: string
version: string              # semver; bumps on active EOUs require an ECP

classification:
  function:         generate | specify | validate | diagnose | promote | refactor | audit | propose | activate | implement | retire
  target_object:    string   # what this EOU acts on
  automation_mode:  deterministic | LLM_assisted | human_executed | hybrid
  authority_level:  suggest_only | draft_only | write_candidate | write_inactive | mutate_active | approve | publish
  risk_level:       low | medium | high | critical
  lifecycle_stage:  candidate | draft | simulated | pilot | active | monitored | stable | deprecated | retired

purpose:
  statement: string          # one sentence: what failure it prevents or decision it improves
  non_goals: []

operating_hypothesis: string # "Given X, this EOU can produce Y without risk R"

inputs:
  required: []
  optional: []
  forbidden_assumptions: []

context_manifest:
  source_of_truth: []        # canonical files this EOU reads
  supporting: []             # secondary reference files
  forbidden: []              # files this EOU must not read or mutate

execution:
  steps: []                  # ordered, concrete, bounded — no "perform bounded operation"
  decision_points: []        # named branch conditions with resolution criteria
  stop_conditions: []        # observable states that stop execution before completion
  allowed_tools: []
  prohibited_actions: []

outputs:
  primary: []                # concrete file path(s)
  secondary: []
  trace:
    - foundry/runs/{eou_id}/{run_id}.yml

success_criteria:
  must_pass: []              # binary, verifiable conditions
  should_pass: []            # quality checks that are not hard blockers

validation:
  deterministic: []          # machine-checkable: field presence, schema conformance
  judgment: []               # requires human or LLM review
  red_team: []               # adversarial scenarios to test boundary robustness

failure_modes:
  known: []
  warning_signs: []
  repair_actions: []

escalation:
  require_human_when: []
  require_approval_for: []

responsibility:
  executor: string           # Claude | script | human
  reviewer: string
  approver: string
  cannot_delegate: []

blast_radius:
  allowed_scope: []          # directories or files this EOU may write to
  forbidden_scope: []        # directories or files this EOU must never touch

versioning:
  supersedes: []
  changelog: []
```

The authoritative source is `schemas/eou.schema.yml`. If this document and the schema ever drift, the schema wins.

As of v0.6.0 (ECP-0014), every EOU at `lifecycle_stage` in {active, monitored, stable} must EITHER declare a non-empty `outputs.trace` listing a path under `runs/`, OR have a non-expired `foundry/audits/no-trace/{eou_id}.yml` justification with a named human reviewer. The validator enforces this as a hard error — no warning phase.

---

## 15. EOU progression

Do not convert a messy workflow directly into active automation.

Use this progression:

```text
messy workflow
→ narrative description
→ artifact inventory
→ decision map
→ EOU specs (candidates)
→ schemas
→ validators
→ skills / scripts
→ candidate set audit
→ simulation
→ human approval
→ active governed system
```

This progression is safer than jumping straight into automation.

---

## 16. Failure-first design

When designing EOUs, ask:

```text
How will this fail?
How will it look successful while failing?
How will we detect that?
```

Failure modes include:

```text
beautiful but non-compliant output
unsupported claims
schema mismatch
fake validation passing
missing required fields
AI-generated audit that flatters the output
trace not preserved
```

Feature-first design creates bloated systems.

Failure-first design creates robust systems.

---

## 17. Compile / audit / revise separation

Every serious EOU system needs three modes:

```text
compile / produce mode — produce structured output from structured input
audit mode            — detect violations, gaps, overreach, missing evidence
revise mode           — repair specific failures without damaging what works
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

For AI agents, these should often be different skills or subagents. The same agent that produces output may audit poorly.

---

## 18. Minimum executable judgment

Not all judgment can be fully automated, but much judgment can be partially operationalized.

Abstract judgment:

```text
This EOU is too broad.
```

Minimum executable judgment:

```text
Check:
- Does the EOU have exactly one primary success criterion?
- Does the purpose.statement name a failure prevented or decision improved?
- Does authority_level match what the execution.steps actually do?
- Is blast_radius.allowed_scope consistent with authority_level?
```

EOUs do not need to eliminate judgment. They need to make judgment inspectable.

---

## 19. Falsifiable outputs

Every EOU output should be falsifiable.

Weak output:

```text
EOU improved.
```

Better output:

```text
EOU spec now passes:
- Classification completeness check
- Authority/blast-radius consistency check
- No placeholder strings check

Still fails:
- Regression coverage (no regression cases on file)
```

A falsifiable output can be audited. A non-falsifiable output is just an opinion.

(This is the same concept V6 names *governed effect* — typed, named, traceable, attributable to a run, connected to a target artifact. The current schema captures it through `outputs` + `success_criteria` + `validation.deterministic`; absorbing V6's `effect_contract` as a derived block is tracked in `05-v6-design-pulls.md`.)

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

The canonical trace path is: `foundry/runs/{eou_id}/{run_id}.yml`

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
9. Separate produce, audit, and revise.
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

The mature goal is not automation for its own sake.

The mature goal is:

> Make valuable human workflows executable enough to scale, inspectable enough to trust, and flexible enough to remain intelligent.
