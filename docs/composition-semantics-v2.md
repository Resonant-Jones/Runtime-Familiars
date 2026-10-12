# Composition Semantics v2

**Spec version:** 1.1.0  
**Date:** 2026-08-08  
**Status:** Published — replaces Phase 2/3 composition model

---

## Overview

Composition Engine v2 upgrades Runtime Familiars from component-level replacement to deterministic, inspectable field-level composition. Three strategies (`replace`, `merge`, `overlay`) plus eight field operations provide expressive modularity without losing legibility.

---

## Three Composition Strategies

### Replace

Incoming component entirely supersedes the target component. The replaced source remains visible in provenance.

```yaml
composition:
  strategy: replace
  target: behavior_rules
```

### Merge

Combine structured fields from multiple compatible sources. Default for worldline + character lore.

```yaml
composition:
  strategy: merge
```

### Overlay

Modify selected aspects of an existing component without replacing it. Primary mechanism for additive behavior modules.

```yaml
composition:
  strategy: overlay
  target: behavior_rules
operations:
  humor: {op: add, value: dry-observational}
  initiative: {op: set, value: high}
```

---

## Eight Field Operations

| Operation | Effect |
|---|---|
| `set` | Replace a field value |
| `add` | Introduce a new capability |
| `remove` | Disable/remove an optional property |
| `reinforce` | Declare compatible intent from two sources |
| `deemphasize` | Reduce salience without removal |
| `append` | Add to end of list/instruction block |
| `prepend` | Add to beginning of list/instruction block |
| `inherit` | Explicitly preserve previous value |

---

## Precedence Rules

| Priority | Source |
|---|---|
| 1 | Runtime mode overlay |
| 2 | Explicit user-selected overlay |
| 3 | Character-local override |
| 4 | External package default |
| 5 | Spec default |

---

## Backward Compatibility

Packages without explicit `composition` blocks use **legacy semantics**: inline components take precedence over external packs of the same type. No existing package behavior changes.
