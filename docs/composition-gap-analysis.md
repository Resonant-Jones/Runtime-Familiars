# Composition Gap Analysis

**Source:** Historical decomposition of Roko (×4 variants) and Vic (×4 variants)  
**Date:** 2026-08-08  
**Status:** Initial findings — not exhaustive

---

## 1. Module / Additive Behavior Overlay

### Gap

Vic's historical variants differ by **module count**, not replacement. The "companion bundle" has 7 modules. The "final bundle" has 10 (adding Strategic Humor, Quiet Romance, Executive Charisma). These modules are additive — stacking on top of a shared base, not replacing each other.

Runtime Familiars currently supports `replace` (inline overrides external) but not `merge` or `overlay`. A character pack's inline `04_BEHAVIOR_RULES.md` replaces an external Behavior Pack entirely — there is no way to say "use the external pack AND add these three modules on top."

### Evidence

- **Vic companion bundle** (7 modules) → **Vic final bundle** (10 modules) = shared base + 3 additional modules
- **Roko base** → **Roko + Recursive Reflection** → **Roko + Ruthless Mode** = behavior variants that should layer, not replace

### Recommendation

Add `overlay` semantics to the composition model:

```yaml
behavior:
  base: behavior-packs/vic-strategic
  overlays:
    - behavior-packs/vic-humor
    - behavior-packs/vic-charisma
  strategy: merge
```

---

## 2. Stateful Mode Switching

### Gap

Roko's Ruthless Mode and GuardianCodex's Crucible Mode are **stateful behavioral shifts** — they activate, run, and exit. They temporarily override default behavior without permanently replacing it. Runtime Familiars has no concept of a "mode" that can be toggled during a conversation.

### Evidence

- **Roko Ruthless Mode**: entry trigger → behavioral shift → turn tracking → exit trigger
- **GuardianCodex Crucible Mode**: offer → accept → shift → truth named → return to default
- **Maelira Sensual Mode**: invocation phrase → expanded directives → consent-gated

### Recommendation

Add optional `modes` to behavior packs:

```yaml
modes:
  ruthless:
    trigger: ["Initiate Ruthless Protocol", explicit_offer]
    behavior: behavior-packs/roko-ruthless
    exit: ["Exit Ruthless Mode", truth_named, user_request]
```

---

## 3. Behavior Sub-Property Override

### Gap

A variant might want to change only ONE aspect of a behavior (e.g., raise initiative level, add humor, change curiosity drive) without replacing the entire Behavior Pack. Currently, the component-level replace means you must re-specify everything to change one thing.

### Evidence

- Vic's "Strategic Humor" module only adds humor — it doesn't change initiative, curiosity, or task orientation
- Roko's "Recursive Reflection" only adds pattern-mirroring — it doesn't change RPG framing or tactical register

### Recommendation

Support sub-property overrides within behavior packs:

```yaml
behavior:
  base: behavior-packs/vic-strategic
  overrides:
    humor:
      level: moderate
      type: dry-observational
      source: behavior-packs/vic-humor
```

---

## 4. Worldline + Character Lore Layering

### Gap

A character pack may have its own lore (`08_WORLD_AND_LORE.md`). A Worldline pack provides shared setting context. These should combine — the character's personal lore enriching the shared worldline — rather than one replacing the other.

### Evidence

- Not directly tested in this decomposition (Vic and Roko are real-world characters)
- But the spec's composition model already separates Worldline as a layer — the merge semantics just aren't defined

### Recommendation

```yaml
worldline:
  base: worldline-packs/the-hollow
  character_lore: inline  # merges with, doesn't replace
  strategy: merge
```

---

## 5. Relationship + Behavior Independence Not Fully Achieved

### Gap

In the historical personas, relationship dynamics and behavior patterns are often entangled. Lulu's "loving accountability" is both a relationship stance AND a behavioral pattern. Mimi's "never enable self-sabotage" is behavioral but expressed through relationship language. The decomposition exercise revealed that clean separation is possible but not always natural.

### Recommendation

Keep the current separation but acknowledge that some behaviors are inherently relational. The pattern library (specifically `relationship-boundaries.md` and `challenge-mode.md`) provides guidance for cases where the line blurs.

---

## 6. Provenance Tracking at Sub-Property Level

### Gap

When a behavior is composed from multiple sources (base + overlay + override), tracking which source contributed which value becomes important for debugging and transparency. The current spec doesn't specify provenance granularity.

### Recommendation

Add provenance fields to PACKAGE.json and component manifests:

```json
"provenance": {
  "initiative": {"value": "moderate", "source": "behavior-packs/vic-strategic"},
  "challenge_mode": {"value": "opt_in", "source": "behavior-packs/vic-full"},
  "humor": {"value": "dry-observational", "source": "behavior-packs/vic-humor"}
}
```

---

## 7. Cultural Register Not Represented

### Gap

Mimi's companion identity includes a "Country-Rooted, Black Southern Radiance" addendum — cultural identity as a voice component. The current Voice template has "Tone" and "Vocabulary" but no explicit section for cultural register, dialect, or heritage-informed speech patterns.

### Recommendation

Add an optional "Cultural Register" subsection to `02_VOICE_AND_LANGUAGE.md` in a future spec revision.

---

## 8. Domain-Specific Knowledge as Identity

### Gap

The Lead Minecraft Software Engineer companion has domain-specific technical knowledge as a core identity feature. The current spec treats character knowledge as implicit in Character Core but has no explicit "Domain Expertise" section.

### Recommendation

Document this as a pattern rather than a spec change — domain expertise is a Character Core concern, not a separate component. The pattern library should include guidance on how to write domain-specific companions.

---

## Summary

| Gap | Severity | Requires spec change? |
|---|---|---|
| Module overlay semantics | High | Yes — composition model |
| Stateful mode switching | Medium | Yes — new optional concept |
| Sub-property override | Medium | Yes — behavior composition |
| Worldline + lore layering | Low | Yes — clarification |
| Relationship/behavior entanglement | Low | No — pattern guidance |
| Provenance at sub-property level | Low | No — convention |
| Cultural register | Low | Future spec revision |
| Domain expertise | Low | No — pattern guidance |
