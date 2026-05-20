---
name: 95-generating-eous
description: Require every generating EOU to declare its envelope, budget, registry-diff check, minimality test, operational-value test, counter-generation, and blast radius. Candidates may not self-activate.
---

# Generating EOUs Rule

**Every generating EOU must declare its envelope, budget, registry-diff, minimality test, operational-value test, counter-generation, and blast radius before any candidate it produces is considered valid.** Generation is cheap and audit is expensive; without these declarations a generating EOU becomes an uncontrolled procedure factory that produces complexity faster than humans can review it.

Generating EOUs (`function: generate`) are proposal-producing units with strictly limited authority.

## Required declaration fields

Every generating EOU spec must include all of these sections:

| Section | Required content |
|---------|-----------------|
| `generation_envelope.allowed_outputs` | explicit list — no wildcards |
| `generation_envelope.forbidden_outputs` | must include `active_eou`, `approved_eou`, `constitution_change` |
| `generation_envelope.default_status` | must be `candidate` |
| `generation_budget.max_candidates` | numeric ceiling |
| `registry_diff` | questions checking for duplicates and better alternatives |
| `minimality_test` | questions testing whether a rule/schema/checklist would suffice |
| `operational_value_test` | reject criteria for zero-value candidates |
| `counter_generation` | `required: true`; `requires_for_each_candidate` fields listed |
| `blast_radius.forbidden_scope` | must exclude constitution, approved ECPs, active registry |

## Required fields per generated candidate

Each candidate output must include:

- `lifecycle_stage: candidate` (immutable until human promotion)
- `distinct_success_criterion`
- `classification.authority_level`
- `classification.risk_level`
- `owner_required`
- `activation_requirements`
- `operational_value`
- `arguments_against`
- `minimality_result`

## Required pipeline

```text
generate → argue against each candidate → rank → select minimal subset → audit-candidate-eou-set → simulate → human approval → activate
```

**Never generate → activate.** A generating EOU that outputs `active_eou` or sets `lifecycle_stage: active` has violated the generation envelope. This is a `critical` audit finding.

## Candidate output path

`foundry/self-evolution/candidate-sets/cs-{generating_eou_id}-{YYYYMMDD}-{hhmm}.yml`

Schema: `schemas/candidate-set.schema.yml` (ECP-0013, v0.6.0+). The validator
walks this directory and enforces:
- every candidate has `status: candidate` and non-empty `arguments_against`
- `audit_outcome` declares all seven required keys (`accepted`, `merged`,
  `demoted_to_rule`, `demoted_to_validator`, `demoted_to_stop_condition`,
  `rejected`, `minimal_recommended_subset`)
- `audit_status: audited` requires either `minimal_recommended_subset` or
  `rejected` to be non-empty (an audited set must say what survived)

Candidates must not be written directly to `foundry/eous/` or `foundry/meta-eous/` — those directories are for approved, active specs only. Pre-v0.6.0 layout
(`foundry/self-evolution/ecp/proposed/{slug}-candidates-{YYYYMMDD}.yml`) is
deprecated; the validator no longer requires the skip-pattern workaround.

## Violation indicators

| Signal | Severity | How to detect | Required action |
|--------|----------|---------------|-----------------|
| A generating EOU spec is missing any required `generation_envelope.*` field | critical | Check for `allowed_outputs`, `forbidden_outputs`, `default_status` in spec | Block promotion; require author to declare complete envelope before spec proceeds |
| A generated candidate has `lifecycle_stage` set to anything other than `candidate` | critical | Scan output files for `lifecycle_stage:` values other than `candidate` | Revert file; record as `generation_envelope_breach`; block the generating EOU from further output |
| A generated candidate is written directly to `foundry/eous/` or `foundry/meta-eous/` | critical | Watch for new files in those directories without a preceding ECP in `foundry/self-evolution/ecp/implemented/` | Revert file; require full governance pipeline before any placement in those directories |
| A generating EOU spec is missing `counter_generation` or `minimality_test` | high | Check spec structure for required declaration fields | Flag as `high`; block promotion until missing sections are added |
| A candidate output is missing `arguments_against` or `minimality_result` | medium | Scan each candidate in the output file | Return to generating EOU; require `arguments_against` and `minimality_result` before the candidate proceeds to `$audit-candidate-eou-set` |
