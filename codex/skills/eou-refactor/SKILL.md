---
name: eou-refactor
description: Generate candidate EOU refactor options from an audit or incident. Does not apply changes directly.
---

# Refactor EOU

Generate candidate refactor options for `$target`. Do not apply any change.

## Required reading

1. `foundry/refactoring-patterns.yml` — canonical refactor types (split, merge, scope-reduction, authority-downgrade, etc.)
2. `foundry/constitution.yml` — invariants that constrain any proposed change
3. The source EOU spec (infer path from `$target` if an audit path is given)

## Procedure

1. Read `$target` (EOU ID or audit report). If it is an audit report, extract the EOU ID and load the corresponding spec.
2. Identify the structural problems: scope creep, authority inflation, weak validation, missing stop conditions, steps that are not bounded operations, etc.
3. For each structural problem, generate one or more refactor options using the patterns in `foundry/refactoring-patterns.yml`.
4. Include a "no change" baseline option with its trade-offs stated.
5. Rank options by: smallest blast radius, then lowest authority required, then easiest rollback.
6. For each option that touches authority, approval, or constitutional invariants: mark `requires_ecp: true`.
7. Write the candidate refactor set.

## Output

Write to `foundry/self-evolution/refactor-options/{eou_id}-refactor-{YYYYMMDD}.yml`.

Each option must include:

```yaml
option_id:
target_failure:       # the structural problem this addresses
proposed_change:      # one specific modification (not a vague direction)
expected_benefit:     # observable improvement
risk:                 # what can degrade
affected_files:       # list of files that would change
tests_required:       # regression cases to add or update
rollback_plan:        # how to revert
arguments_against:    # strongest case for not doing this
requires_ecp:         # true | false
```

## ECP trigger criteria

Mark `requires_ecp: true` when the option does any of the following:
- changes `authority_level`
- modifies `blast_radius.forbidden_scope`
- weakens or removes a validator or stop condition
- changes responsibility or approval authority
- modifies any constitutional invariant

## Constraints

- Do not apply any refactor option. Write candidate set only.
- Always include the "no change" baseline as an option.
- The recommended minimal set must exclude options with unresolved open risks.
