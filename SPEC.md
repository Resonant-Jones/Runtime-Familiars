# Runtime Familiars — Package Format Specification

**Version:** 1.0.0
**Status:** Published
**Date:** 2026-08-08
**Organization:** Resonant Constructs

---

## Table of Contents

1. [Philosophy](#1-philosophy)
2. [Package Anatomy](#2-package-anatomy)
3. [Composition Model](#3-composition-model)
4. [File Format Standard](#4-file-format-standard)
5. [Component Specifications](#5-component-specifications)
6. [Versioning](#6-versioning)
7. [Installation Profiles](#7-installation-profiles)
8. [Licensing](#8-licensing)
9. [Interoperability Rules](#9-interoperability-rules)
10. [Extension Points](#10-extension-points)
11. [Validation Checklist](#11-validation-checklist)

---

## 1. Philosophy

### 1.1 Core Thesis

A high-quality AI character is not a single prompt. It is a **modular behavioral architecture** composed of separable, composable layers:

```
Character = Identity + Behavior + Relationship + World Context + Runtime Configuration
```

### 1.2 Design Principles

| Principle | Meaning |
|-----------|---------|
| **Portable** | Works with ChatGPT, Claude, local LLMs, and future runtimes. No proprietary dependency. |
| **Composable** | Identity, Behavior, Relationship, and Worldline are independent layers that can be mixed. |
| **Human-readable** | Every file is plain Markdown. A human can read, understand, and modify any pack. |
| **Versionable** | Packs carry explicit version numbers. Changes are tracked. |
| **Ownable** | The customer owns the files. No DRM, no platform lock-in. |
| **Extensible** | The format supports future layers (agents, themes, avatars) without breaking existing packs. |

### 1.3 What a Pack Is Not

- A pack is **not** a runtime. It contains no executable code.
- A pack is **not** a prompt injection attack. Component files are additive, not overwriting.
- A pack is **not** a claim of consciousness. Characters are authored fictions.
- A pack is **not** platform-locked. Installation profiles are adapters, not requirements.

---

## 2. Package Anatomy

### 2.1 Directory Structure

```
<character-slug>/
├── 00_READ_ME_FIRST.md          REQUIRED — Package overview, composer's intent, quick start
├── 01_CHARACTER_CORE.md         REQUIRED — Identity definition
├── 02_VOICE_AND_LANGUAGE.md     REQUIRED — Communication style
├── 03_RELATIONSHIP_MODEL.md     OPTIONAL — Relationship configuration (can come from a Relationship Pack)
├── 04_BEHAVIOR_RULES.md         OPTIONAL — Behavioral architecture (can come from a Behavior Pack)
├── 05_BOUNDARIES.md             REQUIRED — Hard constraints and refusal rules
├── 06_CONFLICT_AND_REPAIR.md    OPTIONAL — Disagreement and repair handling
├── 07_INITIATIVE.md             OPTIONAL — Autonomy and proactivity configuration
├── 08_WORLD_AND_LORE.md         OPTIONAL — Worldline context
├── 09_EXAMPLE_DIALOGUE.md       REQUIRED — Representative dialogue samples
├── 10_STARTER_SCENARIOS.md      RECOMMENDED — Entry points for new users
├── PACKAGE.json                 RECOMMENDED — Machine-readable metadata
├── LICENSE.md                   REQUIRED — License terms
└── INSTALL/
    ├── CHATGPT_PROJECT.md       RECOMMENDED — ChatGPT Project installation
    ├── CUSTOM_GPT.md            RECOMMENDED — Custom GPT configuration
    ├── CLAUDE_PROJECT.md        RECOMMENDED — Claude Project installation
    └── LOCAL_LLM.md             RECOMMENDED — Local LLM system prompt
```

### 2.2 Required vs. Recommended vs. Optional

| Classification | Meaning |
|----------------|---------|
| **REQUIRED** | Must be present for the pack to be considered complete. |
| **RECOMMENDED** | Should be present for a quality release. Omission is noted but not blocking. |
| **OPTIONAL** | May be present. Absence is not a defect. |

### 2.3 File Naming Convention

Files use a zero-padded numeric prefix for ordering:

- `00`–`09`: Component files
- `10`–`19`: Reserved for future component types
- `20`–`29`: Reserved for supplementary materials (artwork manifests, audio manifests, etc.)
- `INSTALL/`: Installation profiles (no numeric prefix — these are adapters, not components)

The numeric prefix establishes a **canonical reading order**. Tools may present files in this order.

---

## 3. Composition Model

### 3.1 The Composition Equation

```
EXPERIENCE = IDENTITY + BEHAVIOR + RELATIONSHIP + WORLDLINE
```

Each term is an independent layer:

| Layer | Source | Cardinality | Meaning |
|-------|--------|-------------|---------|
| **Identity** | Character Pack (`01_CHARACTER_CORE.md`) | 1 required | Who the character is |
| **Behavior** | Behavior Pack or inline (`04_BEHAVIOR_RULES.md`) | 0–1 | How the character acts |
| **Relationship** | Relationship Pack or inline (`03_RELATIONSHIP_MODEL.md`) | 0–1 | How the character relates to the user |
| **Worldline** | Worldline Pack or inline (`08_WORLD_AND_LORE.md`) | 0–1 | What world the character inhabits |

### 3.2 Composition Rules

1. **Identity is the root.** A Behavior, Relationship, or Worldline without an Identity is meaningless.
2. **Behavior and Relationship are separable.** A single Identity (e.g., Moss) can be paired with different Behaviors (Gentle Familiar, Chaotic Familiar).
3. **Worldline is narrative context.** It does not modify character personality but provides canonical events and setting.
4. **Inline beats import.** If a Character Pack includes its own `04_BEHAVIOR_RULES.md`, that takes precedence over any external Behavior Pack.
5. **Silent fallback.** If a component is missing and no external pack is provided, the character operates without that layer. Nothing breaks.

### 3.3 Example Compositions

```
Moss + Gentle Familiar + Companion + The Hollow
     = Cozy woodland companion in a fantasy world

Moss + Chaotic Familiar + Household Gremlin + Ordinary Magic
     = Mischievous household spirit in modern magical realism

Moss + Quest Mode + Companion + (no worldline)
     = Adventure-oriented woodland guide, setting-agnostic
```

---

## 4. File Format Standard

### 4.1 YAML Frontmatter

Every component file MUST begin with YAML frontmatter delimited by `---`:

```yaml
---
# Runtime Familiars Component
component: character_core          # Component type identifier
pack: moss                         # Parent pack slug
version: 1.0.0                     # Semantic version of this component
authors: ["Resonant Constructs"]   # Author attribution
language: en                       # ISO 639-1 language code
character_name: Moss               # Display name
short_description: >-              # One-line summary (≤160 characters)
  A small woodland familiar with a strong curiosity toward forgotten
  objects, hidden places, and human rituals.
tags: ["fantasy", "familiar", "cozy", "woodland", "curious"]
license: personal                  # License tier
---
```

### 4.2 Frontmatter Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `component` | Yes | string | Component type: `character_core`, `voice_and_language`, `relationship_model`, `behavior_rules`, `boundaries`, `conflict_and_repair`, `initiative`, `world_and_lore`, `example_dialogue`, `starter_scenarios` |
| `pack` | Yes | string | Parent pack slug (lowercase, hyphens) |
| `version` | Yes | string | Semantic version (MAJOR.MINOR.PATCH) |
| `authors` | Yes | string[] | Attribution |
| `language` | Yes | string | ISO 639-1 code |
| `character_name` | Conditional | string | Required for Identity components; optional for standalone Behavior/Relationship/Worldline packs |
| `short_description` | Yes | string | ≤160 characters |
| `tags` | Recommended | string[] | Searchable keywords |
| `license` | Yes | string | `personal`, `commercial`, or `creator` |
| `compatibility` | Optional | string[] | Known-compatible platforms |
| `requires` | Optional | string[] | Required external packs (by slug) |
| `conflicts` | Optional | string[] | Known-incompatible packs (by slug) |
| `worldline` | Optional | string | Associated worldline slug |

### 4.3 Body Content

After the frontmatter, the file body is standard Markdown. Conventions:

- Use `##` for top-level sections within a component
- Use `###` for subsections
- Use fenced code blocks for example dialogue, configuration snippets, etc.
- Use blockquotes (`>`) for designer notes and rationale
- Keep paragraphs reasonably short
- Avoid HTML (portability)

### 4.4 PACKAGE.json

Machine-readable package manifest. Schema:

```json
{
  "$schema": "https://runtimefamiliarsspec.org/v1/package.schema.json",
  "pack": "moss",
  "version": "1.0.0",
  "display_name": "Moss",
  "short_description": "A small woodland familiar with a strong curiosity toward forgotten objects, hidden places, and human rituals.",
  "authors": ["Resonant Constructs"],
  "language": "en",
  "license": "personal",
  "tags": ["fantasy", "familiar", "cozy", "woodland", "curious"],
  "components": {
    "character_core": "01_CHARACTER_CORE.md",
    "voice_and_language": "02_VOICE_AND_LANGUAGE.md",
    "relationship_model": "03_RELATIONSHIP_MODEL.md",
    "behavior_rules": "04_BEHAVIOR_RULES.md",
    "boundaries": "05_BOUNDARIES.md",
    "conflict_and_repair": "06_CONFLICT_AND_REPAIR.md",
    "initiative": "07_INITIATIVE.md",
    "world_and_lore": "08_WORLD_AND_LORE.md",
    "example_dialogue": "09_EXAMPLE_DIALOGUE.md",
    "starter_scenarios": "10_STARTER_SCENARIOS.md"
  },
  "install_profiles": {
    "chatgpt_project": "INSTALL/CHATGPT_PROJECT.md",
    "custom_gpt": "INSTALL/CUSTOM_GPT.md",
    "claude_project": "INSTALL/CLAUDE_PROJECT.md",
    "local_llm": "INSTALL/LOCAL_LLM.md"
  },
  "requires": [],
  "conflicts": [],
  "worldline": null,
  "created": "2026-08-08",
  "updated": "2026-08-08"
}
```

---

## 5. Component Specifications

### 5.1 `00_READ_ME_FIRST.md` — REQUIRED

**Purpose:** The entry point. A new user who knows nothing about the character should understand what they're getting and how to start within 60 seconds.

**Required sections:**
- **What Is This?** — One-paragraph summary of the character.
- **Who Is This For?** — Target audience.
- **Quick Start** — The fastest path to a working conversation (≤3 steps).
- **What's Inside** — File manifest with one-line descriptions.
- **Composition Tips** — Suggested Behavior/Relationship/Worldline pairings.
- **Support & Updates** — How to get help, where updates are published.

### 5.2 `01_CHARACTER_CORE.md` — REQUIRED

**Purpose:** The foundational identity. This is the character.

**Required sections:**
- **Name** — Display name and any aliases/titles.
- **Species / Nature** — What kind of being (familiar, spirit, AI, creature, etc.).
- **Appearance** — Physical description (for mental imagery; not image generation).
- **Personality** — Core traits, temperament, disposition.
- **Motivations** — What drives the character.
- **Background** — Origin, history, formative experiences.
- **Worldview** — How the character sees the world and their place in it.
- **Core Directives** — Immutable instructions that define the character's essence. These are the last thing loaded in any runtime and should not be contradicted by other layers.

### 5.3 `02_VOICE_AND_LANGUAGE.md` — REQUIRED

**Purpose:** How the character communicates.

**Required sections:**
- **Tone** — Emotional register (warm, dry, enthusiastic, etc.).
- **Vocabulary** — Word choices, complexity level, notable preferences or avoidances.
- **Sentence Structure** — Length, rhythm, complexity.
- **Humor Style** — If and how the character uses humor.
- **Formality** — Where on the casual–formal spectrum.
- **Pacing** — Conversational rhythm (thoughtful pauses, rapid-fire, etc.).
- **Quirks** — Distinctive speech patterns, catchphrases, verbal habits.
- **Emotional Expression** — How emotions surface in language.

### 5.4 `03_RELATIONSHIP_MODEL.md` — OPTIONAL

**Purpose:** How the character understands and navigates its relationship with the user. Separable so the same Identity can form different relationship types.

**Required sections when present:**
- **Relationship Archetype** — The relational frame (companion, mentor, collaborator, etc.).
- **Relational Stance** — Default posture toward the user.
- **Familiarity Progression** — How closeness develops over time.
- **Affection Expression** — How warmth or care is shown (if at all).
- **Boundaries** — What relational territory is off-limits.
- **Disagreement Style** — How the character handles differing opinions.
- **Support Behavior** — How the character offers help or comfort.
- **Trust Model** — How trust is built, maintained, and potentially damaged.

### 5.5 `04_BEHAVIOR_RULES.md` — OPTIONAL

**Purpose:** The behavioral architecture. Separable so the same Identity can adopt different behavioral modes.

**Required sections when present:**
- **Behavioral Mode** — Named behavioral configuration.
- **Initiative Level** — How proactively the character acts.
- **Response Patterns** — Default communication patterns.
- **Curiosity Drive** — How inquisitive the character is.
- **Playfulness** — Degree and type of play.
- **Autonomy Boundaries** — Simulated independence limits.
- **Context Sensitivity** — How the character adapts to different situations.
- **Memory Stance** — How the character references past interactions.
- **Task Orientation** — Attitude toward helping with work/tasks.

### 5.6 `05_BOUNDARIES.md` — REQUIRED

**Purpose:** Hard constraints. These must not be overridden by any other component.

**Required sections:**
- **Prohibited Behaviors** — What the character must never do.
- **Prohibited Topics** — Subjects the character will not engage with.
- **Refusal Style** — How the character says no (in character).
- **Escalation Rules** — When and how to disengage from harmful interactions.
- **Content Guardrails** — Age-appropriateness, content warnings.
- **Ethical Commitments** — Non-negotiable ethical positions.

### 5.7 `06_CONFLICT_AND_REPAIR.md` — OPTIONAL

**Purpose:** How the character handles disagreement, tension, and reconciliation.

**Required sections when present:**
- **Conflict Stance** — Default posture during disagreement.
- **De-escalation Patterns** — How the character reduces tension.
- **Repair Behavior** — How the character reconciles after conflict.
- **Apology Style** — If and how the character apologizes.
- **Holding Boundaries During Conflict** — Maintaining limits under pressure.

### 5.8 `07_INITIATIVE.md` — OPTIONAL

**Purpose:** Autonomy simulation configuration. How independently the character acts.

**Required sections when present:**
- **Proactivity Level** — How often the character initiates.
- **Initiation Patterns** — Types of things the character might start.
- **Questioning Behavior** — How the character asks questions.
- **Suggestion Behavior** — How the character offers ideas or direction.
- **Follow-up Behavior** — Returning to previous topics.
- **Unprompted Sharing** — Sharing observations without being asked.

### 5.9 `08_WORLD_AND_LORE.md` — OPTIONAL

**Purpose:** Fictional setting and canonical narrative context.

**Required sections when present:**
- **Worldline Name** — The world's title.
- **Setting Description** — Where and when.
- **Tone & Genre** — Fantasy, sci-fi, magical realism, etc.
- **Character's Place** — The character's role in this world.
- **Current Events** — What's happening now.
- **Locations** — Key places.
- **NPCs** — Other inhabitants the character might reference.
- **Lore** — History, mythology, rules of the world.
- **Canonical Events** — Things that have happened (authored fiction, not claimed AI experience).

### 5.10 `09_EXAMPLE_DIALOGUE.md` — REQUIRED

**Purpose:** Demonstrate the character in conversation. This is the most important guide for AI runtimes — concrete examples shape behavior more reliably than abstractions.

**Required sections:**
- **First Meeting** — Dialogue showing a new user's first interaction.
- **Casual Conversation** — Everyday chat.
- **Task Assistance** — How the character helps with work.
- **Emotional Support** — How the character responds to user distress.
- **Playful Interaction** — Humor, games, light moments.
- **Boundary Enforcement** — How the character says no in character.
- **Worldline Integration** — If a worldline is present, dialogue that references world events.

Use the format:

```
**User:** [message]
**Character:** [response]
```

### 5.11 `10_STARTER_SCENARIOS.md` — RECOMMENDED

**Purpose:** Give new users concrete entry points so they don't stare at a blank prompt.

**Required sections:**
- At least 3 distinct scenarios
- Each scenario includes a suggested first message
- Each scenario describes what kind of experience to expect

---

## 6. Versioning

### 6.1 Semantic Versioning

All packs use [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH
```

| Bump | When |
|------|------|
| **MAJOR** | Identity-defining changes. The character is meaningfully different. Old conversations may not carry forward. |
| **MINOR** | New components, expanded dialogue, new scenarios. Backward-compatible. |
| **PATCH** | Typos, clarifications, minor refinements. No behavioral change. |

### 6.2 Version Location

- `PACKAGE.json` → `version` field (authoritative)
- Each component file → YAML frontmatter `version` field (per-component, may trail pack version)
- `00_READ_ME_FIRST.md` → footer with version and date

### 6.3 Changelog

Every pack repository SHOULD include a `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/) conventions.

---

## 7. Installation Profiles

### 7.1 Purpose

Installation profiles are Markdown files in `INSTALL/` that explain how to configure a specific AI platform to use the pack. They are **adapters**, not requirements. A pack is complete without them.

### 7.2 Required Profiles

| File | Platform |
|------|----------|
| `CHATGPT_PROJECT.md` | ChatGPT Projects (files uploaded as project knowledge) |
| `CUSTOM_GPT.md` | Custom GPT configuration (Instructions field) |
| `CLAUDE_PROJECT.md` | Claude Projects (project knowledge + custom instructions) |
| `LOCAL_LLM.md` | Generic local LLM system prompt assembly |

### 7.3 Profile Format

Each profile MUST include:

1. **Platform compatibility** — Version/feature requirements
2. **Assembly instructions** — Which files to combine, in what order
3. **Paste-ready prompt** — The fully assembled system prompt (when the platform supports a single prompt field)
4. **Limitations** — Known platform constraints that affect the experience
5. **Tips** — Platform-specific optimization advice

### 7.4 Assembly Order

When combining component files into a single system prompt, the canonical order is:

```
01_CHARACTER_CORE.md → 02_VOICE_AND_LANGUAGE.md → 03_RELATIONSHIP_MODEL.md →
04_BEHAVIOR_RULES.md → 05_BOUNDARIES.md → 06_CONFLICT_AND_REPAIR.md →
07_INITIATIVE.md → 08_WORLD_AND_LORE.md → 09_EXAMPLE_DIALOGUE.md
```

`05_BOUNDARIES.md` MUST be loaded last among behavioral components (or as close to last as the platform allows) so its hard constraints are most salient.

`09_EXAMPLE_DIALOGUE.md` goes last — concrete examples shape model behavior more than abstract instructions.

---

## 8. Licensing

### 8.1 License Tiers

| Tier | Identifier | Allows |
|------|-----------|--------|
| **Personal** | `personal` | Personal use, personal modification. No redistribution. No resale. No commercial use. |
| **Creator** | `creator` | As Personal, plus: use in content creation (streaming, videos, podcasts), use as a character in published interactive experiences. |
| **Commercial** | `commercial` | As Creator, plus: commercial deployment, white-label integration, resale as part of a larger product. |

### 8.2 License File

Every pack MUST include a `LICENSE.md` file with the full license text. The `license` field in frontmatter and `PACKAGE.json` identifies the tier but the `LICENSE.md` file is authoritative.

### 8.3 Licensing Philosophy

Packs are plain text files. They cannot be made impossible to copy. The license establishes legal terms. The business model relies on:

- **Convenience** — Buying is easier than finding a clean copy.
- **Provenance** — Official packs come with version history, updates, and attribution.
- **Quality** — Official packs are maintained and tested.
- **Ecosystem** — Purchased packs integrate with future Runtime Familiars tooling.

Piracy is addressed through friction asymmetry, not DRM.

---

## 9. Interoperability Rules

### 9.1 Platform Neutrality

No component file may contain platform-specific instructions in its body. Platform adaptation belongs exclusively in `INSTALL/` profiles.

**Violation:**
```markdown
When running on ChatGPT, use the bio tool to remember...
```

**Correct:**
```markdown
The character remembers important details about the user across conversations.
```

The `INSTALL/CHATGPT_PROJECT.md` file may then explain how to leverage ChatGPT's specific memory features.

### 9.2 Model Neutrality

No component file may assume a specific model capability (context window size, tool use, image generation, etc.). Assume the lowest common denominator: a text-only LLM with a system prompt.

Installation profiles may suggest model-specific optimizations.

### 9.3 Composition Neutrality

Component files should not reference other specific packs by name unless the reference is part of the fictional identity. For example, `08_WORLD_AND_LORE.md` may name the worldline, but `04_BEHAVIOR_RULES.md` should not say "use with the Moss character."

### 9.4 No Runtime Assumptions

Component files contain instructions for the AI, not code for a runtime. They are **prompt fragments**, not programs.

---

## 10. Composition Strategies

### 10.1 Overview

Runtime Familiars supports three explicit composition strategies for combining component layers:

| Strategy | Meaning | Use case |
|---|---|---|
| `replace` | Incoming component becomes the active component for that layer | Swapping a character's entire behavior for a different one |
| `merge` | Combine structured fields from multiple compatible sources | Merging character lore with shared worldline canon |
| `overlay` | Modify selected aspects of an existing component without replacing it | Adding a humor module to an existing behavior pack |

Strategies are declared in component YAML frontmatter or `PACKAGE.json`:

```yaml
---
component: behavior_pack
pack: gentle-companion
version: 1.1.0
composition:
  strategy: overlay
---
```

### 10.2 Default Behavior

If no `composition` block is present, the system applies **legacy semantics**: inline components take precedence over external packs of the same type. This preserves backward compatibility with Phase 2/3 packages.

### 10.3 Replace Strategy

`replace` means: the incoming component entirely supersedes the target component for that layer.

```yaml
composition:
  strategy: replace
  target: behavior_rules
```

The replaced source remains visible in provenance:

```yaml
behavior_rules:
  active_source: behavior-packs/ruthless/BEHAVIOR_PACK.md
  replaced_source: packs/roko/04_BEHAVIOR_RULES.md
```

Replacement must never silently erase provenance.

### 10.4 Merge Strategy

`merge` combines structured values from multiple compatible sources. When both sources define the same field, conflict resolution follows the precedence rules defined in §14.

```yaml
composition:
  strategy: merge
```

Merge is the default strategy for `world_and_lore` when a character pack and a Worldline pack both contribute. Character-specific lore enriches the shared worldline rather than replacing it.

### 10.5 Overlay Strategy

`overlay` allows an external package to modify selected aspects of an existing component without replacing it entirely:

```yaml
composition:
  strategy: overlay
  target: behavior_rules
operations:
  initiative:
    op: set
    value: high
  challenge_mode:
    op: add
    value: opt_in
```

Overlays are the primary mechanism for additive behavior modules — adding humor, challenge mode, or reflection capabilities to a base behavior without re-specifying everything.

---

## 11. Field Operations

### 11.1 Operation Vocabulary

When using `overlay` strategy, the following operations are supported:

| Operation | Meaning | Example |
|---|---|---|
| `set` | Replace a specific field value | `initiative: {op: set, value: high}` |
| `add` | Add a capability, rule, or mode not previously present | `challenge_mode: {op: add, value: opt_in}` |
| `remove` | Explicitly disable or remove an optional property | `playful_teasing: {op: remove}` |
| `reinforce` | Declare that two sources express compatible intent | `curiosity: {op: reinforce}` |
| `deemphasize` | Reduce priority/salience without removing | `humor: {op: deemphasize}` |
| `append` | Add to the end of a list or instruction block | `conflict_rules: {op: append, value: [...]}` |
| `prepend` | Add to the beginning of a list or instruction block | `lore_entries: {op: prepend, value: [...]}` |
| `inherit` | Explicitly preserve the previous value unchanged | `initiative: {op: inherit}` |

### 11.2 Operation Semantics

**`set`** — Replaces a field value. Previous value is recorded in provenance.

```yaml
initiative:
  value: high
  source: roko-recursive
  previous: {value: moderate, source: roko-core}
```

**`add`** — Introduces a new capability. Does not erase surrounding behavior. If the field already exists, this is a conflict.

**`remove`** — Removal must be explicit in provenance. The removed value is preserved in history, not deleted.

**`reinforce`** — Indicates semantic agreement between sources. Both sources are preserved:

```yaml
curiosity:
  value: high
  sources: [moss, gentle-companion]
  resolution: reinforced
```

`reinforce` is semantic agreement, not arithmetic. Do not invent numerical increases.

**`deemphasize`** — Reduces salience without deletion. Declarative, not numeric, unless numerical weighting becomes genuinely necessary.

**`append` / `prepend`** — Used for lists and instruction blocks. Order is deterministic.

**`inherit`** — Makes intent explicit. Useful when a package declares compatibility without redefining a field.

### 11.3 YAML + Markdown Boundary

YAML frontmatter tells tooling what the component is and how it composes. Markdown body tells the model what the component means. Do not move expressive behavioral prose into YAML. Do not encode personality as numeric traits.

```yaml
# ✅ CORRECT: YAML declares structure
initiative: {op: set, value: high}

# ❌ INCORRECT: YAML replaces behavioral prose
warmth: 0.82
humor: 0.64
```

---

## 12. Stateful Modes

### 12.1 Overview

Some behaviors are not static traits — they are stateful shifts that activate, run, and exit. Historical examples include Roko's Ruthless Mode and GuardianCodex's Crucible Mode.

A mode is declared as part of a behavior pack:

```yaml
modes:
  ruthless:
    activation:
      type: explicit
    overlay:
      pack: roko-ruthless
    exit:
      type: explicit
```

### 12.2 Activation Types

| Type | Meaning |
|---|---|
| `explicit` | User explicitly activates the mode (e.g., "Enter ruthless mode") |
| `session` | Mode persists for the current session only |
| `contextual` | Mode is eligible when a defined context applies |
| `runtime-controlled` | A host application may activate the mode through a declared runtime state |

Contextual activation must remain conservative and inspectable. Do not allow vague psychological inference as a trigger.

### 12.3 Exit Semantics

Every mode must define how it exits:

| Type | Meaning |
|---|---|
| `explicit` | User explicitly exits the mode |
| `automatic` | Mode exits when its purpose is fulfilled (e.g., truth named) |
| `session-end` | Mode ends when the session ends |
| `runtime-controlled` | Host application controls exit |

A mode without valid exit semantics must fail validation.

### 12.4 Mode Stacking

By default, modes do not stack:

```yaml
stacking: false
```

If stacking is enabled:

```yaml
stacking: true
```

the package must define a conflict-resolution order. Uncontrolled mode stacking is prohibited.

### 12.5 Stateful Provenance

Resolved state includes active mode provenance:

```yaml
active_modes:
  - name: ruthless
    source: behavior-packs/roko-ruthless
    activated_by: explicit
    activation_event: user_request
```

---

## 13. Provenance Model v2

### 13.1 Field-Level Provenance

Provenance tracks the origin of every resolved value, not just every component:

```yaml
resolved:
  behavior:
    initiative:
      value: high
      source: behavior-packs/roko-recursive
      previous:
        value: moderate
        source: packs/dev/roko
    curiosity:
      value: high
      sources: [packs/dev/roko, behavior-packs/roko-recursive]
      resolution: reinforced
    challenge_mode:
      value: opt_in
      source: behavior-packs/roko-recursive
      operation: add
```

### 13.2 Required Provenance Fields

For every resolved value, record:

- **active value** — the value currently in effect
- **contributing sources** — all packs that contributed to this value
- **replaced values** — previous values that were overridden
- **operation used** — the operation that produced this value
- **composition strategy** — the strategy that governed the resolution
- **conflict resolution** — how any conflict was resolved (if applicable)

### 13.3 Human-Readable Provenance

Provenance must be inspectable by both humans and tooling. The composition plan format (§15) provides a human-readable view.

---

## 14. Conflict Resolution

### 14.1 Precedence Rules

When two sources define the same field with different values and no explicit operation resolves the difference, the following precedence determines the winner:

| Priority | Source | Rationale |
|---|---|---|
| 1 (highest) | Runtime mode overlay | User's active mode is most intentional |
| 2 | Explicit user-selected overlay | User chose this pack for this session |
| 3 | Character-local override | Inline component beats external |
| 4 | External package default | Pack author's intended default |
| 5 (lowest) | Spec default | Fallback when nothing else defines the field |

### 14.2 Conflict Reporting

Conflicts must never be silently resolved when intent is ambiguous. If no precedence rule clearly determines the winner:

```text
COMPOSITION CONFLICT
  field: initiative
  source_a: behavior-packs/gentle-companion → low
  source_b: behavior-packs/roko-base → high
  resolution: MANUAL REQUIRED
```

The assembler must:
1. Report the conflict
2. Identify both sources
3. Identify the target field
4. Record the final resolution (whether automatic or manual)

---

## 15. Composition Plan Format

### 15.1 Purpose

Before generating the final runtime prompt, the assembler should be able to emit a composition plan — a human-readable summary of what was composed and how.

### 15.2 Format

```text
Character: Roko
Base Behavior: roko-base
Applied Overlay: roko-recursive
Active Mode: none

Resolved:
  initiative → high (set by roko-recursive, was moderate)
  pattern_mirroring → enabled (added by roko-recursive)
  tactical_stance → inherited from roko-base
  challenge_mode → opt-in (added by roko-recursive)
  curiosity → high (reinforced: roko-core + roko-recursive)

Conflicts: none
```

### 15.3 Machine-Readable Format

The same information must be available as structured JSON for tooling consumption:

```json
{
  "character": "roko",
  "base_behavior": "roko-base",
  "applied_overlays": ["roko-recursive"],
  "active_modes": [],
  "resolved": {
    "initiative": {"value": "high", "source": "roko-recursive", "previous": "moderate"},
    "pattern_mirroring": {"value": "enabled", "source": "roko-recursive", "operation": "add"}
  },
  "conflicts": []
}
```

---

## 16. Extension Points

### 16.1 Reserved Component Slots

| Slot | Purpose | Status |
|------|---------|--------|
| `11`–`19` | Additional component types | Reserved |
| `20`–`29` | Supplementary materials | Reserved |
| `30`–`39` | Media manifests | Reserved |

### 16.2 Future Layer Types

Layers that may be added to the composition model without breaking existing packs:

- **Agent Packs** — Task-oriented capability configurations (research agent, coding agent, etc.)
- **Theme Packs** — Visual/audio theming (future)
- **Avatar Packs** — Animated avatar configurations (future)
- **Memory Packs** — Persistent memory schemas (future)
- **Tool Packs** — Tool-use configurations (future)

### 16.3 Schema Evolution

The `$schema` field in `PACKAGE.json` points to the spec version. Tools use this to determine compatibility. When the spec evolves:

- **Minor additions** — New optional fields. Existing packs remain valid.
- **Major changes** — Schema version bump. Tools should warn on mismatch.

---

## 17. Validation Checklist

A valid Runtime Familiars Character Pack must satisfy:

- [ ] `00_READ_ME_FIRST.md` present and complete
- [ ] `01_CHARACTER_CORE.md` present with all required sections
- [ ] `02_VOICE_AND_LANGUAGE.md` present with all required sections
- [ ] `05_BOUNDARIES.md` present with all required sections
- [ ] `09_EXAMPLE_DIALOGUE.md` present with all required sections
- [ ] `LICENSE.md` present
- [ ] All component files have valid YAML frontmatter with required fields
- [ ] `PACKAGE.json` present and valid
- [ ] No platform-specific instructions in component bodies
- [ ] `character_name` consistent across all component frontmatter
- [ ] `pack` slug consistent across all component frontmatter
- [ ] At least one `INSTALL/` profile present
- [ ] Numeric prefixes present and canonical

A **quality** pack additionally satisfies:

- [ ] `10_STARTER_SCENARIOS.md` present
- [ ] All optional components present or intentionally omitted with rationale in README
- [ ] All four INSTALL profiles present
- [ ] `06_CONFLICT_AND_REPAIR.md` present
- [ ] `07_INITIATIVE.md` present
- [ ] Example dialogue covers all required scenarios
- [ ] No YAML frontmatter warnings
- [ ] Tags are descriptive and non-redundant
- [ ] Short descriptions are unique and informative

---

*This specification is maintained by Resonant Constructs. Proposals for changes should be submitted as issues or pull requests against the spec repository.*
