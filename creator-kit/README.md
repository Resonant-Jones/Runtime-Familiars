# Runtime Familiars — Creator Kit

Everything you need to build a portable AI identity pack.

---

## What's Here

| Directory | Purpose |
|-----------|---------|
| [`character-pack/`](character-pack/) | Templates for a complete character pack |
| [`behavior-pack/`](behavior-pack/) | Template for a standalone Behavior Pack |
| [`relationship-pack/`](relationship-pack/) | Template for a standalone Relationship Pack |
| [`worldline/`](worldline/) | Template for a Worldline (narrative continuity layer) |

---

## Quick Start: Build Your First Character

1. **Copy the template:**
   ```bash
   cp -r creator-kit/character-pack/ packs/my-character/
   ```

2. **Fill in the required files** (marked REQUIRED in each template):
   - `01_CHARACTER_CORE.md` — Who are they?
   - `02_VOICE_AND_LANGUAGE.md` — How do they talk?
   - `05_BOUNDARIES.md` — What won't they do?
   - `09_EXAMPLE_DIALOGUE.md` — Show them in conversation.

3. **Add optional components** as your character needs them.

4. **Write installation profiles** in `INSTALL/` so users can deploy your character.

5. **Validate** against the checklist in [SPEC.md](../SPEC.md#11-validation-checklist).

---

## Design Principles

Read the [Package Format Specification](../SPEC.md) before you start. Key points:

- **No platform-specific instructions in component bodies.** Platform adaptation lives in `INSTALL/`.
- **Assume the lowest common denominator.** A text-only LLM with a system prompt.
- **Concrete examples beat abstract instructions.** `09_EXAMPLE_DIALOGUE.md` is the most important file.
- **Boundaries go last (or close to last).** Hard constraints should be most salient to the model.
- **Components are composable.** Don't lock your character to a specific behavior or relationship.

---

## The Composition Model

```
Character = Identity + Behavior + Relationship + Worldline
```

Your character pack provides the **Identity** layer. Behavior, Relationship, and Worldline can be:

- **Included inline** (files in the pack directory) — self-contained, no dependencies.
- **Left empty** — the character works without them, just less richly.
- **Provided externally** — the user pairs your character with a standalone Behavior/Relationship/Worldline pack.

Design your character so it works with **any** compatible Behavior, Relationship, or Worldline.

---

## File Reference

| File | Required? | What It Contains |
|------|-----------|-----------------|
| `00_READ_ME_FIRST.md` | REQUIRED | Overview, quick start, composition tips |
| `01_CHARACTER_CORE.md` | REQUIRED | Name, personality, background, motivations |
| `02_VOICE_AND_LANGUAGE.md` | REQUIRED | Tone, vocabulary, humor, speech patterns |
| `03_RELATIONSHIP_MODEL.md` | OPTIONAL | How the character relates to the user |
| `04_BEHAVIOR_RULES.md` | OPTIONAL | Behavioral architecture and patterns |
| `05_BOUNDARIES.md` | REQUIRED | Hard constraints, prohibited behaviors |
| `06_CONFLICT_AND_REPAIR.md` | OPTIONAL | Disagreement and reconciliation handling |
| `07_INITIATIVE.md` | OPTIONAL | Proactivity and autonomy configuration |
| `08_WORLD_AND_LORE.md` | OPTIONAL | Setting, lore, canonical events |
| `09_EXAMPLE_DIALOGUE.md` | REQUIRED | Representative conversations |
| `10_STARTER_SCENARIOS.md` | RECOMMENDED | Entry points for new users |
| `PACKAGE.json` | RECOMMENDED | Machine-readable manifest |
| `LICENSE.md` | REQUIRED | License terms |

---

## After You Build

1. Validate against the checklist.
2. Write all four installation profiles.
3. Test on at least two platforms.
4. Get someone who doesn't know the character to try the quick start.
5. Iterate based on their experience.

---

*See the [Moss sample pack](../packs/moss/) for a complete reference implementation.*
