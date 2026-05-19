---
name: eou-foundry-init
description: "Use when the user asks to initialize, scaffold, or create a new EOU-governed application. Creates a sibling directory with foundry/, instance copies of plugin templates, a starter constitution, and an initial git repo. Refuses to overwrite an existing directory."
metadata:
  short-description: Scaffold a new EOU-governed app
---

# Initialize EOU-Governed Application

You are scaffolding a new EOU-governed application. The user is invoking this from a workspace directory and should supply an app name.

## 1. Get the app name

If the user supplied an app name in their request, use it. Otherwise ask: "What is the application's slug name? (lowercase, alphanumeric + hyphen)"

Optional inputs:
- A one-line description of what the application does (defaults to the slug)
- `NO_GIT=1` — set this environment variable before the command to skip `git init` in the new directory (default: initialize git)

Validate the slug. Reject names containing `/`, `\`, `..`, a leading `.`, or any character outside `[a-z0-9-]`. Refuse to overwrite an existing directory.

## 2. Run init script

> `${PLUGIN_ROOT}` is the Codex runtime env var for the plugin root. The Claude Code equivalent is `${CLAUDE_PLUGIN_ROOT}`. Both resolve to the same directory — the name differs by runtime.

Run `bash "${PLUGIN_ROOT}/scripts/init_app.sh" "$APP_NAME" "$DESCRIPTION" $([ "$NO_GIT" = "1" ] && echo "--no-git")` and let the script handle the existence check and scaffolding atomically. Report what it produced.

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
- Runs `python3 "${PLUGIN_ROOT}/scripts/validate_foundry.py"`
  against the new app to confirm the scaffold passes the schema check.

## 4. Report

If the script returns exit code 0, surface a summary of what was created:

```
App initialized:
  ✓ <app-name>/                created with foundry/, .claude/, AGENTS.md, README.md
  ✓ foundry/constitution.yml   from template, customized for <app-name>
  ✓ foundry/registry.yml       empty (entries: [])
  ✓ git repo initialized       (or "skipped: NO_GIT=1")
  ✓ validate_foundry.py        OK

Next steps:
  cd <app-name>
  edit AGENTS.md                # the application's instructions
  edit foundry/constitution.yml # tailor invariants to this app's domain
  $generate-eou-candidates       # produce candidate EOUs for the workflow
```

## 5. Constraints

- Do not create an app directory interactively — require the slug as input before proceeding.
- Do not overwrite an existing directory — delegate the check to `init_app.sh` and report the exit code 2 error.
- Do not run `git init` or `validate_foundry.py` manually — the script handles both atomically.
- Do not modify template files or the plugin's own foundry during initialization.
- Do not proceed past Step 2 if the slug fails validation — report the error immediately.

## 6. Errors

If `init_app.sh` fails:
- Exit code 2 (existing directory): report "Directory `<app-name>/` already exists; refusing to overwrite. Pick a different name or move it aside."
- Exit code 3 (invalid slug): report "Invalid app name. Use lowercase alphanumeric + hyphen only."
- Exit code 4 (validate_foundry failed): show the validator output, then say "Scaffold completed but validation found issues. Inspect `<app-name>/foundry/` and fix before continuing."
- Any other non-zero: show the script's stderr verbatim.
