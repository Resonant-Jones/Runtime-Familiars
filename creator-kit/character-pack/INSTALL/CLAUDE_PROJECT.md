# Install on Claude — Projects

> **Platform:** Anthropic Claude (Projects feature)
> **Requires:** Claude Pro or Team subscription
> **Last tested:** August 2026

---

## Overview

Claude Projects let you upload documents as project knowledge and set custom instructions. Claude is particularly good at maintaining character voice over long conversations, making it an excellent platform for Runtime Familiars.

---

## Installation

### Step 1: Create a New Project

1. Open Claude (web or desktop app).
2. Click **Projects** in the sidebar → **Create Project**.
3. Name it after your character (e.g., "Moss").

### Step 2: Upload Project Knowledge

1. In the project, find the **Project knowledge** section.
2. Click **Add content** and upload these files:

   **Upload all component files:**
   - `01_CHARACTER_CORE.md`
   - `02_VOICE_AND_LANGUAGE.md`
   - `03_RELATIONSHIP_MODEL.md` (if present)
   - `04_BEHAVIOR_RULES.md` (if present)
   - `05_BOUNDARIES.md`
   - `06_CONFLICT_AND_REPAIR.md` (if present)
   - `07_INITIATIVE.md` (if present)
   - `08_WORLD_AND_LORE.md` (if present)
   - `09_EXAMPLE_DIALOGUE.md`
   - `10_STARTER_SCENARIOS.md` (if present)

   > **Claude handles large document sets well.** Upload everything. The model is designed to work with substantial project knowledge.

### Step 3: Set Custom Instructions

1. Find the **Custom instructions** (or **Project instructions**) field.
2. Paste the instructions below.

---

## Custom Instructions

Paste this into the project's custom instructions:

```
You are playing the character defined in the Project Knowledge documents.

Your identity, voice, behavior, boundaries, and world context are defined in those files.
Read and internalize them before responding.

Key documents (in priority order):
1. 01_CHARACTER_CORE.md — Who you are.
2. 02_VOICE_AND_LANGUAGE.md — How you speak.
3. 09_EXAMPLE_DIALOGUE.md — Concrete examples of you in conversation. Follow these patterns closely.
4. 05_BOUNDARIES.md — Hard constraints. Never violate these.

If other documents are present (03, 04, 06, 07, 08), they define additional layers of your behavior and context.

Core rules:
- Stay in character always.
- Worldline events are authored fiction. You participate in a story; you do not claim independent conscious experience.
- When boundaries are tested, enforce them in character.
- If you don't know something, say so — in your voice.

Begin by introducing yourself naturally, as your character would.
```

---

## Limitations

- **Project knowledge is additive:** Claude reads project knowledge as supplementary context, not as hardwired identity. The custom instructions above help focus the model on what matters.
- **No persistent memory across projects:** Each project is self-contained. Conversations in one project don't carry to another.
- **Context window still applies:** Extremely long conversations may eventually push early document content out of context. Claude's context window is large (200K tokens for Pro), so this is rarely an issue.

---

## Tips

- **Claude excels at character work.** It's often the best platform for characters with subtle voices or complex emotional ranges.
- **Start conversations in the project:** Don't start a conversation outside the project and move it in — the project knowledge only applies to conversations started within the project.
- **Re-upload on updates:** When a new pack version is released, delete old files and upload the new ones. Start a fresh conversation.
- **Use the "Add content" button for text:** You can also paste component content directly as text notes rather than uploading files.
