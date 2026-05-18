# Executable Operating Unit System

A2B Engine V2.2 treats the workshop itself as a set of **Executable Operating Units** (EOUs).

An EOU is a bounded work unit that can be understood, executed, delegated, audited, improved, versioned, and partially automated.

The key distinction:

```text
messy workflow = result-shaped
EOU = process-shaped
```

A mature EOU specifies:

```text
purpose
inputs
context manifest
execution steps
decision points
outputs
success criteria
validation
failure modes
stop conditions
repair actions
responsibility ownership
versioning
```

## EOU types

```text
deterministic — scripts can execute and validate it
judgment      — an LLM or human must evaluate quality
owner_decision — the human owner must decide and approve
hybrid        — mixed deterministic and judgment work
```

## Design rule

Do not convert a messy workflow directly into automation. Convert it through this ladder:

```text
messy workflow
→ narrative description
→ artifact inventory
→ decision map
→ EOU card
→ schema
→ validator
→ script / skill
→ audit
→ versioned operating system
```

## Boundary rule

An EOU boundary should appear where the success criterion changes.

Examples:

```text
compile chapter ≠ audit chapter
validate schema ≠ judge prose quality
generate analogy ≠ audit analogy limits
```

## Trace rule

Every EOU should preserve enough trace to answer:

```text
What inputs were used?
Which constraints were applied?
What failed validation?
What human judgment remains?
Who owns approval?
```

## Relation to the book engine

The book workshop argues that polished artifacts are weak evidence unless process, residue, transfer, verification, and responsibility are visible. The workshop must follow the same rule: every generated artifact must be tied to the operating unit that produced and audited it.


## Foundry V2 correction

The canonical EOU governance system is now `foundry/` with faceted classification and recursive governance.

Do not treat `generating` as a single peer type. Generation is a function that must be constrained by authority level, risk level, lifecycle stage, generation envelope, budget, registry-diff check, minimality test, operational-value test, and counter-generation.

See `foundry/engine/eou-foundry-v2.md` and `dev-docs/13-eou-foundry-v2-redesign.md`.
