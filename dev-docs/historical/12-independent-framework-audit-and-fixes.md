# Independent Framework Audit and Fixes

> **Historical — superseded by Foundry-first layout.** This audit was performed
> on the pre-refactor tree (pre-Foundry-V2 reorganization). References to root-
> level `eous/` and `scripts/validate_eous.py` describe artifacts that have
> since been moved (to `foundry/eous/`) or deleted (the wrapper script). Kept
> for historical reference; for current canonical state see
> `00-canonical-decisions.md` and `13-eou-foundry-v2-redesign.md`.

This file records a fresh audit pass after the EOU abstraction was added to the workshop.

## Audit posture

The framework was audited as a third-party system, not as an explanation of prior decisions.

The test question was:

> Does the workshop actually operationalize its own claim that messy human workflows should become bounded, auditable EOUs?

## Problems found

1. **Reader-state drift**
   - Multiple chapter cards and TOC acts referenced `S5_SYSTEM_REDESIGN`, but `book/reader-states.yml` did not define that state.

2. **Story-device registry drift**
   - `book/mirror-artifacts.yml` referenced `presentation-hiding-weak-strategy`, but there was no corresponding card.

3. **Duplicate / stale mirror cards**
   - Older duplicate mirror artifact cards remained (`working-code-nobody-understands`, `polished-essay-with-no-discovery`) while newer canonical cards were being used elsewhere.

4. **Device-category pollution**
   - `book/analogy-bank.yml` still contained non-analogy story-device sections even though V2.1 now has dedicated files for mirror artifacts, paired scenes, metaphor upgrades, motifs, and protocol scenes.

5. **Validator blind spots**
   - `validate_book.py` did not catch unknown reader-state references or registry-to-card mismatches.

6. **Packaged compiled artifacts**
   - `__pycache__` and `.pyc` files were present in the archive after syntax checks.

7. **EOU concept not yet operationalized**
   - The EOU abstraction existed in `dev-docs/11-executable-operating-units.md`, but there were no EOU cards, no EOU contract, no validator, and no Claude skill for EOU auditing.

## Fixes applied

1. Added `S5_SYSTEM_REDESIGN` to the seeded book and template reader-state files.
2. Canonicalized mirror artifacts and added the missing `presentation-hiding-weak-strategy` card.
3. Removed stale duplicate mirror artifact cards.
4. Cleaned `book/analogy-bank.yml` so it only contains analogy-related data.
5. Extended `scripts/validate_book.py` to catch:
   - unknown reader-state references in TOC and chapter cards;
   - story-device registry IDs without matching cards;
   - duplicate registry IDs.
6. Extended `scripts/validate_workshop.py` to:
   - clean compiled artifacts after syntax checks;
   - validate the dev-docs index;
   - validate that no `__pycache__` or `.pyc` artifacts remain;
   - run EOU validation.
7. Added an operational EOU layer:
   - `foundry/engine/eou-system.md`
   - `foundry/engine/eou-contract.md`
   - `eous/compile-chapter.yml`
   - `eous/audit-chapter.yml`
   - `eous/validate-book.yml`
   - `templates/eou-template/eou.yml`
   - `scripts/validate_eous.py`
   - `.claude/rules/90-eou.md`
   - `.claude/skills/eou-audit/SKILL.md`

## Remaining boundaries

The workshop still distinguishes:

```text
deterministic validation ≠ literary quality
chapter scaffold ≠ publication prose
Claude skill audit ≠ human approval
```

Those are not defects. They are responsibility boundaries.
