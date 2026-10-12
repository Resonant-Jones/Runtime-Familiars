═══ Composition Report: moss ═══

## Configuration

  Character pack:    moss
  Behavior pack:     gentle-companion
  Relationship pack: (none — using inline)
  Worldline pack:    the-hollow

## Component Provenance

| # | Component | Source | Type | Overrides |
|---|-----------|--------|------|-----------|
| 1 | `character_core` | `/Volumes/Dev_SSD/Runtime-Familiars/packs/moss/01_CHARACTER_CORE.md` | inline | `—` |
| 2 | `voice_and_language` | `/Volumes/Dev_SSD/Runtime-Familiars/packs/moss/02_VOICE_AND_LANGUAGE.md` | inline | `—` |
| 3 | `relationship_model` | `/Volumes/Dev_SSD/Runtime-Familiars/packs/moss/03_RELATIONSHIP_MODEL.md` | inline | `—` |
| 4 | `behavior_rules` | `/Volumes/Dev_SSD/Runtime-Familiars/packs/moss/04_BEHAVIOR_RULES.md` | inline | `/Volumes/Dev_SSD/Runtime-Familiars/behavior-packs/gentle-companion/BEHAVIOR_PACK.md` |
| 5 | `conflict_and_repair` | `/Volumes/Dev_SSD/Runtime-Familiars/packs/moss/06_CONFLICT_AND_REPAIR.md` | inline | `—` |
| 6 | `initiative` | `/Volumes/Dev_SSD/Runtime-Familiars/packs/moss/07_INITIATIVE.md` | inline | `—` |
| 7 | `world_and_lore` | `/Volumes/Dev_SSD/Runtime-Familiars/packs/moss/08_WORLD_AND_LORE.md` | inline | `/Volumes/Dev_SSD/Runtime-Familiars/worldline-packs/the-hollow/WORLDLINE.md` |
| 8 | `boundaries` | `/Volumes/Dev_SSD/Runtime-Familiars/packs/moss/05_BOUNDARIES.md` | inline | `—` |
| 9 | `example_dialogue` | `/Volumes/Dev_SSD/Runtime-Familiars/packs/moss/09_EXAMPLE_DIALOGUE.md` | inline | `—` |

## Override History

The following inline components override external pack components:

### `behavior_rules`
- **Resolved value from:** `/Volumes/Dev_SSD/Runtime-Familiars/packs/moss/04_BEHAVIOR_RULES.md`
- **Overrides:** `/Volumes/Dev_SSD/Runtime-Familiars/behavior-packs/gentle-companion/BEHAVIOR_PACK.md`
- **Rule:** Inline character configuration overrides imported external packs.

### `world_and_lore`
- **Resolved value from:** `/Volumes/Dev_SSD/Runtime-Familiars/packs/moss/08_WORLD_AND_LORE.md`
- **Overrides:** `/Volumes/Dev_SSD/Runtime-Familiars/worldline-packs/the-hollow/WORLDLINE.md`
- **Rule:** Inline character configuration overrides imported external packs.

## Assembly Warnings

  ⚠️  Component 'behavior_rules': inline (moss) overrides external (gentle-companion)
  ⚠️  Component 'world_and_lore': inline (moss) overrides external (the-hollow)

## Assembly Order

```text
  character_core → voice_and_language → relationship_model → behavior_rules → conflict_and_repair → initiative → world_and_lore → boundaries → example_dialogue
```

Canonical order reference:

```text
  character_core → voice_and_language → relationship_model → behavior_rules → conflict_and_repair → initiative → world_and_lore → boundaries → example_dialogue
```

## Assembly Stats

  Total components:  9
  Inline sources:    9
  External sources:  0
  Overrides applied: 2
  Output characters: 60,326
  Output words:      9,744
