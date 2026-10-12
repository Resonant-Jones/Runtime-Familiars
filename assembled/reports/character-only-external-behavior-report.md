═══ Composition Report: test-character ═══

## Configuration

  Character pack:    test-character
  Behavior pack:     gentle-companion
  Relationship pack: (none — using inline)
  Worldline pack:    (none — using inline)

## Component Provenance

| # | Component | Source | Type | Overrides |
|---|-----------|--------|------|-----------|
| 1 | `character_core` | `/Volumes/Dev_SSD/Runtime-Familiars/tools/test_fixtures/valid/test-character/01_CHARACTER_CORE.md` | inline | `—` |
| 2 | `voice_and_language` | `/Volumes/Dev_SSD/Runtime-Familiars/tools/test_fixtures/valid/test-character/02_VOICE_AND_LANGUAGE.md` | inline | `—` |
| 3 | `behavior_rules` | `/Volumes/Dev_SSD/Runtime-Familiars/behavior-packs/gentle-companion/BEHAVIOR_PACK.md` | external | `—` |
| 4 | `boundaries` | `/Volumes/Dev_SSD/Runtime-Familiars/tools/test_fixtures/valid/test-character/05_BOUNDARIES.md` | inline | `—` |
| 5 | `example_dialogue` | `/Volumes/Dev_SSD/Runtime-Familiars/tools/test_fixtures/valid/test-character/09_EXAMPLE_DIALOGUE.md` | inline | `—` |

## Missing Components

  - `relationship_model` — not provided by character pack or external packs
  - `conflict_and_repair` — not provided by character pack or external packs
  - `initiative` — not provided by character pack or external packs
  - `world_and_lore` — not provided by character pack or external packs

## Assembly Order

```text
  character_core → voice_and_language → behavior_rules → boundaries → example_dialogue
```

Canonical order reference:

```text
  character_core → voice_and_language → relationship_model → behavior_rules → conflict_and_repair → initiative → world_and_lore → boundaries → example_dialogue
```

## Assembly Stats

  Total components:  5
  Inline sources:    4
  External sources:  1
  Overrides applied: 0
  Output characters: 9,792
  Output words:      1,335
