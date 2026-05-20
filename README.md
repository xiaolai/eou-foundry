# eou-foundry

[![Validated by NLPM](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/xiaolai/eou-foundry/main/nlpm-badge.json)](https://github.com/xiaolai/eou-foundry/blob/main/nlpm-badge.json)

Recursive governance for **Executable Operating Units (EOUs)** — installable
as a Claude Code plugin into any project that needs to turn messy human
workflows into structured, auditable, improvable operating units.

## What an EOU is

An EOU is an operational hypothesis, not a prompt or a checklist:

```text
Given inputs X, context Y, procedure Z, and validation tests T,
this unit should produce output O within acceptable risk R.
```

Every EOU uses faceted classification — no single vague type label decides
authority or risk:

```text
function + target_object + automation_mode + authority_level + risk_level + lifecycle_stage
```

## What the plugin provides

| Layer | What ships |
|---|---|
| Schemas | `schemas/*.schema.yml` — the contract (EOU, ECP, registry-entry, run-trace, no-trace-justification, candidate-set, incident, audit-report) |
| Engine artifacts (v0.5.0+) | `engine/` — canonical, plugin-owned, app-inherited: `constitution-defaults.yml`, `failure-taxonomy.yml`, `maturity-model.yml`, `refactoring-patterns.yml`, `runtime-contract.yml`, `governance.yml`, plus 11 canonical meta-EOUs under `engine/meta-eous/` |
| Engine theory | `engine/{eou-contract, eou-foundry-v2, eou-system}.md` |
| Governance rules | 7 rules covering classification, ECP requirement, recursive governance, no-self-approval, generating-EOU constraints, and constitutional reads |
| Skills | 11 Foundry skills (see Skills table below) |
| Templates | Constitution, registry, generic EOU, generating-EOU starters |
| Scaffolding | `/eou-foundry:init` creates a new application dir with a fresh `foundry/` that inherits engine artifacts from the plugin |
| Validators | `scripts/validate_foundry.py` (full pipeline: constitution merge, registry, ECPs, regression, run traces, trace gate, candidate sets, activation evidence, maturity evidence, dependency DAG, engine artifacts, overrides) |
| Design docs | 6 dev-docs: foundations, architecture, doctrine, vocabulary principles, V6 design pulls, values over rules |

## What the plugin does *not* provide

- **Application-level engines.** A book-workshop application using A2B
  Engine V2.2 needs its own `engine/` docs and its own workshop-specific
  skills/rules. The plugin governs the EOU contract; the application owns
  its domain.
- **Application state.** The consuming project's `foundry/constitution.yml`,
  `registry.yml`, `eous/`, `incidents/`, `audits/`, `runs/` are owned and
  versioned by the application, not the plugin.
- **Application-level ECPs.** Changes to an application's own EOUs go
  through that application's ECP cycle. Changes to the *plugin* go through
  the plugin's ECP cycle in `self-evolution/`.

## Install

From the xiaolai marketplace (recommended):

```bash
# one-time, if you haven't already added the xiaolai marketplace:
claude plugin marketplace add xiaolai/claude-plugin-marketplace

# then in any project:
claude plugin install eou-foundry@xiaolai --scope project
```

From a local checkout (for plugin development):

```bash
claude plugin marketplace add /path/to/eou-foundry
claude plugin install eou-foundry@eou-foundry-local --scope project
```

## Quick start

From a workspace directory:

```bash
/eou-foundry:init my-app
```

That creates `./my-app/foundry/` populated from the plugin's templates and
runs `validate_foundry.py` against it. The new app is its own git repo.

## Skills

| Skill | Purpose |
|---|---|
| `/eou-foundry:generate-eou-candidates` | Generate a ranked candidate EOU set from a messy workflow |
| `/eou-foundry:audit-candidate-eou-set` | Audit a generated candidate set for boundary quality and minimality |
| `/eou-foundry:eou-specify` | Convert an approved candidate into a formal EOU spec |
| `/eou-foundry:eou-audit` | Audit an EOU spec against the schema (judgment-heavy) |
| `/eou-foundry:eou-validate` | Validate the foundry's structural integrity (deterministic) |
| `/eou-foundry:eou-diagnose` | Diagnose an EOU failure using the F-code taxonomy |
| `/eou-foundry:eou-refactor` | Generate candidate refactor options (proposal-only) |
| `/eou-foundry:eou-promote` | Evaluate whether an EOU can be promoted to the next maturity level (recommendation only) |
| `/eou-foundry:foundry-audit` | Audit the consuming project's whole `foundry/` system-wide |
| `/eou-foundry:ecp-propose` | Draft a formal ECP from a diagnosed failure or refactor option |
| `/eou-foundry:generate-regression-cases` | Convert incidents and audit failures into candidate regression cases |

## v0.5.0 — Engine-reference architecture (ECP-0003)

Pre-v0.5.0, every scaffolded app carried snapshot copies of the engine
artifacts (failure taxonomy, maturity model, governance rules, etc.).
Apps drifted from the engine as the plugin evolved.

In v0.5.0, **engine artifacts live canonically in the plugin and apps
inherit them**. An app's `foundry/constitution.yml` declares
`inherits_from: "eou-foundry@>=0.5.0"`; the validator merges the plugin's
`engine/constitution-defaults.yml` first, then the app's local
strengthenings on top, and refuses any merge that drops or weakens an
engine key. Apps can override individual engine artifacts under
`foundry/overrides/<engine-file>.yml`, but the override is merged
key-by-key against the engine canonical — it cannot drop keys present
upstream.

## v0.6.0 — Lifecycle/evidence triangle + closure gaps

Four ECPs together turn lifecycle claims from self-declarations into
evidence-bound assertions, plus close two structural gaps:

- **Trace gate (ECP-0014, hard-cut).** Every EOU at `lifecycle_stage` in
  `{active, monitored, stable}` must either declare `outputs.trace`
  referencing `runs/` paths, OR have a non-expired
  `foundry/audits/no-trace/{eou_id}.yml` justification with a named
  human reviewer (TODO placeholders are rejected). No warning phase —
  the no-trace-justification mechanism IS the migration path.
- **Activation evidence (ECP-0010).** Registry entries at active stages
  must populate `activated_by` (either `{ecp_id, approver, activated_at}`
  or `{legacy_bootstrap: true, bootstrap_justification, bootstrap_expires_at}`).
  No EOU enters production without a recorded governance path.
- **Maturity evidence (ECP-0009).** Registry `maturity` claims must be
  at or above the level required by the entry's `lifecycle_stage` per
  `engine/maturity-model.yml`. Self-declared maturity is rejected.
- **Candidate-set schema (ECP-0013).** Candidate sets now have a
  schema, a canonical path
  (`foundry/self-evolution/candidate-sets/cs-{generator}-{YYYYMMDD}-{hhmm}.yml`),
  and a validator walker. Every candidate inside must have `status: candidate`
  and non-empty `arguments_against`; the `audit_outcome` block must declare
  all seven outcome keys (`accepted`, `merged`, `demoted_to_rule`,
  `demoted_to_validator`, `demoted_to_stop_condition`, `rejected`,
  `minimal_recommended_subset`).

## Rules (loaded automatically when plugin is installed)

| File | Enforces |
|---|---|
| `89-eou-foundry.md` | Canonical EOU layer at `foundry/`; faceted classification mandatory |
| `90-eou.md` | EOUs live under `foundry/eous/` or `foundry/meta-eous/`; no root-level `eous/` |
| `91-foundry-constitution.md` | Read `foundry/constitution.yml`, `governance.yml`, `failure-taxonomy.yml` before changing EOU behavior |
| `92-ecp.md` | All significant Foundry mutations require an ECP |
| `93-recursive-governance.md` | Bounded self-improvement (observe → diagnose → propose → simulate → regression → audit → approve → implement); no observe-then-self-edit |
| `94-no-self-approval.md` | No EOU may be the sole approver of changes to itself |
| `95-generating-eous.md` | Generating EOUs must declare envelope, budget, registry-diff, minimality, operational-value, counter-generation; never generate → activate |

## Validation

From the consuming project's root:

```bash
# preferred — slash command resolves the plugin install path automatically
/eou-foundry:eou-validate

# or invoke the script directly
EOU_FOUNDRY_PLUGIN_PATH=/path/to/installed/eou-foundry \
  python3 /path/to/installed/eou-foundry/scripts/validate_foundry.py .
```

The script resolves the plugin root in priority order:
`EOU_FOUNDRY_PLUGIN_PATH` env var → `~/.claude/plugins/installed_plugins.json`
→ the script's own parent directory. Engine artifacts are read from the
plugin; app artifacts are read from `./foundry/`. The validator refuses
constitution merges that weaken engine invariants and refuses lifecycle
claims unsupported by their declared evidence.

## Self-evolution and feedback

The plugin's own evolution lives in `self-evolution/`:

```text
self-evolution/
├── changelog.md
├── ecp/
│   ├── proposed/        ← ECPs received from applications upstream
│   ├── approved/
│   ├── implemented/
│   └── rejected/
└── regression/
    └── cases/
```

The mature feedback loop:

```text
application/foundry/incidents/      real failure during work
   ↓ distilled into
application/foundry/self-evolution/upstream/proposed-to-plugin/<ecp>.yml
   ↓ copied / PR'd to
eou-foundry/self-evolution/ecp/proposed/<ecp>.yml
   ↓ reviewed at plugin level
eou-foundry @ vNext (released)
   ↓ applications upgrade
```

Because the proposal originates downstream and is reviewed upstream, the
`no-self-approval` rule becomes structural — the plugin literally cannot
approve its own changes.

## License

ISC. See `LICENSE`.
