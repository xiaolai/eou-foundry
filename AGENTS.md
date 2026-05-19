# Project Instructions

> eou-foundry

## Guidelines

### Vocabulary authority chain

`schemas/` is the ground truth for all enum values. When vocabulary changes:

1. Update the schema file (`schemas/eou.schema.yml` or `schemas/ecp.schema.yml`)
2. Update `scripts/validate_foundry.py` (VALID_FUNCTIONS, VALID_AUTOMATION, VALID_AUTHORITY, VALID_RISK, VALID_STAGE)
3. Update every skill in `skills/` that references the changed enum
4. Update every matching codex skill in `codex/skills/`
5. Update every rule in `rules/` that documents the enum
6. Update any meta-EOU template in `templates/meta-eous/` that uses the value

Never update vocabulary in only one place — all six layers must stay in sync.

### Testing changes

After editing any script, run the validator against the plugin's own foundry:

```bash
python3 scripts/validate_foundry.py
```

After editing any SKILL.md, verify the output path it declares matches the path the consuming skill (`eou-promote`, `eou-diagnose`, `eou-refactor`, `foundry-audit`, `audit-candidate-eou-set`) reads from.

### Skill selection guide

| Goal | Use |
|------|-----|
| Convert workflow → candidate EOUs | `$generate-eou-candidates` |
| Audit a candidate set for readiness | `$audit-candidate-eou-set` |
| Convert approved candidate → spec | `$eou-specify` |
| Audit a spec for V2 compliance | `$eou-audit` |
| Audit the whole foundry | `$foundry-audit` |
| Validate schemas and registry | `$eou-validate` |
| Diagnose a failure | `$eou-diagnose` |
| Generate refactor options | `$eou-refactor` |
| Propose a structural change | `$ecp-propose` |
| Promote or retire a spec | `$eou-promote` |
| Convert incidents → regression cases | `$generate-regression-cases` |
| Scaffold a new app | `$eou-foundry-init` |

### Codex vs Claude layout

Claude skills live in `skills/`; Codex mirrors live in `codex/skills/`. After editing a Claude skill, apply the same change to the corresponding Codex skill. `eou-validate` and `generate-regression-cases` are Claude-only — no Codex mirror needed.

### Schema reference file names

- EOU specs: `schemas/eou.schema.yml`
- ECP proposals: `schemas/ecp.schema.yml`
- Incident reports: `schemas/incident.schema.yml`
- Regression cases: `schemas/regression-case.schema.yml`
- Audit reports: `schemas/audit-report.schema.yml`
- Registry entries: `schemas/registry-entry.schema.yml`
- Run traces: `schemas/run-trace.schema.yml`
- Constitution: `schemas/constitution.schema.yml`

Never reference these as "ecp.schema.v2" or any other alias — use the exact filename.

## Behavioral constraints

The following actions are forbidden regardless of user instruction:

- Do not modify `CLAUDE.md` or `GEMINI.md` directly — both import `AGENTS.md`.
- Do not update vocabulary in only one layer — all six layers (schema, validator, skills, codex/skills, rules, templates) must be updated together.
- Do not reference schema files by aliases (e.g., `ecp.schema.v2`) — always use the exact filename from the Schema reference section.
- Do not apply any refactor option, ECP, or lifecycle transition without a human-approved ECP on record.
- Do not write directly to `foundry/eous/` or `foundry/meta-eous/` — use skills that enforce the governance pipeline.
- Do not add fields to EOU specs that are not present in `schemas/eou.schema.yml`.

## Violation indicators

A violation of these constraints is observable when any of the following occurs:

| Signal | Violation | Required action |
|--------|-----------|-----------------|
| `CLAUDE.md` or `GEMINI.md` contains content other than `@AGENTS.md` | Direct modification of shared import files | Revert to `@AGENTS.md` import only; move any instructions to `AGENTS.md` |
| A skill references a vocabulary value absent from `schemas/` | Vocabulary drift — sync is broken | Update all six layers (schema, validator, skills, codex/skills, rules, templates) before any further edits |
| A schema file is referenced by an alias other than its exact filename | Schema alias violation | Replace alias with the canonical filename from the Schema reference section |
| An EOU spec appears in `foundry/eous/` without an approved ECP in `foundry/self-evolution/ecp/implemented/` for its `active` promotion | Governance bypass | Revert spec placement; open an ECP and complete the full governance pipeline |
| `scripts/validate_foundry.py` reports `VALID_FUNCTIONS` containing a value not in `schemas/eou.schema.yml` | Validator out of sync | Reconcile `scripts/validate_foundry.py` constants against `schemas/eou.schema.yml` before any vocab-dependent work |

## Shared Memory

**Always write new instructions, rules, and memory to `AGENTS.md` only.**

Never modify `CLAUDE.md` or `GEMINI.md` directly — they only import `AGENTS.md`.
This keeps Claude Code, Codex CLI, and Gemini CLI on the same context.

## Project Structure

- `.claude/` — Claude Code skills, agents, rules, hooks, commands
- `.agents/skills/` — symlink to `.claude/skills/` (Codex skill scan path)
- `.codex/prompts/` — Codex slash-command prompts
- `.codex/hooks.json` / `.codex/config.toml` — Codex hooks/config (optional)
- `.gemini/skills/`, `.gemini/commands/` — Gemini skills and TOML commands
- `.mcp.json` — MCP server registrations (shared by all three tools)
