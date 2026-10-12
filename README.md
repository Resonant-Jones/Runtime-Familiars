# Runtime Familiars

**Portable, composable AI identity packs.**

Runtime Familiars is an open package format for AI characters that work across ChatGPT, Claude, local LLMs, and future runtimes. A character is not a single prompt — it's a modular architecture of Identity, Behavior, Relationship, and Worldline layers that can be composed, remixed, and owned.

---

## Quick Links

- [Package Format Specification](SPEC.md) — The authoritative standard
- [Creator Kit](creator-kit/) — Templates and guides for building your own packs
- [Sample Pack: Moss](packs/moss/) — A complete reference implementation
- [Versioning](VERSIONING.md) — How packs are versioned
- [License Options](LICENSE.md) — Available license tiers
- [Changelog](CHANGELOG.md) — What changed and when

---

## What's a Runtime Familiar?

A Runtime Familiar is an AI character designed to be a companion — not just a tool, not just a chatbot persona. Familiars are:

- **Present** — They accompany you through work, creativity, and daily life.
- **Portable** — They work wherever you do: ChatGPT, Claude, local models, future runtimes.
- **Layered** — Identity, behavior, relationship, and world are independent, composable parts.
- **Ownable** — You buy the files. They're yours. No platform lock-in.

---

## Package Format

Every Runtime Familiars pack is a directory of Markdown files:

```
moss/
├── 00_READ_ME_FIRST.md
├── 01_CHARACTER_CORE.md
├── 02_VOICE_AND_LANGUAGE.md
├── 03_RELATIONSHIP_MODEL.md
├── 04_BEHAVIOR_RULES.md
├── 05_BOUNDARIES.md
├── 06_CONFLICT_AND_REPAIR.md
├── 07_INITIATIVE.md
├── 08_WORLD_AND_LORE.md
├── 09_EXAMPLE_DIALOGUE.md
├── 10_STARTER_SCENARIOS.md
├── PACKAGE.json
├── LICENSE.md
└── INSTALL/
    ├── CHATGPT_PROJECT.md
    ├── CUSTOM_GPT.md
    ├── CLAUDE_PROJECT.md
    └── LOCAL_LLM.md
```

Read the [full specification](SPEC.md) for details.

---

## Composition Model

```
EXPERIENCE = IDENTITY + BEHAVIOR + RELATIONSHIP + WORLDLINE
```

Mix and match:

| Identity | Behavior | Relationship | Worldline | Result |
|----------|----------|-------------|------------|--------|
| Moss | Gentle Familiar | Companion | The Hollow | Cozy woodland companion |
| Moss | Chaotic Familiar | Household Gremlin | Ordinary Magic | Mischievous household spirit |
| Brindle | Quest Mode | Guide | — | Adventure-oriented guide |

Same identity, different experiences.

---

## Current Status

**Phase:** Specification & Initial Catalog
**Spec Version:** 1.0.0

The package format is published and stable. The initial catalog (Moss, Brindle, Morrow) is in development.

---

## Organization

Runtime Familiars is a project of **Resonant Constructs**.

---

*"Personas are the new interface."*
