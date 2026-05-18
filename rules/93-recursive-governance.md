---
description: Allow the Foundry to inspect and improve its own EOUs only through bounded governance (observe → diagnose → propose → simulate → regression → audit → human approval → deploy). Forbid self-edit + self-approve.
---

# Recursive Governance Rule

The Foundry may recursively inspect and improve its own EOUs, but only through bounded governance.

Allowed:

```text
observe → diagnose → propose → simulate → regression test → audit → human approval → deploy
```

Forbidden:

```text
observe → edit itself → approve itself
```

No EOU may be the sole judge of changes to itself.
