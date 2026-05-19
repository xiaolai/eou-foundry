# EOU Vocabulary Design Principles

Principles for deciding what earns a place in the EOU Foundry vocabulary as a
top-level noun or verb — and what does not.

These principles were derived from first principles and then battle-tested
against four established frameworks: OntoClean (Guarino & Welty), Domain-Driven
Design (Evans), ISO 25964 / ANSI-NISO Z39.19 warrant theory, and BPMN / Event
Storming (Brandolini). The six principles below incorporate the revisions that
cross-framework analysis forced.

---

## The Six Principles

### P1 — One term per distinct identity, at uniform granularity, within a declared scope

Two terms merge when they share the same identity criterion, operate at the
same level of specificity, and live within the same scope. A term legitimately
meaning different things across scopes is not a violation — it is a boundary
that must be named. Never apply the merge test globally across undeclared scope
boundaries.

Sibling terms in the vocabulary must be at comparable levels of specificity.
A vocabulary that mixes crisp acts (`diagnose`) with vague phases (`process`)
at the same level fails this principle even if each term individually passes
the merge test.

### P2 — Nouns are rigid artifacts; verbs are state-changing acts

A noun belongs in the inventory when it is *rigid* — it remains the same kind
of thing regardless of what state it is in — and has a testable criterion for
identity across time.

A state of an artifact is not a noun. `candidate`, `pending-approval`, and
`active` are field values on EOU specs, not standalone nouns. The artifact
they modify (`EOU spec`) is the noun.

A verb belongs when it either changes the authority-state of a named artifact
or produces a new rigid artifact that governance can act on independently.
Sub-steps that serve a named verb without changing anything a stakeholder needs
to react to separately are not top-level verbs.

### P3 — A verb is top-level only if it gates or produces

A verb earns its place when it either:

(a) changes what the executor is permitted to do next, or
(b) produces a named artifact that governance can act on independently.

An act that evaluates and recommends but does not change authority or produce
a governed artifact is a sub-step, not a top-level verb.

### P4 — The vocabulary is closed under its own operations, within scope

Every verb applies to at least one noun. Every noun is the target of at least
one verb. A term that never appears in a verb+noun combination within its scope
has no structural role and is a deletion candidate.

Evaluate closure per declared scope, not globally. A closure gap — a noun with
no producing verb, or a verb whose artifacts are only described in prose — is
evidence of an unnamed act.

### P5 — Comprehensive means no unnamed judgment

The vocabulary is comprehensive when every significant decision point has a
name that forces the practitioner to surface what they are actually deciding.

If practitioners routinely describe an act as "we just checked" or "it felt
right," or if documentation describes a step without assigning it a verb from
`VALID_FUNCTIONS`, the vocabulary has a gap.

### P6 — A term requires warrant before it enters

A term earns inclusion through at least one of:

- **Literary warrant** — it appears in actual domain artifacts (specs, rules, schemas)
- **User warrant** — practitioners reach for it unprompted when describing their work
- **Structural warrant** — the vocabulary hierarchy requires it for coherence
- **Domain warrant** — the operational domain requires the distinction to prevent a specific failure

Intuition alone is not warrant. Absence of warrant is grounds for exclusion or
demotion to a sub-step or field value.

---

## Self-Audit: EOU Foundry Vocabulary

Applying the six principles to the foundry's own nouns and verbs.

### Current canonical vocabulary

**Verbs (`VALID_FUNCTIONS`):**
`generate | specify | validate | diagnose | promote | refactor | audit | propose | activate | implement | retire`

**Nouns (governed artifacts):**
EOU spec, ECP, candidate set, incident, audit report, validation report,
regression case, run trace, no-change record, refactor option, diagnosis

**Field values (not nouns):**
lifecycle stages (`candidate | draft | simulated | pilot | active | monitored | stable | deprecated | retired`),
authority levels (`suggest_only | draft_only | write_candidate | write_inactive | mutate_active | approve | publish`)

### Findings

| ID | Principle | Severity | Finding |
|----|-----------|----------|---------|
| V-01 | P2 | Moderate | `candidate` is used both as a lifecycle stage (field value on EOU spec) and as shorthand for items in the candidate set — conflating an anti-rigid role with a rigid artifact |
| V-02 | P3 | Moderate | `promote` names the evaluation ("can this EOU advance?"), not the state-changing act; the actual stage transition happens through ECP approval and has no top-level verb |
| V-03 | P4 | **High** | `implement` appears in documentation and diagrams as a named edge (`ECP →implement→ EOU spec`) but is absent from `VALID_FUNCTIONS` |
| V-04 | P4 | Moderate | `report` (creating an incident) is not a verb; incidents are recorded throughout the system but no named act covers their creation |
| V-05 | P4 | Low | Run trace has no producing verb; produced during execution but not covered by any entry in `VALID_FUNCTIONS` |
| V-06 | P4 | Moderate | No-change record has no producing verb; implied as an outcome of `diagnose` but not assigned a named act |
| V-07 | P5 | **High** | `activate` — moving an EOU to `lifecycle_stage: active` — is the most consequential lifecycle transition; it appears repeatedly in prose and diagrams as a step but has no top-level verb |
| V-08 | P5 | Moderate | `retire` is unnamed as a distinct act; folded inside `promote` despite requiring a different judgment (owner decision + successor documentation) from promotion |
| V-09 | P1 | Low | `validate` and `audit` both produce reports; the deterministic/judgment distinction between them is documented in prose but not surfaced in the vocabulary structure itself |

