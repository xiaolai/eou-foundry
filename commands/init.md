---
description: Scaffold a new EOU-governed application in the current workspace. Creates a sibling directory with foundry/, instance copies of plugin templates, a starter constitution, and an initial git repo.
argument-hint: "<app-name> [--description \"...\"] [--no-git]"
allowed-tools:
  - Bash
  - Read
  - Write
  - AskUserQuestion
---

# /eou-foundry:init

You are scaffolding a new EOU-governed application. The user invoked this
from a workspace directory and supplied an app name.

## 1. Parse arguments

Read `$ARGUMENTS`. Required: the first positional token is the app name
(slug: lowercase, alphanumeric + hyphen). Optional flags:
- `--description "..."` — one-line application purpose; defaults to the slug.
- `--no-git` — skip `git init` in the new application directory.

If no app name is supplied, ask the user:

```
AskUserQuestion:
  question: "What is the application's slug name? (lowercase, alphanumeric + hyphen)"
  header: "App name"
  options:
    - label: "Other"
      description: "Enter a slug name"
```

Validate the slug. Reject names containing `/`, `\`, `..`, leading `.`, or any
character outside `[a-z0-9-]`. Refuse to overwrite an existing directory.

## 2. Refuse if target exists

Run `bash "${CLAUDE_PLUGIN_ROOT}/scripts/init_app.sh" "$APP_NAME" "$DESCRIPTION" $([ "$NO_GIT" = "1" ] && echo "--no-git")` and let the script handle the existence check + scaffolding atomically. Report what it produced.

## 3. What the script does (for reference)

`scripts/init_app.sh` is idempotent in the sense of "refuse to clobber":

- Refuses if `./<app-name>/` already exists.
- Creates `./<app-name>/` and inside it:
  - `foundry/` populated from `templates/` — constitution, governance,
    registry (empty), maturity-model, failure-taxonomy, refactoring-patterns,
    runtime-contract, meta-eous/, templates/eou-template, templates/generating-eou-template.
  - `foundry/eous/`, `foundry/incidents/`, `foundry/audits/`,
    `foundry/runs/`, `foundry/self-evolution/{ecp/{proposed,approved,implemented,rejected},regression/cases,upstream/proposed-to-plugin}/` empty.
  - `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` minimal starters.
  - `.claude/settings.json` minimal scaffold (no hooks).
  - `.gitignore` with the standard AI-tool ignores.
  - `README.md` one-paragraph application overview.
- Substitutes `{{APP_NAME}}` and `{{DESCRIPTION}}` placeholders in the
  template files.
- Unless `--no-git`, runs `git init` and makes a single initial commit.
- Runs `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_foundry.py"`
  against the new app to confirm the scaffold passes the schema check.

## 4. Report

After the script returns, run `bash "${CLAUDE_PLUGIN_ROOT}/scripts/init_app.sh" --status "$APP_NAME"` and surface a summary:

```
App initialized:
  ✓ <app-name>/                created with foundry/, .claude/, AGENTS.md, README.md
  ✓ foundry/constitution.yml   from template, customized for <app-name>
  ✓ foundry/registry.yml       empty (entries: [])
  ✓ git repo initialized       (or "skipped: --no-git")
  ✓ validate_foundry.py        OK

Next steps:
  cd <app-name>
  edit AGENTS.md                # the application's instructions
  edit foundry/constitution.yml # tailor invariants to this app's domain
  /eou-foundry:generate-eou-candidates  # produce candidate EOUs for the workflow
```

## 5. Errors

If `init_app.sh` fails:
- Exit code 2 (existing directory): report "Directory `<app-name>/` already exists; refusing to overwrite. Pick a different name or move it aside."
- Exit code 3 (invalid slug): report "Invalid app name. Use lowercase alphanumeric + hyphen only."
- Exit code 4 (validate_foundry failed): show the validator output, then say "Scaffold completed but validation found issues. Inspect `<app-name>/foundry/` and fix before continuing."
- Any other non-zero: show the script's stderr verbatim.
