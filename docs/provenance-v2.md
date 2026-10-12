# Provenance Model v2

**Spec version:** 1.1.0  
**Date:** 2026-08-08

---

## Overview

Provenance v2 upgrades tracking from component-level to field-level. Every resolved value carries its full origin chain: active source, replaced sources, operation used, and conflict resolution.

---

## Field-Level Provenance

```yaml
resolved:
  behavior:
    initiative:
      value: high
      source: behavior-packs/roko-recursive
      previous:
        value: moderate
        source: packs/dev/roko
    curiosity:
      value: high
      sources: [packs/dev/roko, behavior-packs/roko-recursive]
      resolution: reinforced
    challenge_mode:
      value: opt_in
      source: behavior-packs/roko-recursive
      operation: add
```

---

## Required Fields Per Resolved Value

- **active value** — currently in effect
- **contributing sources** — all packs that contributed
- **replaced values** — previous values overridden
- **operation used** — the operation that produced this value
- **composition strategy** — the strategy governing resolution
- **conflict resolution** — how conflicts were resolved (if applicable)

---

## Composition Plan Output

Human-readable summary produced before runtime prompt generation:

```text
Character: Roko
Base Behavior: roko-base
Applied Overlay: roko-recursive
Active Mode: none

Resolved:
  initiative → high (set by roko-recursive, was moderate)
  pattern_mirroring → enabled (added)
  curiosity → high (reinforced: roko-core + roko-recursive)

Conflicts: none
```

The same data is available as structured JSON for tooling.
