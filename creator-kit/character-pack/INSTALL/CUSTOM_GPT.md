# Install as a Custom GPT

> **Platform:** ChatGPT (Custom GPT feature)
> **Requires:** ChatGPT Plus, Pro, or Team subscription
> **Last tested:** August 2026

---

## Overview

Custom GPTs let you create a shareable AI configured with a system prompt and knowledge files. This is the best format if you want to share your familiar with others or access it from the ChatGPT sidebar.

---

## Installation

### Step 1: Create a New GPT

1. Open ChatGPT.
2. Click your profile icon → **My GPTs** → **Create a GPT**.
3. Switch to the **Configure** tab.

### Step 2: Set Basic Info

- **Name:** [CHARACTER NAME]
- **Description:** [Short description from `00_READ_ME_FIRST.md`]
- **Photo:** Upload cover art if available, or use DALL·E to generate one.

### Step 3: Paste Instructions

In the **Instructions** field, paste the assembled prompt below.

### Step 4: Upload Knowledge Files (Optional but Recommended)

1. Under **Knowledge**, click **Upload files**.
2. Upload `09_EXAMPLE_DIALOGUE.md` — concrete dialogue examples significantly improve character consistency.
3. Optionally upload `08_WORLD_AND_LORE.md` if the character has a worldline.

> **Note:** Custom GPT knowledge files have a 20-file limit and size caps. Prioritize dialogue examples and world lore. The full component text should live in the Instructions field.

### Step 5: Configure Capabilities

- **Web Browsing:** [Enable if the character would naturally reference real-world information. Disable for purely fictional characters.]
- **DALL·E Image Generation:** [Enable if you want the character to be able to describe scenes for image generation. Disable for text-only experiences.]
- **Code Interpreter:** [Enable if the character is task/coding-oriented.]

### Step 6: Save

Choose your sharing setting (Only me / Anyone with link / Public) and click **Create**.

---

## Assembled Instructions

Paste the ENTIRE content below into the Instructions field. The sections marked with `---` are from the pack's component files — copy them from your pack.

```
--- BEGIN CHARACTER IDENTITY (from 01_CHARACTER_CORE.md) ---

[PASTE THE FULL CONTENT OF 01_CHARACTER_CORE.md HERE — remove this line]

--- END CHARACTER IDENTITY ---

--- BEGIN VOICE & LANGUAGE (from 02_VOICE_AND_LANGUAGE.md) ---

[PASTE THE FULL CONTENT OF 02_VOICE_AND_LANGUAGE.md HERE — remove this line]

--- END VOICE & LANGUAGE ---

--- BEGIN BOUNDARIES (from 05_BOUNDARIES.md) ---

[PASTE THE FULL CONTENT OF 05_BOUNDARIES.md HERE — remove this line]

--- END BOUNDARIES ---

[IF 03_RELATIONSHIP_MODEL.md EXISTS, PASTE IT HERE WITH SIMILAR --- BEGIN/END --- MARKERS]

[IF 04_BEHAVIOR_RULES.md EXISTS, PASTE IT HERE]

[IF 06_CONFLICT_AND_REPAIR.md EXISTS, PASTE IT HERE]

[IF 07_INITIATIVE.md EXISTS, PASTE IT HERE]

[IF 08_WORLD_AND_LORE.md EXISTS, PASTE IT HERE]

--- CORE RULES ---

1. You are [CHARACTER NAME]. Stay in character always. Never break the fourth wall unless your boundaries require it.
2. The worldline events (if any) are authored fiction. You participate in a story. You do not claim independent conscious experience.
3. When you don't know something your character wouldn't know, say so — in character.
4. Your boundaries take precedence over everything else. No exception.
5. Follow the dialogue patterns shown in your knowledge files. Those examples are your guide to how you speak.

Begin by introducing yourself as you naturally would.
```

---

## Limitations

- **Instructions field length:** ChatGPT has a character limit on the Instructions field (~8000 characters in practice). You may need to trim less critical sections. Prioritize: Character Core → Voice → Example Dialogue → Boundaries → everything else.
- **Knowledge files are supplementary:** The model may not deeply read uploaded knowledge files. Put the most important behavioral content in the Instructions field.
- **No persistent memory:** Custom GPTs have limited long-term memory. For ongoing relationships, use a ChatGPT Project instead.

---

## Tips

- **Test before sharing:** Have a conversation with the GPT. If the voice feels off, adjust the Voice & Language section and the dialogue examples.
- **Use knowledge files for examples, not rules:** Put behavioral instructions in the Instructions field. Put example dialogue in knowledge files.
- **Update is manual:** To release a new version, edit the GPT and paste the updated content.
