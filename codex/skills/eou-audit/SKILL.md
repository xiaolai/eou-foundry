---
name: eou-audit
description: Audit EOU specs for Foundry V2 faceted classification, authority limits, schemas, validation, failure modes, trace, blast radius, and responsibility ownership.
---

# EOU Audit

Audit an EOU card or the whole `foundry/` directory.

Read:

- `foundry/constitution.yml`
- `foundry/governance.yml`
- `foundry/failure-taxonomy.yml`
- `schemas/eou.schema.yml`
- target EOU card(s)

Run deterministic validation when possible:

```bash
python3 scripts/validate_foundry.py
```

Check:

1. Does the EOU use faceted classification?
2. Is its authority level appropriate for its function and risk?
3. Is the EOU small enough to execute and test?
4. Is the non-goal explicit?
5. Does it have a context manifest?
6. Are stop conditions and repair actions concrete?
7. Does it separate deterministic, judgment, and decision responsibilities?
8. Does it preserve trace?
9. Is human approval required where responsibility cannot be delegated?
10. If generating, does it include generation envelope, budget, registry diff, minimality, operational value, and counter-generation?
11. Does it avoid treating polished output as proof of valid execution?

Write findings to:

`audits/eou-audits/eou-audit.md`
