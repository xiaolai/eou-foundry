---
description: Enforce faceted EOU classification (function + target + automation + authority + risk + lifecycle). Load when designing, auditing, or promoting EOUs in foundry/.
---

# EOU Foundry V2 Rules

The canonical EOU layer is `foundry/`.

An EOU is an operational hypothesis, not merely a prompt, checklist, SOP, or script.

Every EOU must use faceted classification:

```text
function + target_object + automation_mode + authority_level + risk_level + lifecycle_stage
```

Do not use a single vague type label to decide authority or risk.

## Canonical objective

Optimize for reduced hidden failure, inspectability, truthfulness, schema coherence, traceability, and human responsibility.

Do not optimize for speed, fluency, fewer warnings, higher apparent pass rate, or number of EOUs created.
