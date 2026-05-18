# eou-foundry

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
| Schemas | `schemas/*.schema.yml` — the contract |
| Engine theory | `engine/{eou-contract, eou-foundry-v2, eou-system}.md` |
| Governance rules | 7 rules covering schema, constitution, ECP requirement, recursive governance, no-self-approval, generating-EOU constraints |
| Skills | 9 Foundry skills (specify, audit, diagnose, refactor, promote, foundry-audit, ECP propose, generate candidates, audit-candidate-set) |
| Templates | Constitution, governance, registry starters; maturity model, failure taxonomy, refactoring patterns, runtime contract; 10 meta-EOU specs; EOU and generating-EOU card templates |
| Scaffolding | `/eou-foundry:init` creates a new application dir with a fresh `foundry/` |
| Validators | `scripts/validate_foundry.py`, `validate_recursive_case.py` |
| Architecture history | 5 dev-docs documenting the design evolution |

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

Local (from a checkout):

```bash
claude plugin install /Users/joker/github/xiaolai/myprojects/claude-plugins/eou-foundry --scope project
```

From a marketplace (once published):

```bash
claude plugin install eou-foundry@xiaolai --scope project
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
| `/eou-foundry:eou-specify` | Convert an approved candidate into a formal EOU spec |
| `/eou-foundry:eou-audit` | Audit an EOU card against the schema |
| `/eou-foundry:eou-diagnose` | Diagnose an EOU failure using the failure taxonomy |
| `/eou-foundry:eou-refactor` | Generate candidate refactor options (proposal-only) |
| `/eou-foundry:eou-promote` | Evaluate whether an EOU can be promoted to the next maturity level |
| `/eou-foundry:foundry-audit` | Audit the consuming project's whole `foundry/` |
| `/eou-foundry:ecp-propose` | Draft a formal ECP from a diagnosed failure |
| `/eou-foundry:generate-eou-candidates` | Generate a ranked candidate EOU set from a messy workflow |
| `/eou-foundry:audit-candidate-eou-set` | Audit a generated candidate set for boundary quality and minimality |

## Rules (loaded automatically when plugin is installed)

| File | Enforces |
|---|---|
| `89-eou-foundry.md` | Canonical EOU layer at `foundry/`; faceted classification mandatory |
| `90-eou.md` | EOUs live under `foundry/eous/` or `foundry/meta-eous/`; no root-level `eous/` |
| `91-foundry-constitution.md` | Read `foundry/constitution.yml`, `governance.yml`, `failure-taxonomy.yml` before changing EOU behavior |
| `92-ecp.md` | All significant Foundry mutations require an ECP |
| `93-recursive-governance.md` | Bounded self-improvement (observe → diagnose → propose → simulate → regression → audit → approve → deploy); no observe-then-self-edit |
| `94-no-self-approval.md` | No EOU may be the sole approver of changes to itself |
| `95-generating-eous.md` | Generating EOUs must declare envelope, budget, registry-diff, minimality, operational-value, counter-generation; never generate → activate |

## Validation

From the consuming project's root:

```bash
python3 scripts/validate_foundry.py
python3 scripts/validate_recursive_case.py   # only if case-studies/recursive-book-production/ exists
```

These scripts ship in this plugin but execute against the consuming
project's `foundry/`. The plugin's `clean_generated.py` removes
`__pycache__/*.pyc` under the consuming project's repo root.

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
