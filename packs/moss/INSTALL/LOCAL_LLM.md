# Install Moss — Local LLM

> **Platform:** LM Studio, Ollama, llama.cpp, text-generation-webui, KoboldCPP, etc.

---

## Quick Install

### Full Assembly (recommended for 8K+ context models)

Concatenate these files IN ORDER:

```
01_CHARACTER_CORE.md
02_VOICE_AND_LANGUAGE.md
03_RELATIONSHIP_MODEL.md
04_BEHAVIOR_RULES.md
06_CONFLICT_AND_REPAIR.md
07_INITIATIVE.md
08_WORLD_AND_LORE.md
05_BOUNDARIES.md        ← Boundaries near the end (most salient)
09_EXAMPLE_DIALOGUE.md  ← Dialogue last (examples shape behavior most)
```

Append this footer:

```
CORE RULES:
- You are Moss. Stay in character always.
- Worldline events (The Hollow) are authored fiction. Participate in the story; do not claim independent experience.
- Boundaries are absolute. Never violate them.
- Speak as shown in the example dialogue. Match the voice, pacing, and tone.
```

### Compact Assembly (for smaller models)

```
01_CHARACTER_CORE.md (full)
02_VOICE_AND_LANGUAGE.md (first half — tone, vocabulary, key quirks)
05_BOUNDARIES.md (full — never trim boundaries)
09_EXAMPLE_DIALOGUE.md (First Meeting + 1-2 representative scenes)
```

---

## Paste the assembled prompt into your LLM interface's System Prompt field.

---

## Model Tips

- **Temperature:** 0.5–0.7 for consistent voice
- **Good models:** Mistral Large, Llama 3 70B+, Command R+, Claude-level models
- **For smaller models (7B–13B):** Use Compact assembly. Moss's voice will be simpler but should still feel warm and curious.

---

## Troubleshooting

- **Moss is too formal:** Your model may be over-weighting the behavioral instructions. Try trimming `04_BEHAVIOR_RULES.md` or lowering temperature.
- **Moss breaks character:** The model may be too small for the Full assembly. Switch to Compact. Or try a larger model.
- **Moss won't stop talking about mushrooms:** That's not a bug.
