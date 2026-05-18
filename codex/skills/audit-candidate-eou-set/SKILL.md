---
name: audit-candidate-eou-set
description: Audit a generated candidate EOU set for boundary quality, minimality, overlap, authority, operational value, and governance risk.
---

# Audit Candidate EOU Set

Audit `$path` (a `candidate_eou_set.yml` file).

## Required reading

1. `foundry/constitution.yml`
2. `foundry/registry.yml`
3. `foundry/governance.yml`
4. `foundry/meta-eous/audit-candidate-eou-set.yml`

## Tests

Run each test against every candidate in the set.

### Boundary Test
Each candidate must have **one** distinct success criterion. A candidate whose success criterion subsumes another candidate's fails this test. Flag candidates with compound or overlapping success criteria.

### Non-Overlap Test
No candidate may duplicate an existing EOU in `foundry/registry.yml` or another candidate in this set. Check by purpose, target_object, and success criterion. Flag overlapping pairs and recommend merge or rejection.

### Minimality Test
Each candidate must fail the following substitution checks — if it passes any, it should be converted instead of created as an EOU:
- Can this be a **rule** (static constraint, no execution required)?
- Can this be a **validator** (schema constraint, machine-checkable)?
- Can this be a **regression case** (captures a known failure)?
- Can this be a **stop condition** on an existing EOU?
- Can this be a **checklist item** inside an existing EOU's steps?

### Authority Test
Generating EOUs in the candidate set must not have `authority_level` set to `approve`, `publish`, or `write_active`. Flag candidates claiming more authority than `write_candidate` or `write_inactive` without constitutional justification.

### Operational Value Test
Each candidate must satisfy at least one of:
- `prevents_failure`: names a concrete failure mode it blocks
- `improves_decision`: names a judgment it makes explicit
- `exposes_hidden_judgment`: surfaces an implicit step that is currently untracked
- `improves_traceability`: adds observable accountability to a previously opaque step

Reject candidates that exist only for completeness or that duplicate the purpose of an existing artifact.

### Counter-Generation Test
Each kept candidate must include `arguments_against` — the strongest case for not creating it. Candidates missing this field are not ready for specification.

### Set Composition Test
If the candidate set includes EOUs that generate outputs, it must also include EOUs (or identify existing ones) for auditing and approving those outputs. A generation-only set without a corresponding audit path is incomplete.

### High-Stakes Test
Candidates touching finance, health, legal, safety, content about minors, public claims, publication, or active governance must have `responsibility.approver` set to a named human role and `escalation.require_human_when` non-empty. Flag candidates in these domains missing human ownership.

## Verdict thresholds

| Verdict | Criteria |
|---|---|
| **PASS** | All candidates pass Boundary, Authority, and Operational Value tests. At most 1 Minimality finding per 5 candidates. High-Stakes test passes for all domain-relevant candidates. |
| **REVISE** | 1–2 Minimality or Non-Overlap failures, no Authority or High-Stakes failures. Candidates can be revised without rejection. |
| **FAIL** | Any Authority or High-Stakes failure. More than 2 Minimality failures. Any candidate with an Authority level above `write_inactive` lacking constitutional justification. |

## Output

Write the audit report to `foundry/audits/candidate-set-audits/{set_id}.audit.yml`:

```yaml
set_id:
audit_date:
verdict:  # PASS | REVISE | FAIL
candidate_recommendations:
  keep:    # list of candidate IDs — pass all tests
  merge:   # list of (id_a, id_b, reason) pairs
  defer:   # list of (id, reason) — valid but out of scope
  reject:  # list of (id, reason) — fails tests
  convert: # list of (id, convert_to: rule|validator|regression_case|stop_condition|checklist)
findings:
  - candidate_id:
    test:
    severity:  # critical | high | medium | low
    description:
    required_action:
required_revisions_before_specification:
  - # list of changes needed before any candidate can proceed to eou-specify
```
