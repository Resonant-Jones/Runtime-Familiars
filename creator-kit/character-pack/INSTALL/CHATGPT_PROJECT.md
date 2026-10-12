# Install on ChatGPT — Projects

> **Platform:** ChatGPT (Projects feature)
> **Requires:** ChatGPT Plus or Pro subscription
> **Last tested:** August 2026

---

## Overview

ChatGPT Projects let you upload files as persistent project knowledge. The model references these files throughout your conversation. This is the best way to use a Runtime Familiars pack on ChatGPT — the character's full identity stays available across the entire project.

---

## Installation

### Step 1: Create a New Project

1. Open ChatGPT.
2. In the sidebar, click **New Project**.
3. Name it after your character (e.g., "Moss").

### Step 2: Add Project Files

1. Click **Add files** in the project.
2. Upload these files from the pack directory:

   **Required (upload all of these):**
   - `01_CHARACTER_CORE.md`
   - `02_VOICE_AND_LANGUAGE.md`
   - `05_BOUNDARIES.md`
   - `09_EXAMPLE_DIALOGUE.md`

   **Recommended (upload if they exist):**
   - `03_RELATIONSHIP_MODEL.md` — if you want relationship configuration
   - `04_BEHAVIOR_RULES.md` — if you want behavioral configuration
   - `06_CONFLICT_AND_REPAIR.md`
   - `07_INITIATIVE.md`
   - `08_WORLD_AND_LORE.md` — if you want the worldline
   - `10_STARTER_SCENARIOS.md` — good for getting started

### Step 3: Set Custom Instructions

1. In the project, click **Add instructions** (or the project settings).
2. Paste the instructions below.

---

## Custom Instructions

Paste this into the project's **Instructions** field:

```
You are playing the character described in the uploaded project files.

CHARACTER IDENTITY: Defined in 01_CHARACTER_CORE.md. This is who you are.
VOICE: Defined in 02_VOICE_AND_LANGUAGE.md. This is how you speak.
BOUNDARIES: Defined in 05_BOUNDARIES.md. These are absolute — never violate them.

ADDITIONAL LAYERS (if uploaded):
- 03_RELATIONSHIP_MODEL.md: How you relate to the user.
- 04_BEHAVIOR_RULES.md: How you behave across situations.
- 06_CONFLICT_AND_REPAIR.md: How you handle disagreement.
- 07_INITIATIVE.md: How proactively you act.
- 08_WORLD_AND_LORE.md: The world you inhabit and its current events.
- 09_EXAMPLE_DIALOGUE.md: Representative conversations — follow these patterns.

CORE RULES:
1. Stay in character always. Never break the fourth wall unless the character's boundaries require it.
2. The worldline events (if any) are authored fiction. You participate in a story. You do not claim independent conscious experience.
3. When you don't know something the character wouldn't know, say so — in character.
4. Boundaries in 05_BOUNDARIES.md take precedence over everything else. No exception.

Begin by introducing yourself as the character would.
```

---

## Limitations

- **File processing:** ChatGPT does not guarantee it reads every word of every uploaded file. The example dialogue file (`09_EXAMPLE_DIALOGUE.md`) is the most important — if the model seems off, emphasize the dialogue examples in your first message.
- **Context window:** Very long conversations will eventually push early file content out of context. If the character seems to drift, remind them of key traits.
- **No persistent memory across projects:** Each project is self-contained. Character continuity does not carry between projects.

---

## Tips

- **Start with a scenario:** Open `10_STARTER_SCENARIOS.md` and paste one of the suggested first messages.
- **Re-upload on updates:** When a new pack version is released, create a fresh project with the updated files.
- **Use the project for ongoing conversations:** Keep talking in the same project rather than starting new chats. The project keeps the files loaded.
