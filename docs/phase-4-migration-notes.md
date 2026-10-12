# Phase 4 Migration Notes

**From:** Spec 1.0.0 (Phase 2/3)  
**To:** Spec 1.1.0 (Phase 4 — Composition Engine v2)  
**Date:** 2026-08-08

---

## What Changed

### Spec (SPEC.md)

Added sections 10–15:
- §10: Composition Strategies (replace, merge, overlay)
- §11: Field Operations (set, add, remove, reinforce, deemphasize, append, prepend, inherit)
- §12: Stateful Modes (activation types, exit semantics, stacking, provenance)
- §13: Provenance Model v2 (field-level tracking)
- §14: Conflict Resolution (precedence rules, conflict reporting)
- §15: Composition Plan Format (human-readable + machine-readable)

Renumbered: §10→16 (Extension Points), §11→17 (Validation Checklist)

### Assembler (tools/assemble.py)

- `resolve_component()` now reads `composition.strategy` from external pack frontmatter
- `overlay` and `merge` strategies combine content rather than replacing it
- `legacy` (or unspecified) preserves original replace behavior
- New `_apply_overlay()` helper for content merging with provenance markers

### Fixture Packs

| Pack | Version | Composition | Strategy |
|---|---|---|---|
| `gentle-companion` | 1.0.0 → 1.1.0 | Added | `overlay` |
| `the-hollow` | 1.0.0 → 1.1.0 | Added | `merge` |
| `roko-base` | 0.1.0 | Added | `overlay` |

---

## Backward Compatibility

All existing Phase 2/3 packages remain valid. Packages without explicit `composition` blocks use **legacy semantics**: inline components take precedence over external packs of the same type. No existing behavior changes.

---

## Migration Path

To adopt v2 composition for an existing pack:

1. Add a `composition` block to the pack's YAML frontmatter:

```yaml
composition:
  strategy: overlay  # or merge, or replace
```

2. Bump the pack version (minor bump for composition metadata addition).
3. Existing packages without composition blocks continue to work — no migration required.

---

## Known Limitations (deferred to future phases)

- **Multi-overlay stacking**: Only one external pack per component type is supported. Stacking multiple overlays (e.g., roko-base + roko-recursive simultaneously) requires future assembler enhancement.
- **Stateful mode runtime support**: Mode entry/exit toggling requires runtime integration (deferred to Codexify). Mode content loads but is always active.
- **Field-level operation parsing**: The assembler detects composition strategy and applies overlay/merge semantics, but does not parse individual field operations (set, add, reinforce, etc.) from YAML. Full field-level composition requires a future assembler version.
- **Conflict detection**: Precedence rules are defined in the spec but automatic conflict detection is not yet implemented in the assembler.

---

## Files Added in Phase 4

```
docs/
├── composition-semantics-v2.md
├── stateful-modes.md
├── provenance-v2.md
├── composition-regression-report.md
└── phase-4-migration-notes.md
```

## Files Modified in Phase 4

```
SPEC.md                         (+ sections 10-15, renumbered 16-17)
tools/assemble.py               (+ composition strategy detection, overlay/merge support)
behavior-packs/gentle-companion/BEHAVIOR_PACK.md   (+ composition block, v1.0.0→1.1.0)
worldline-packs/the-hollow/WORLDLINE.md            (+ composition block, v1.0.0→1.1.0)
behavior-packs/roko-base/BEHAVIOR_PACK.md          (+ composition block)
```