### Analysis

**V-03 and V-07 are the most serious findings.**

Both are High severity because they represent closure failures at the ends of
the governance pipeline — the two acts that close the loop:

```text
propose ECP → [implement?] → EOU spec updated
generate candidates → [activate?] → EOU spec live
```

The system's own Mermaid diagrams label these edges explicitly (`ECP
-->|implement| SPEC`, `APP --> ACT["activate"]`) but neither appears in
`VALID_FUNCTIONS`. This means validators cannot check for them, skills cannot
reference them by canonical name, and practitioners have no authoritative name
for the most consequential acts in the system.

**V-02 compounds V-07.**

`promote` currently covers both the evaluation function and the lifecycle
transition concept. Separating the evaluation ("should this EOU advance?")
from the actual transition ("this EOU is now active") would give `activate`
a clear scope and give `promote` a cleaner definition: evaluation only,
no authority to change state.

**V-01 (the candidate conflation) is a naming discipline issue, not a
structural one.**

The `candidate set` is a legitimate rigid artifact (produced by `generate`,
consumed by `audit`). The problem is that "candidates" (plural, unqualified)
is used colloquially to mean EOU specs at `lifecycle_stage: candidate` — an
anti-rigid role. The fix is discipline in prose: always write "candidate set"
for the artifact and "EOU spec at candidate stage" (or "candidate-stage EOU
spec") for the role-state. No vocabulary addition needed.

**V-04, V-05, V-06 are related: three artifacts without producing verbs.**

- Incidents: currently implied to be created by practitioners observing failures.
  The act is real — it is the `observe` step in the governance pipeline — but
  `observe` is not in `VALID_FUNCTIONS`.
- Run traces: produced by execution, but execution is the domain of the
  consuming application's EOUs, not the Foundry itself. Low severity for now.
- No-change records: produced when `diagnose` finds insufficient evidence for
  a change. The `diagnose` verb could be understood to produce either an ECP
  (via `propose`) or a no-change record directly. If `diagnose` produces both,
  the producing-verb relationship is satisfied, but the two outputs need to be
  explicitly documented as the two outcomes of `diagnose`.

**V-08 (`retire` unnamed) is a moderate clarity issue.**

Retirement requires: successor EOU documented or owner decision recorded. That
is a different judgment from promotion (evidence of maturity). Separating the
two into `promote` (evaluate and advance) and `retire` (owner-authorized
withdrawal) would make both clearer and give `retire` a distinct success
criterion.

**V-09 (`validate` vs `audit`) is low severity.**

The distinction is real and correct: `validate` = deterministic structural
check (schema conformance, field presence, registry consistency); `audit` =
judgment-heavy evaluation (design quality, compliance, blast-radius coherence).
The vocabulary is right; the documentation of the distinction could be sharper.

### What the audit does not recommend changing

The eight canonical function values are well-warranted (P6 satisfied for all
eight), are at comparable granularity (P1 satisfied), and are all rigid acts
with distinct success criteria (P3 satisfied). The authority level and
lifecycle stage hierarchies are correctly modeled as field values, not nouns
(P2 satisfied).

The noun inventory (EOU spec, ECP, candidate set, incident, audit report,
validation report, regression case, run trace, no-change record, refactor
option, diagnosis) is complete except for the closure gaps noted above.

### Resolution status

All findings have been resolved:

| ID | Resolution |
|----|-----------|
| V-01 | Prose discipline: "candidate set" for the artifact, "candidate-stage EOU spec" for the role-state. No vocabulary addition. |
| V-02 | `promote` redefined as evaluation-only in skills, codex/skills, and template. Skills now explicitly state that `activate` and `retire` are the execution functions. |
| V-03 | `implement` added to `VALID_FUNCTIONS`, schema, rules, and all six vocabulary-authority-chain layers. Rule 93 pipeline updated: `deploy` → `implement`. |
| V-04 | Deferred — incident creation (`observe`) is application-domain, not foundry-level. |
| V-05 | Deferred — run trace production is application-domain. |
| V-06 | `diagnose` dual-output contract documented in both Claude and Codex skills. |
| V-07 | `activate` added to `VALID_FUNCTIONS` and all six layers. |
| V-08 | `retire` added to `VALID_FUNCTIONS` and all six layers. |
| V-09 | Function vocabulary table in `02-architecture.md` distinguishes evaluation functions (`promote`, `audit`, `validate`) from execution functions. |
