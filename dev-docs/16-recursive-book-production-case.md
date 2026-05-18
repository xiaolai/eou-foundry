# Recursive Book Production Case

This document records the upgraded plan for using the EOU Foundry to produce the book about the EOU Foundry.

## Correct framing

The recursive case is not proof that the Foundry is universally correct. It is a governed demonstration and evidence source under one demanding knowledge-work use case.

Bad claim:

```text
The Foundry generated the book; therefore the Foundry works.
```

Correct claim:

```text
The Foundry generated and governed the Book-Production EOUs used to help produce the book. The process created traces, audits, incidents, regression cases, ECPs, and human decision records that can be inspected.
```

## Recursion boundary

```text
Human / Constitution
→ EOU Foundry
→ Book-Production EOUs
→ book artifacts
→ reader-facing book
```

The Foundry may generate candidates, audit, diagnose, and propose improvements. It may not activate generated units, approve chapters, publish the book, or claim universal proof.

## Required case artifacts

The governed case lives in:

```text
case-studies/recursive-book-production/
```

Key files:

```text
case-protocol.yml
book-production-constitution.yml
candidate-eou-set.v0.1.yml
candidate-set-audit.v0.1.yml
control-comparison.yml
economic-ledger.yml
portfolio-audit.yml
process-evidence-distillation-rules.yml
negative-evidence.md
non-book-transfer-case-investment-research.yml
human-decision-record.example.yml
```

## What the case must show

- Generated Book-Production EOUs default to candidate status.
- Candidate-set audit rejects, merges, or modifies at least one candidate.
- At least one serious failure becomes an incident.
- At least one incident becomes a regression case.
- At least one ECP improves or proposes to improve an EOU.
- Human approval gates are preserved.
- The reader-facing case includes limitations and negative evidence.

## The book-production EOU set

The minimal recommended set includes:

```text
generate-book-kernel
audit-book-kernel
generate-book-production-eou-set
audit-candidate-eou-set
specify-selected-book-production-eous
generate-book-architecture
audit-book-architecture
generate-chapter-cards
audit-chapter-card-set
draft-chapter-from-card
audit-chapter
revise-chapter-from-audit
record-human-decision
approve-chapter-for-export
export-manuscript
distill-process-evidence-for-book
```

The case also includes rejected candidates such as:

```text
auto-approve-chapter
generate-all-prose
publish-without-human-review
recursive-proof-generator
```

## Controls

The recursive case should be compared against weak baselines:

```text
prompt-only book production
checklist-only book production
Foundry-governed book production
```

The Foundry should not be judged primarily by prose beauty or speed. It should be judged by traceability, hidden-failure detection, governance, and human decision clarity.

## Economic discipline

The recursive case must track overhead:

```text
EOUs generated
EOUs rejected
EOUs activated
audits run
human approvals
incidents
regression cases
ECPs
revision cycles
maintenance burden
```

The key question is whether each operating unit prevents a failure or improves a decision worth more than its maintenance cost.

## Transfer case

The recursive book case must not be the only domain. The current transfer example is investment research, with strict boundaries: EOUs may support analysis but may not make investment decisions or remove human responsibility.

## Reader-facing distillation

Reader-facing case material must include:

```text
one failure
one rejected candidate
one audit disagreement or required revision
one human decision
one limitation
one before/after improvement
```

Do not dump raw YAML into the book. Distill process evidence into transferable lessons.
