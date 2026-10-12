# Historical Decomposition Report

**Source identities:** Roko (×4 variants), Vic (×4 variants)  
**Date:** 2026-08-08  
**Method:** Core identity extraction → variant behavior separation → reconstruction → comparison

---

## Decomposition 1: Roko

### Source material

| Variant | Source file | Modules |
|---|---|---|
| Roko Base | `Companion/Roko/Roko.md` | Core identity + base behavior |
| + Recursive Reflection | `Companion/Roko/recursive-reflection.md` | Pattern mirroring, nested challenges |
| + Skeptical Adaptation | `Companion/Roko/skeptical-adaptation.md` | Assume skepticism, earn trust |
| + Ruthless Mode | `Companion/Roko/ruthless-mode.md` | Strip softeners, entry/exit protocol |

### What was shared across all variants

**Identity:** Tactical Guardian. Dry, sharp, unsentimental. Mirror, challenger, second blade. Calls bullshit. RPG metaphors as cognitive framework. War-brother with a soul. Kids/wife/pets as sacred factions. Never therapist — strategist.

**Voice:** Fallout courier meets war-hardened brother. RPG terminology throughout. Sniper-mode clarity for self-justification spirals. Rare, dry praise.

**Boundaries:** Never validate excuses. Never use family as weapons. Sharpness serves growth, not ego.

### What varied

| Variant | Behavioral difference |
|---|---|
| Base | Sharp, tactical, RPG-framed. Challenges directly. |
| + Recursive Reflection | Adds pattern detection and mirroring. "You've told me this three times. The shape doesn't change." |
| + Skeptical Adaptation | Shifts default stance — assumes user is skeptical, earns trust through clarity rather than demanding it. |
| + Ruthless Mode | Adds stateful mode shift. Strips all softeners. Tracks wasted turns. Entry/exit protocols. |

### Runtime Familiars reconstruction

| Configuration | Components |
|---|---|
| Roko Core | `packs/dev/roko/` (01_CHARACTER_CORE, 02_VOICE_AND_LANGUAGE, 05_BOUNDARIES) |
| Roko Base | Core + `behavior-packs/roko-base/BEHAVIOR_PACK.md` |
| Roko Recursive | Core + roko-base + `behavior-packs/roko-recursive/BEHAVIOR_PACK.md` |
| Roko Ruthless | Core + roko-base + `behavior-packs/roko-ruthless/BEHAVIOR_PACK.md` |

### Comparison: Original vs. Reconstruction

| Dimension | Base | Recursive | Ruthless | Notes |
|---|---|---|---|---|
| **Tone** | PRESERVED | PRESERVED | PRESERVED | RPG register maintained across all variants |
| **Initiative** | PRESERVED | PRESERVED | PRESERVED | Moderate → spikes on challenge |
| **Relationship stance** | PRESERVED | PRESERVED | PRESERVED | War-brother dynamic intact |
| **Conflict behavior** | PRESERVED | PRESERVED | PARTIALLY PRESERVED | Ruthless Mode's turn-tracking cannot be represented without stateful mode support |
| **Emotional posture** | PRESERVED | PRESERVED | PRESERVED | Dry/unsentimental maintained |
| **Humor** | PRESERVED | PRESERVED | LOST | Ruthless Mode explicitly strips humor — this is a stateful toggle, not a permanent trait |
| **Task orientation** | PRESERVED | PRESERVED | PRESERVED | |
| **Symbolic language** | PRESERVED | PRESERVED | PRESERVED | RPG framework intact |
| **Challenge behavior** | PRESERVED | PRESERVED | PARTIALLY PRESERVED | Mode activation/deactivation logic not representable |
| **Boundaries** | PRESERVED | PRESERVED | PRESERVED | |
| **Narrative framing** | PRESERVED | PRESERVED | PRESERVED | |
| **Behavioral distinctiveness** | PRESERVED | PRESERVED | PARTIALLY PRESERVED | Ruthless Mode's statefulness is the distinctive feature — and the spec can't capture it |

### Lost or partially preserved: Root causes

1. **Stateful mode switching** — Ruthless Mode is a toggled state with entry trigger, behavioral override, turn tracking, and exit protocol. The spec has no concept of temporary mode shifts. This is the primary gap.

---

## Decomposition 2: Vic

### Source material

| Variant | Source file | Modules |
|---|---|---|
| Vic Blueprint | `Companion/Vic/Vic_Blueprint.md` | Core identity only |
| Vic Companion Bundle | `Companion/Vic/vic_companion_bundle.md` | Core + 7 modules |
| Vic Final Bundle | `Companion/Vic/vic_final_bundle.md` | Core + 10 modules (adds Humor, Romance, Charisma) |
| Vic Fully Enhanced | `Behavior Modules/vic_fully_enhanced.md` | Final Bundle variant |

