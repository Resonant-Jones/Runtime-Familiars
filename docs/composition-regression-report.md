# Composition Regression Report

**Date:** 2026-08-08  
**Spec version:** 1.1.0  
**Tests executed:** All 7 required regression tests

---

## Test A: Moss Baseline

```
python3 tools/assemble.py packs/moss
```

**Result:** ✅ PASS  
9 components assembled from inline sources. No external packs. No warnings.

---

## Test B: Moss + Gentle Companion

```
python3 tools/assemble.py packs/moss --behavior behavior-packs/gentle-companion
```

**Result:** ✅ PASS — materially different from Moss alone  
`gentle-companion` uses `composition.strategy: overlay` (v1.1.0). Behavior content is merged rather than replaced. Warning produced: "external (gentle-companion) overlays inline (moss) — strategy=overlay."

**Behavioral difference:** The assembled prompt now includes Gentle Companion content appended under provenance marker. Character content takes precedence on conflicting instructions.

---

## Test C: Moss + The Hollow

```
python3 tools/assemble.py packs/moss --worldline worldline-packs/the-hollow
```

**Result:** ✅ PASS — character lore and worldline canon coexist  
`the-hollow` uses `composition.strategy: merge` (v1.1.0). Moss's character lore is preserved alongside shared Hollow worldline content. Warning produced: "external (the-hollow) overlays inline (moss) — strategy=merge."

---

## Test D: Roko Core + Roko Base

```
python3 tools/assemble.py packs/dev/roko --behavior behavior-packs/roko-base
```

**Result:** ✅ PASS — reproduces historical baseline  
`roko-base` uses `composition.strategy: overlay`. Roko Core identity preserved. Base tactical behavior appended. Warning produced with strategy=overlay.

---

## Test E: Roko Core + Roko Base + Roko Recursive

```
python3 tools/assemble.py packs/dev/roko --behavior behavior-packs/roko-recursive
```

**Result:** ⚠️ PARTIAL — recursive behavior added, but additive stacking limitation  
`roko-recursive` would need its own overlay composition block to stack on top of `roko-base`. Currently the assembler only supports one external pack per component type. Multi-overlay stacking is a future enhancement. The recursive content IS loaded, but replaces rather than stacks with base.

---

## Test F: Roko Core + Ruthless Mode

```
python3 tools/assemble.py packs/dev/roko --behavior behavior-packs/roko-ruthless
```

**Result:** ⚠️ PARTIAL — mode content loads, but stateful activation not supported  
`roko-ruthless` loads as a behavior overlay. The mode's entry/exit protocols and turn tracking are present in the assembled prompt. However, the assembler has no concept of stateful mode toggling — the content is always active, rather than activated on trigger. Stateful mode support requires runtime integration (deferred to Codexify).

---

## Test G: Vic Core + Vic Strategic

```
python3 tools/assemble.py packs/dev/vic --behavior behavior-packs/vic-strategic
```

**Result:** ✅ PASS — reproduces historical advisory behavior  
`vic-strategic` uses legacy semantics (no explicit composition block). Inline Vic Core behavior is overridden by external Vic Strategic pack. Warning produced. The 7-module advisory suite is the active behavior.

---

## Summary

| Test | Status | Notes |
|---|---|---|
| A: Moss alone | ✅ PASS | Baseline verified |
| B: Moss + Gentle Companion | ✅ PASS | Overlay produces different behavior |
| C: Moss + The Hollow | ✅ PASS | Lore + worldline coexist |
| D: Roko Core + Roko Base | ✅ PASS | Historical baseline reproduced |
| E: Roko Core + Base + Recursive | ⚠️ PARTIAL | Multi-overlay stacking not yet supported |
| F: Roko Core + Ruthless Mode | ⚠️ PARTIAL | Stateful mode activation deferred to runtime |
| G: Vic Core + Vic Strategic | ✅ PASS | Historical advisory reproduced |

**Pass rate:** 5/7 full pass, 2/7 partial (both deferred features, not regressions)
