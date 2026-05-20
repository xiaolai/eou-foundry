---
name: eou-refactor
description: |
  Generate candidate EOU refactor options (split, merge, scope-reduction, authority-downgrade, step-extraction, validator-addition, stop-condition-injection, responsibility-separation) from an audit finding or incident. Produces options only; applying any option requires an ECP through $ecp-propose.
  <example>
  Context: An audit flagged that one EOU conflates two distinct judgments. Owner wants refactor options before opening an ECP.
  user: "$eou-refactor foundry/audits/eou-audits/audit-foundry.audit.yml"
  assistant: "I'll generate refactor options from the canonical patterns in foundry/refactoring-patterns.yml, weighing blast radius and constitutional fit, then write options under foundry/self-evolution/refactor-options/."
  </example>
  <example>
  Context: User asks for a specific refactor of an EOU with too-broad authority.
  user: "$eou-refactor eou-promote"
  assistant: "I'll generate options including authority-downgrade variants. None are applied; downstream $ecp-propose converts a chosen option into a proper change proposal."
  </example>
argument-hint: EOU_ID_OR_AUDIT_PATH
arguments:
  - target
allowed-tools:
  - Read
  - Write
  - Grep
---

# Refactor EOU

Generate candidate refactor options for `$target`. Do not apply any change.

## Inputs

- `$target` (required) — either an EOU ID (resolved to `foundry/eous/{id}.yml` or `foundry/meta-eous/{id}.yml`) or a path to an audit report or diagnosis file. When an audit path is given, the EOU ID is extracted from the report.

## Required reading

1. `foundry/refactoring-patterns.yml` — canonical refactor types (split, merge, scope-reduction, authority-downgrade, step-extraction, validator-addition, stop-condition-injection, responsibility-separation)
2. `foundry/constitution.yml` — invariants that constrain any proposed change
3. `foundry/governance.yml` — authority boundaries and lifecycle-gate rules; required because refactor options can touch authority_level and blast_radius
4. The source EOU spec (infer path from `$target` if an audit path is given)

## Stop conditions

Halt and report before generating options if:
- `$target` does not identify an EOU ID and one cannot be inferred.
- No audit report or incident exists to identify a structural problem — do not generate options from speculation.
- The EOU spec does not exist in `foundry/eous/` or `foundry/meta-eous/`.

## Procedure

1. Read `$target` (EOU ID or audit report). If it is an audit report, extract the EOU ID and load the corresponding spec.
2. Identify the structural problems: scope creep, authority inflation, weak validation, missing stop conditions, unbounded steps, ambiguous responsibility, missing trace preservation, blast-radius overreach, and circular EOU dependencies.
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

## Scope Note

**Upstream:** receives an EOU id or audit-findings path. Typically invoked when `$eou-audit` flags a structural issue (overlap, conflated judgment, authority creep).

**Downstream:** produces refactor options (split, merge, scope-reduction, authority-downgrade, etc.) at `foundry/self-evolution/refactor-options/`. A chosen option then feeds `$ecp-propose` — refactor itself never applies changes.

**Related:** `$eou-diagnose` (sibling — F-code classification path); `$ecp-propose` (downstream consumer).

**Pipeline:** `eou-audit (fail) → eou-refactor → ecp-propose → simulate → audit → human approval → implement`
