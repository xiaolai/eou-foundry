# Plugin Dev Docs

Design memory for the **eou-foundry** plugin itself: foundations,
architecture, doctrine, and vocabulary. These docs describe the engine
that governs consuming applications.

## Current canonical docs

| # | File | Purpose |
|---|---|---|
| 01 | `01-foundations.md` | Core EOU and Foundry concepts |
| 02 | `02-architecture.md` | Plugin layout and engine/instance separation |
| 03 | `03-doctrine.md` | Design and maintenance doctrine for EOUs |
| 04 | `04-vocabulary-principles.md` | Vocabulary discipline and precedence rules |

## historical/

Pre-split engineering records from when the Foundry was part of the
book-workshop monolith (before commit `19e32d0` in the workshop and
plugin v0.1.0 here). These describe the foundry-engine evolution and
are preserved as evidence, not authority:

- `historical/12-independent-framework-audit-and-fixes.md` — fresh framework
  audit after EOU operationalization; identifies the layering issues that
  drove the V2 Foundry redesign.
- `historical/12a-v2.1-source-audit.md` — independent codebase quality
  audit of the v2.1 combined repo; the source defects this audit caught
  drove the v2.1-fixed → v2.2 → v2.3 cycle.

Both carry deprecation banners. They were moved here from
`book-workshop/dev-docs/` as part of the engine-as-reference-not-copy
refactor (plugin ECP-0003, v0.5.0) — their subject is the foundry
engine, not the workshop, so this is their correct home.

For current state, read `00`–`04` in this directory and the plugin's
`README.md`. For the workshop-side dev-docs (A2B engine, workshop
architecture, build workflow), see `book-workshop/dev-docs/`.
