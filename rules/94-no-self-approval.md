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

## Violation indicators

| Signal | Severity | How to detect | Required action |
|--------|----------|---------------|-----------------|
| `responsibility.executor` equals `responsibility.approver` in an EOU spec | critical | `scripts/validate_foundry.py` flags `self_approval` on every spec | Block promotion; reassign approver to a different party |
| A generating EOU writes `lifecycle_stage: active` on a candidate it produced | critical | Scan generated output files for `lifecycle_stage: active` | Revert generated file; record as `generation_envelope_breach` |
| The same executor both proposes and approves an ECP | critical | Check `approval.approver` against the EOU's `responsibility.executor` | Invalidate ECP approval; require a different named human to re-approve |
| A skill or script invokes itself to validate its own output without a separate auditor | high | Trace the audit pipeline for the same executor in both proposal and audit steps | Introduce a distinct auditing EOU with a different `responsibility.executor` |
