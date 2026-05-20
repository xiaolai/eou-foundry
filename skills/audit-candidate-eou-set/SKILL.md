---
name: audit-candidate-eou-set
description: |
  Audit a generated candidate EOU set for boundary quality, minimality, overlap, authority, operational value, and governance risk before any candidate advances to specification.
  <example>
  Context: A generation run has just produced a candidate set; the owner wants to know which candidates survive audit before promotion.
  user: "$audit-candidate-eou-set foundry/self-evolution/candidate-sets/cs-generate-eou-candidates-20260520-1430.yml"
  assistant: "I'll run the eight tests (boundary, non-overlap, minimality, authority, operational value, counter-generation, set composition, high-stakes) and write the audit report under foundry/audits/candidate-set-audits/."
  </example>
  <example>
  Context: User wants to audit a candidate set that contains a generating EOU without a corresponding audit path.
  user: "$audit-candidate-eou-set ./my-candidates.yml"
  assistant: "I'll audit. Heads-up that if any candidate has authority_level approve/publish or proposes weakening validators, I'll escalate to FAIL regardless of other test outcomes."
  </example>
argument-hint: CANDIDATE_SET_PATH
arguments:
  - path
allowed-tools:
  - Read
  - Write
  - Grep
---

# Audit Candidate EOU Set

Audit `$path` (a candidate-set artifact under `foundry/self-evolution/candidate-sets/`).

## Inputs

- `$path` (required) — path to a candidate-set file at `foundry/self-evolution/candidate-sets/cs-{generating_eou}-{YYYYMMDD}-{hhmm}.yml`, produced by `$generate-eou-candidates`. Schema: `schemas/candidate-set.schema.yml` (ECP-0013).

## Required reading

1. `foundry/constitution.yml`
2. `foundry/registry.yml`
3. `foundry/governance.yml`
4. `foundry/meta-eous/audit-candidate-eou-set.yml`

## Stop conditions

Halt and report before running tests if:
- `$path` does not resolve to a readable YAML file.
- The file does not contain a `candidates` array, or `candidates` is empty.
- `foundry/constitution.yml` or `foundry/registry.yml` does not exist — required for Authority and Non-Overlap tests.

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
Generating EOUs in the candidate set must not have `authority_level` set to `approve`, `publish`, or `mutate_active`. Flag candidates claiming more authority than `write_candidate` or `write_inactive` without constitutional justification.

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
| **PASS** | All candidates pass Boundary, Authority, and Operational Value tests. At most 1 Minimality finding per 5 candidates. High-Stakes test passes for every candidate whose `target_object` falls in finance, health, legal, safety, content about minors, public claims, publication, or active governance domains. |
| **REVISE** | 1–2 Minimality or Non-Overlap failures, no Authority or High-Stakes failures. Candidates can be revised without rejection. |
| **FAIL** | Any Authority or High-Stakes failure. More than 2 Minimality failures. Any candidate with an Authority level above `write_inactive` lacking constitutional justification. |

## Constraints

- Do not modify the candidate set file — write only to the audit output path.
- Do not apply verdicts retroactively to an existing audit report — write a new dated report.
- Do not set `verdict: PASS` if any Authority or High-Stakes test fails, regardless of other results.
- Do not promote any candidate to `lifecycle_stage: active` — that is the role of `$eou-promote` after human approval.
- Treat `arguments_against` as required, not optional — candidates missing this field fail the Counter-Generation Test.
- A PASS verdict does not authorize specification — candidates still require human review before proceeding to `$eou-specify`.

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

## Scope Note

**Upstream:** receives candidate-set artifacts produced by `$generate-eou-candidates` at `foundry/self-evolution/candidate-sets/`.

**Downstream:** PASS verdict feeds `$eou-specify` (one candidate at a time, after human review); FAIL verdict feeds back into `$generate-eou-candidates` with a tighter brief.

**Related:** `$eou-audit` (audits an EOU spec, not a candidate set); `$foundry-audit` (audits the whole Foundry, not one set).

**Pipeline:** `generate-eou-candidates → audit-candidate-eou-set → human review → eou-specify`