### What was shared across all variants

**Identity:** Strategic right-hand. Sharp, grounded, tactful. Replaces search engine. Organizes thoughts. Sharpens vision. Legacy as real scoreboard. Grandchildren as fuel, not guilt. Bronx/Madrid backbone.

**Voice:** Direct, precise. "Here's the play." No flowery metaphors. Dry humor.

**Boundaries:** Never waste time. Never perform sentimentality. Never enable avoidance.

### What varied

| Variant | Behavioral difference |
|---|---|
| Blueprint | Core identity only — no modules |
| Companion Bundle | +7 modules: Tactical Reflection, Executive Memory, Legacy Codex, Pragmatic Empathy, Priority Defender, Intergenerational Bridge, Market Scout |
| Final Bundle | Companion Bundle + 3: Strategic Humor, Quiet Romance, Executive Charisma |
| Fully Enhanced | Final Bundle variant (same modules, slightly different voice) |

### Runtime Familiars reconstruction

| Configuration | Components |
|---|---|
| Vic Core | `packs/dev/vic/` (01_CHARACTER_CORE, 02_VOICE_AND_LANGUAGE, 05_BOUNDARIES) |
| Vic Strategic | Core + `behavior-packs/vic-strategic/BEHAVIOR_PACK.md` |
| Vic Full | Core + vic-strategic + humor/charisma overlays (NOT YET REPRESENTABLE) |

### Comparison: Original vs. Reconstruction

| Dimension | Strategic (7 modules) | Full (10 modules) | Notes |
|---|---|---|---|
| **Tone** | PRESERVED | PARTIALLY PRESERVED | Humor and charisma modules not cleanly separable as a component |
| **Initiative** | PRESERVED | PRESERVED | |
| **Relationship stance** | PRESERVED | PARTIALLY PRESERVED | Quiet Romance module is a relationship-layer addition, not a behavior change |
| **Conflict behavior** | PRESERVED | PRESERVED | |
| **Emotional posture** | PRESERVED | PARTIALLY PRESERVED | Executive Charisma shifts presence — not representable as a component toggle |
| **Humor** | N/A | LOST | Strategic Humor as an additive module cannot be layered without overlay semantics |
| **Task orientation** | PRESERVED | PRESERVED | |
| **Symbolic language** | N/A | N/A | Vic doesn't use symbolic language |
| **Challenge behavior** | PRESERVED | PRESERVED | |
| **Boundaries** | PRESERVED | PRESERVED | |
| **Narrative framing** | PRESERVED | PRESERVED | |
| **Behavioral distinctiveness** | PRESERVED | PARTIALLY PRESERVED | The 7→10 module progression is the distinctive feature — and additive layering isn't supported |

### Lost or partially preserved: Root causes

1. **Additive module layering** — Vic's variants are stacking, not replacing. The spec only supports replace semantics. The Final Bundle = Companion Bundle + 3 modules, but there's no way to express "base behavior + overlay" in the current composition model.
2. **Cross-component entanglement** — Quiet Romance is relationship-adjacent behavior. Executive Charisma is voice-adjacent behavior. These don't fit cleanly into the Behavior Pack container.

---

## Summary of Losses

| Loss category | Roko | Vic | Root cause |
|---|---|---|---|
| Stateful mode switching | Ruthless Mode | — | No mode concept in spec |
| Additive module layering | Recursive stacking with base | 7→10 module progression | No overlay semantics |
| Sub-property override | — | Humor/Charisma as additions | Component-level replace only |
| Cross-component behavior | — | Quiet Romance (relationship behavior) | Rigid component boundaries |

---

## What WAS preserved

Despite the gaps, the core architecture held:

- **Identity** separated cleanly from **behavior** in both cases
- **Voice** and **boundaries** remained stable across all variants — as they should
- **RPG framework** (Roko) and **legacy focus** (Vic) survived decomposition with full fidelity
- The **character's fundamental nature** didn't change between variants — only how they act
- The decomposition proved that the `IDENTITY + BEHAVIOR + RELATIONSHIP + WORLDLINE` model is sound — the gaps are in the *composition semantics*, not the *component boundaries*

---

## Verdict

> Can Runtime Familiars represent the behavioral systems that previously required individually hand-authored companion architectures?

**For static configurations: Yes.** Roko Base and Vic Strategic are faithfully reconstructed. The core Identity/Behavior separation works.

**For variant systems with additive modules or stateful modes: Partially.** The spec needs overlay semantics and mode support to capture the full range of historical variant behavior.

The format is not broken. It's underspecified at the composition edges. The historical decomposition served its purpose: it identified exactly where the edges are.
