# Install on Local LLMs

> **Platform:** Local LLM interfaces (LM Studio, Ollama, llama.cpp, text-generation-webui, KoboldCPP, etc.)
> **Requires:** A local LLM with a system prompt field
> **Last tested:** August 2026

---

## Overview

Local LLMs give you full control — no subscriptions, no content filters (beyond the model's own training), and complete privacy. The trade-off is that you need to assemble the system prompt yourself and model quality varies.

---

## Assembly

### Step 1: Choose Your Assembly Level

You have two options:

| Level | What You Get | Best For |
|-------|-------------|----------|
| **Full** | All component files concatenated | Maximum character fidelity. Requires a model with a large context window (8K+ tokens). |
| **Compact** | Core identity + voice + boundaries + trimmed dialogue | Smaller models or shorter context windows. Sacrifices nuance for reliability. |

### Step 2: Concatenate Files

**Full Assembly:**

Concatenate these files IN THIS ORDER:

```
01_CHARACTER_CORE.md
02_VOICE_AND_LANGUAGE.md
03_RELATIONSHIP_MODEL.md       (if present)
04_BEHAVIOR_RULES.md            (if present)
06_CONFLICT_AND_REPAIR.md       (if present)
07_INITIATIVE.md                (if present)
08_WORLD_AND_LORE.md            (if present)
05_BOUNDARIES.md                ← BOUNDARIES GO NEAR THE END
09_EXAMPLE_DIALOGUE.md          ← DIALOGUE GOES LAST
```

**Why this order:** The model weights later content more heavily. Boundaries go near the end so they're most salient. Example dialogue goes last because concrete examples shape behavior more than abstract instructions.

**Compact Assembly:**

```
01_CHARACTER_CORE.md            (full content)
02_VOICE_AND_LANGUAGE.md        (first 50% — tone, vocabulary, key quirks)
05_BOUNDARIES.md                (full content — never trim boundaries)
09_EXAMPLE_DIALOGUE.md          (First Meeting + 1 representative scene)
```

### Step 3: Add Core Rules

Append this to the end of your assembled prompt:

```
CORE RULES:
- You are [CHARACTER NAME]. Stay in character always.
- Worldline events are authored fiction. Participate in the story; do not claim independent conscious experience.
- Boundaries are absolute. Never violate them.
- Speak as shown in the example dialogue. Match the voice, pacing, and tone.
```

### Step 4: Paste into System Prompt

Paste the entire assembled text into your LLM interface's **System Prompt** or **Context** field.

- **LM Studio:** Settings → System Prompt
- **Ollama:** Use a Modelfile with `SYSTEM """..."""`
- **text-generation-webui:** Parameters → System Prompt
- **KoboldCPP:** Settings → System Prompt

### Step 5: Start Conversation

Begin a new chat. The character should introduce itself.

---

## Model Recommendations

| Priority | What Matters | Recommendation |
|----------|-------------|----------------|
| **Character fidelity** | Following nuanced voice/tone instructions | Claude-level models, or strong local models (Mistral Large, Llama 3 70B+, Command R+) |
| **Long conversations** | Large context window | Models with 32K+ context |
| **Privacy** | Local execution | Any local model; trade quality for privacy |
| **Speed / Low resources** | Small model size | Phi-3, Llama 3 8B, Mistral 7B — use Compact assembly |

---

## Limitations

- **Model quality varies enormously.** A character that feels vivid on Claude may feel flat on a 7B local model. This is a model limitation, not a pack limitation.
- **No tool use or memory:** Local LLMs don't have ChatGPT's memory, web browsing, or image generation. The character is text-only.
- **Context window management:** If your model has a short context window, conversations will eventually lose the system prompt. Use Compact assembly and restart conversations periodically.

---

## Tips

- **Use the Compact assembly first.** If the character feels right, try the Full assembly. If the Full assembly overwhelms a small model, trim further.
- **Adjust temperature:** Lower temperature (0.5–0.7) for consistency; higher (0.8–1.0) for more variability.
- **Save as a character card:** Some interfaces (KoboldCPP, SillyTavern) support character card formats. You can copy the assembled prompt into a character card for easier reuse.
- **Test with example dialogue first:** After loading the character, paste a line from `09_EXAMPLE_DIALOGUE.md` as the user and check if the character's response matches the tone. If not, the model may need a larger/higher-quality model or a tighter system prompt.
