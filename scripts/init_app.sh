#!/usr/bin/env bash
# eou-foundry: scaffold a new EOU-governed application in cwd.
# Invoked by /eou-foundry:init. Idempotent in the "refuse to clobber" sense.
#
# Usage:
#   init_app.sh <app-name> [<description>] [--no-git]
#   init_app.sh --status <app-name>

set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATES="$PLUGIN_DIR/templates"

ok()   { printf '✓ %s\n' "$*"; }
skip() { printf '· %s\n' "$*"; }
warn() { printf '! %s\n' "$*" >&2; }
err()  { printf 'error: %s\n' "$*" >&2; }

# --- status subcommand -----------------------------------------------------
if [ "${1:-}" = "--status" ]; then
  APP="${2:?app name required}"
  echo "App: $APP"
  [ -d "$APP" ]                            && ok "$APP/ exists"               || warn "$APP/ missing"
  [ -f "$APP/foundry/constitution.yml" ]   && ok "foundry/constitution.yml"   || warn "missing constitution"
  [ -f "$APP/foundry/registry.yml" ]       && ok "foundry/registry.yml"       || warn "missing registry"
  [ -d "$APP/.git" ]                       && ok "git repo initialized"       || skip "no git repo (--no-git or skipped)"
  exit 0
fi

# --- normal init ------------------------------------------------------------
APP_NAME="${1:?app name required}"
DESCRIPTION="${2:-$APP_NAME}"
NO_GIT=0
for arg in "${@:3}"; do
  case "$arg" in
    --no-git) NO_GIT=1 ;;
  esac
done

# Validate slug
if ! printf '%s' "$APP_NAME" | grep -qE '^[a-z0-9][a-z0-9-]*$'; then
  err "invalid app name: $APP_NAME (must match [a-z0-9][a-z0-9-]*)"
  exit 3
fi

# Refuse if dir exists
if [ -e "$APP_NAME" ]; then
  err "directory \"$APP_NAME\" already exists; refusing to overwrite"
  exit 2
fi

# --- scaffold ---------------------------------------------------------------
mkdir -p "$APP_NAME"/{foundry/{eous,meta-eous,incidents,audits,runs,engine,templates},.claude/{rules,skills,agents,commands,hooks},foundry/self-evolution/{ecp/{proposed,approved,implemented,rejected},regression/{cases,fixtures},upstream/proposed-to-plugin}}

# Copy universals (these are domain-agnostic; the app starts identical to the plugin)
for f in maturity-model failure-taxonomy refactoring-patterns runtime-contract; do
  cp "$TEMPLATES/${f}.yml.template" "$APP_NAME/foundry/${f}.yml"
done

# Copy instance starters with placeholder substitution
for f in constitution governance registry; do
  sed -e "s|{{APP_NAME}}|${APP_NAME}|g" \
      -e "s|{{DESCRIPTION}}|${DESCRIPTION}|g" \
      "$TEMPLATES/${f}.yml.template" > "$APP_NAME/foundry/${f}.yml"
done

# Copy meta-EOUs and templates
cp -R "$TEMPLATES/meta-eous/." "$APP_NAME/foundry/meta-eous/"
cp -R "$TEMPLATES/eou-template" "$APP_NAME/foundry/templates/"
cp "$TEMPLATES/generating-eou-template.yml" "$APP_NAME/foundry/templates/"

# Keep empty dirs alive in git
touch "$APP_NAME/foundry/eous/.gitkeep"
touch "$APP_NAME/foundry/incidents/.gitkeep"
touch "$APP_NAME/foundry/audits/.gitkeep"
touch "$APP_NAME/foundry/runs/.gitkeep"
touch "$APP_NAME/foundry/self-evolution/ecp/proposed/.gitkeep"
touch "$APP_NAME/foundry/self-evolution/ecp/approved/.gitkeep"
touch "$APP_NAME/foundry/self-evolution/ecp/implemented/.gitkeep"
touch "$APP_NAME/foundry/self-evolution/ecp/rejected/.gitkeep"
touch "$APP_NAME/foundry/self-evolution/regression/cases/.gitkeep"
touch "$APP_NAME/foundry/self-evolution/regression/fixtures/.gitkeep"
touch "$APP_NAME/foundry/self-evolution/upstream/proposed-to-plugin/.gitkeep"

# AGENTS.md
cat > "$APP_NAME/AGENTS.md" <<EOF
# Project Instructions

> ${DESCRIPTION}

This application is governed by the **eou-foundry** plugin. The plugin
provides EOU schemas, governance rules, audit skills, and validation
infrastructure. This application provides its domain-specific EOUs,
runtime state, and incidents that may feed back upstream as plugin ECPs.

## Foundry layer

The live Foundry instance lives at \`foundry/\`. Edit \`foundry/constitution.yml\`
to tailor invariants to this application's domain.

## Shared Memory

**Always write new instructions, rules, and memory to \`AGENTS.md\` only.**

Never modify \`CLAUDE.md\` or \`GEMINI.md\` directly — they only import \`AGENTS.md\`.
EOF

# CLAUDE.md and GEMINI.md as thin imports
echo "@AGENTS.md" > "$APP_NAME/CLAUDE.md"
echo "@AGENTS.md" > "$APP_NAME/GEMINI.md"

# .claude/settings.json (minimal — apps can add hooks as needed)
cat > "$APP_NAME/.claude/settings.json" <<'EOF'
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(./private/**)"
    ]
  }
}
EOF

# .gitignore
cat > "$APP_NAME/.gitignore" <<'EOF'
# Local Claude / IDE state
.claude/settings.local.json
.claude/CLAUDE.local.md
.claude/*.local.*
CLAUDE.local.md

# Python
__pycache__/
*.pyc
.venv/

# OS
.DS_Store

# Foundry runtime artifacts
foundry/runs/*
!foundry/runs/.gitkeep
foundry/audits/last-session.txt
EOF

# README
cat > "$APP_NAME/README.md" <<EOF
# ${APP_NAME}

${DESCRIPTION}

Governed by the [eou-foundry](https://github.com/xiaolai/eou-foundry) Claude
Code plugin. EOU schemas, rules, and audit skills come from the installed
plugin; runtime state (constitution, registry, EOUs, incidents) lives in
\`foundry/\`.

## Verify

\`\`\`bash
python3 \$(claude plugin path eou-foundry@xiaolai)/scripts/validate_foundry.py
\`\`\`
EOF

ok "scaffolded $APP_NAME/"

# --- git ---
if [ "$NO_GIT" = "0" ]; then
  (
    cd "$APP_NAME"
    git init -q -b main
    git add -A
    git commit -q -m "chore: initialize EOU-governed application from eou-foundry plugin

Scaffolded by /eou-foundry:init with plugin version $(cat "$PLUGIN_DIR/.claude-plugin/plugin.json" | python3 -c 'import json,sys; print(json.load(sys.stdin)[\"version\"])')."
  )
  ok "git repo initialized in $APP_NAME/"
else
  skip "git init skipped (--no-git)"
fi

# --- validate ---
echo
printf '── validate_foundry.py against new scaffold ──\n'
if ! ( cd "$APP_NAME" && python3 "$PLUGIN_DIR/scripts/validate_foundry.py" ); then
  err "validate_foundry.py failed on fresh scaffold — this is a plugin bug, please report"
  exit 4
fi

echo
ok "$APP_NAME/ is ready"
printf '  Next: cd %s && edit AGENTS.md, foundry/constitution.yml\n' "$APP_NAME"
