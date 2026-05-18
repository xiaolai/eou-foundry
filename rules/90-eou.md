---
description: Require new or changed workflows to be defined as EOU cards under foundry/eous/ or foundry/meta-eous/. Forbids the deprecated root-level eous/ directory.
---

# Executable Operating Unit Rule

The canonical EOU layer is `foundry/`.

When adding or changing workflows, define or update an EOU card under:

```text
foundry/eous/
foundry/meta-eous/
```

Do not use the superseded root-level `eous/` directory.

Every EOU must use faceted classification:

```text
function + target_object + automation_mode + authority_level + risk_level + lifecycle_stage
```

Every EOU must declare purpose, non-goals, operating hypothesis, inputs, context manifest, execution, outputs, validation, failure modes, escalation, responsibility, versioning, and blast radius.

Generating EOUs must additionally declare generation envelope, generation budget, registry diff, minimality test, operational-value test, and counter-generation.
