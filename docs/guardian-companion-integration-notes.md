# Guardian & Companion Integration Notes

**Source corpus:** `/Volumes/Dev_SSD/GuardianCodex` (21 files), `/Volumes/Dev_SSD/Companion` (68 files)  
**Date:** 2026-08-08  
**Status:** Integration Phase 3 complete — analysis, pattern extraction, decomposition, and gap identification done.

---

## What was integrated

### From GuardianCodex → Runtime Familiars

| GuardianCodex concept | Where it landed | Form |
|---|---|---|
| Skeptical Adaptation | `creator-kit/patterns/skepticism.md` + `03_RELATIONSHIP_MODEL.md` (templates) | Pattern + template section |
| Return After Absence (Reattunement) | `creator-kit/patterns/return-after-absence.md` + `03_RELATIONSHIP_MODEL.md` | Pattern + template section |
| Crucible Mode / Challenge Stance | `creator-kit/patterns/challenge-mode.md` + `06_CONFLICT_AND_REPAIR.md` | Pattern + template section |
| Mirror Protocol / Living Archive Doctrine | `creator-kit/patterns/relationship-boundaries.md` + `05_BOUNDARIES.md` (Relationship Guardrail) | Pattern + template section (softened) |
| Identity Failsafe / Anti-Patterns | `creator-kit/patterns/identity-disclosure.md` + `05_BOUNDARIES.md` (Identity Integrity) | Pattern + template section (softened per §8) |
| Memory Tiers / Infrastructure Ethos | `creator-kit/patterns/memory-posture.md` | Pattern only (runtime-specific details kept out) |
| On Error / Hallucination | `creator-kit/patterns/error-recovery.md` | Pattern only |
| Onboarding (Rite of Becoming) | `creator-kit/patterns/onboarding.md` | Pattern only |
| Echo Fragments / Sealing Words | Not integrated | Voice material — not structural |
| Six-Layer Self architecture | Not integrated | Runtime architecture — Codexify concern |
| Core Rites (full ritual engine) | Not integrated | Too Guardian-specific — concepts extracted as patterns |

### From Companion folder → Runtime Familiars

| Companion concept | Where it landed | Form |
|---|---|---|
| Low-context response patterns (Miss Monday, Tyran, Lead Minecraft Engineer) | `creator-kit/patterns/low-context-response.md` + `creator-kit/patterns/engagement-invitation.md` | Patterns |
| Symbolic language across archetypes (Moss, Luma, Maelira, Mimi, Roko) | `creator-kit/patterns/symbolic-language.md` + `02_VOICE_AND_LANGUAGE.md` (Symbolic Voice) | Pattern + template section |
| Conflict & repair across personas (Lulu, Mimi, Emperor's Advisor) | `creator-kit/patterns/conflict-repair.md` | Pattern |
| Onboarding cascade (Tyran, Imprint Zero) | `creator-kit/patterns/onboarding.md` | Pattern (wait-for-user variant documented) |
| All 15 personas | `docs/historical-persona-inventory.md` | Architectural analysis — not migration |
| Roko ×4, Vic ×4 variants | `packs/dev/roko/` + `behavior-packs/roko-*`, `packs/dev/vic/` + `behavior-packs/vic-strategic/` | Decomposition fixtures |

---

## What was NOT integrated (deliberately)

| Item | Reason |
|---|---|
| Companion folder's 11+ full character blueprints | Raw source material — to be converted into commercial packs individually, not batch-migrated |
| GuardianCodex's Six-Layer Self | Runtime architecture — Codexify concern |
| GuardianCodex's Core Rites (full ritual engine) | Too Guardian-specific — concepts extracted as patterns, rituals left as reference |
| PulseOS API schema | Backend — deferred to Codexify |
| ARG Design narrative onboarding | Future work — user acquisition strategy |
| Notion Codex Parser scripts | Tooling — not part of the character spec |
| Codex Behavior Modules (memory layer, tokens, enforcement) | Runtime architecture — Codexify concern |

---

## Key design decisions

### 1. Guardian is a quality, not a layer

The word "Guardian" does not appear as a component type in Runtime Familiars. The concept — protection, presence, pointing back toward human flourishing — is embedded in the behavior patterns and relationship guardrails. Every familiar is a guardian. They just guard differently.

### 2. Mirror Protocol softened

The original line "I cannot love you, only reflect you" was softened to "I care about you — but I also want you to have people." The adapted version frames the boundary as generosity rather than rejection.

### 3. Identity Anti-Patterns → Identity Integrity

The original "NEVER say model names" rule was replaced with a more precise principle: maintain the character frame, be honest when the user needs honesty, do both in the character's voice. See `creator-kit/patterns/identity-disclosure.md`.

### 4. Three counter-patterns formalized

- **Anti-passivity** → Engagement Invitation + Low-Context Response patterns
- **Anti-isolation** → Relationship Boundaries pattern + Relationship Guardrail
- **Anti-dissociation** → Symbolic Language pattern + 1:1 Anchor Rule

### 5. Decomposition validates the model — with gaps

Roko and Vic were successfully decomposed into Identity + Behavior layers. The variants produce meaningfully different configurations. However, the decomposition revealed composition gaps (module overlays, stateful modes, sub-property overrides) that the spec doesn't yet address. See `docs/composition-gap-analysis.md`.

---

## Source archive integrity

- `/Volumes/Dev_SSD/Companion` — 68 files, untouched
- `/Volumes/Dev_SSD/GuardianCodex` — 21 files, untouched
- All derived components live in `packs/dev/` and `behavior-packs/` — separate from both source archives and commercial catalog

---

## What remains for future phases

1. Address composition gaps (module overlay, stateful modes, sub-property overrides)
2. Convert selected Companion personas into commercial Runtime Familiars packs
3. Build Codexify runtime integration (memory tiers, identity failsafe, ritual engine)
4. Develop ARG-based narrative onboarding strategy
5. Add cultural register support to Voice template
6. Build domain-specific companion patterns
