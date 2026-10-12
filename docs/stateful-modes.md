# Stateful Modes

**Spec version:** 1.1.0  
**Date:** 2026-08-08

---

## Overview

Some behaviors are not static traits — they are stateful shifts that activate, run, and exit. Stateful modes provide explicit support for these behavioral toggles.

---

## Mode Declaration

```yaml
modes:
  ruthless:
    activation:
      type: explicit
    overlay:
      pack: roko-ruthless
    exit:
      type: explicit
    stacking: false
```

---

## Activation Types

| Type | Meaning | Example |
|---|---|---|
| `explicit` | User activates by command | "Enter ruthless mode" |
| `session` | Persists for current session | Activated at session start |
| `contextual` | Eligible when context applies | User is circling a truth |
| `runtime-controlled` | Host application controls | Codexify activates crucible mode |

Contextual activation must remain conservative and inspectable. Vague psychological inference is not a valid trigger.

---

## Exit Semantics

| Type | Meaning |
|---|---|
| `explicit` | User exits by command |
| `automatic` | Purpose fulfilled (truth named, pattern broken) |
| `session-end` | Mode ends with session |
| `runtime-controlled` | Host application controls exit |

A mode without valid exit semantics fails validation.

---

## Mode Stacking

Default: `stacking: false`. Modes do not stack unless explicitly enabled with a defined conflict-resolution order.

---

## Historical Validation

Roko's Ruthless Mode and GuardianCodex's Crucible Mode served as the primary historical evidence for this feature. Both are stateful toggles with entry triggers, behavioral overrides, and exit protocols.
