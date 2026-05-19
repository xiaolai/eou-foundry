---
name: 91-foundry-constitution
description: Require reading foundry/constitution.yml, governance.yml, and failure-taxonomy.yml before changing EOU behavior, authority, validation, or promotion rules. Constitution changes need explicit human review.
---

# Foundry Constitution Rule

Before changing EOU behavior, validation, authority, or promotion rules, read:

- `foundry/constitution.yml` (app declaration + any strengthenings)
- The plugin's `engine/constitution-defaults.yml` (engine defaults the app inherits)
- The plugin's `engine/governance.yml` (engine separation-of-powers, authority levels)
- The plugin's `engine/failure-taxonomy.yml` (canonical failure classes)

If the app's constitution declares `inherits_from`, the engine defaults are merged
into the app's constitution at validation time. An app's constitution may *add* to
or *strengthen* engine invariants, but it cannot weaken or remove them — the
validator refuses such merges per rule 91 below.

## inherits_from convention (plugin v0.5.0+)

An app's `foundry/constitution.yml` may declare:

```yaml
inherits_from: eou-foundry@>=0.5.0
application:
  id: <app-id>
  description: <one-line>
  owner: <named human>
invariants_additional: []
forbidden_additional: []
generation_invariants_additional: []
```

Engine-default fields (`purpose`, `optimize_for`, `do_not_optimize_for_alone`,
`invariants`, `forbidden`, `generation_invariants`, `change_rules`) need not be
restated. The validator merges engine defaults first, then this file on top.

A pre-v0.5.0-style constitution that lists all 7 engine-default fields locally
still validates (legacy support); it is the app author's responsibility to keep
those local entries consistent with engine defaults until migration.

## What counts as a constitutional change

A change is constitutional if it does any of the following:
- Modifies an invariant in `foundry/constitution.yml` itself
- Changes the definition of an authority level (`suggest_only`, `draft_only`, `write_candidate`, `write_inactive`, `mutate_active`, `approve`, `publish`)
- Removes or weakens a validation gate that currently blocks promotion or activation
- Changes who may approve a lifecycle transition (e.g., allowing a generating EOU to approve its own outputs)
- Adds or removes a class in `foundry/failure-taxonomy.yml`

A change is **not** constitutional if it only modifies a single EOU's steps, inputs, or outputs without touching governance definitions, authority levels, or promotion rules — that is an ordinary ECP.

## What "explicit human review" means

A constitutional change requires:
1. A changelog entry in `foundry/constitution.yml` (or the file being changed) naming the human reviewer.
2. A signed-off ECP (`approval.status: approved`, `approval.approver` set to a named human identity, not a role label like "human owner").
3. A rollback plan documented in the ECP.

"Explicitly reviewed" means these three artifacts exist and are consistent. A comment in a PR description does not satisfy this requirement unless it is also recorded in the ECP.

## Constitutional invariants cannot be silently weakened

"Silently weakened" means: the invariant is removed, narrowed, or made conditional without a constitutional change ECP. Examples:
- Adding `|| skip_if_no_trace` to a required-trace check
- Removing a field from `required_for_each_candidate` without a version bump and ECP
- Changing `require_human_when` from a populated list to an empty list on a high-risk EOU without an ECP

A change that goes through the ECP process with human approval is an explicit weakening and is permitted if justified. A change made directly to the spec or governance file without an ECP is a silent weakening and is prohibited.

## Constitutional changes cannot be performed by an ordinary EOU

No EOU with `function: generate | audit | validate | diagnose | promote | refactor | specify | activate | implement | retire` may modify `foundry/constitution.yml` as part of its normal execution. Only an EOU with `function: propose` and `authority_level: approve` may draft such a change, and it still requires human approval.

## Violation indicators

A violation of this rule is present when any of the following is observed:

| Signal | Violation | Severity | Required action |
|--------|-----------|----------|-----------------|
| `foundry/constitution.yml` was modified without a changelog entry naming a human reviewer | Silent constitutional change | critical | Revert modification; add changelog entry with named reviewer; open a constitutional ECP before re-applying |
| A constitutional change ECP has `approval.status: approved` but `approval.approver` is a role label (e.g., "human owner") rather than a named identity | Invalid approval evidence | critical | Invalidate ECP; require a named human to re-approve with their identity on record |
| A required-trace check was weakened (e.g., made conditional) without a constitutional change ECP | Silent invariant weakening | critical | Revert the weakening; open a constitutional change ECP; do not re-apply until approved |
| A field was removed from a `required_for_each_candidate` list without a version bump and ECP | Silent invariant weakening | critical | Restore the removed field; open a constitutional change ECP; version bump required before re-removal |
| `require_human_when` was changed from a non-empty list to an empty list on a high-risk EOU without an ECP | Silent escalation removal | critical | Restore `require_human_when` to the prior non-empty list; open ECP if removal was intentional |
| An EOU with `function` other than `propose` modified `foundry/constitution.yml` | Unauthorized constitutional mutation | critical | Revert constitution modification; identify and block the EOU from further execution until its `authority_level` is corrected |
