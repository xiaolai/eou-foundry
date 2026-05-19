---
name: 94-no-self-approval
description: Forbid any EOU, skill, script, or agent from being the sole approver of changes to itself. Generation, auditing, refactoring, approval, deployment must remain separable.
---

# No Self-Approval Rule

No EOU, skill, script, or agent may be the sole approver of changes to itself.

## Structural requirement

In every EOU spec, `responsibility.executor` must not equal `responsibility.approver`. This is a hard schema constraint checked by `scripts/validate_foundry.py`.

## Separation of roles (must be different parties)

| Role pair | Constraint |
|-----------|-----------|
| generates EOU | ≠ approves EOU |
| audits EOU | ≠ the EOU being audited |
| proposes ECP | ≠ approves ECP |
| refactors EOU | ≠ self-certifies the refactor |
| deploys change | ≠ the only party who reviewed it |

## Generating EOUs

A generating EOU (`function: generate`) may create candidates only. It may not:

- Set `lifecycle_stage: active` or `approved_eou` on any generated output.
- Approve, publish, or deploy its own outputs.
- Mutate `foundry/registry.yml` or active governance.
- Weaken validators or rewrite the constitution.

## Enforcement

Violations are `self_approval` findings in EOU audit reports (severity: `critical`). An EOU with a self-approval violation may not be promoted to `lifecycle_stage: active`.

## Audited exceptions

The general rule has one named exception, recorded explicitly here rather than tolerated implicitly.

**CI auto-merge from the named maintainer identity.** The plugin's GitHub Actions workflow auto-merges PRs whose author matches `xiaolai`. This is identity-based self-approval at the CI layer: in single-maintainer plugin development, requiring a second human reviewer would block every change without finding different bugs, and no second reviewer is staffed.

The exception applies only when **all three conditions** hold:

1. CI validation (YAML syntax, Python compileall, schema checks) passes before the merge.
2. The workflow run id and merged commit SHA are retained in GitHub Actions logs for audit reconstruction.
3. The exception is revocable: a follow-on ECP may retire the auto-merge without further amendment to this rule.

This exception is recorded in ECP-0011 (filed in book-workshop's upstream channel). Critics may revoke it by opening a new ECP; until they do, the maintainer accepts the single-point-of-failure risk in exchange for development velocity.

The exception does **not** extend to:
- EOU spec changes (still require separation between executor and approver).
- ECP approval (still require named human approver, not a workflow identity).
- Constitutional changes (still require explicit human review per rule 91).

## Violation indicators

| Signal | Severity | How to detect | Required action |
|--------|----------|---------------|-----------------|
| `responsibility.executor` equals `responsibility.approver` in an EOU spec | critical | `scripts/validate_foundry.py` flags `self_approval` on every spec | Block promotion; reassign approver to a different party |
| A generating EOU writes `lifecycle_stage: active` on a candidate it produced | critical | Scan generated output files for `lifecycle_stage: active` | Revert generated file; record as `generation_envelope_breach` |
| The same executor both proposes and approves an ECP | critical | Check `approval.approver` against the EOU's `responsibility.executor` | Invalidate ECP approval; require a different named human to re-approve |
| A skill or script invokes itself to validate its own output without a separate auditor | high | Trace the audit pipeline for the same executor in both proposal and audit steps | Introduce a distinct auditing EOU with a different `responsibility.executor` |
