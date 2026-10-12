# Versioning

Runtime Familiars packs follow [Semantic Versioning 2.0.0](https://semver.org/).

## Pack Version

```
MAJOR.MINOR.PATCH
```

| Bump | Trigger | User Impact |
|------|---------|-------------|
| **MAJOR** (`2.0.0`) | Identity-defining rewrite. Core personality, voice, or boundaries substantially changed. | Old conversations may not carry forward. Re-install recommended. |
| **MINOR** (`1.1.0`) | New components, expanded dialogue, new scenarios, new installation profiles. | Backward-compatible. Existing installations continue to work. New content is additive. |
| **PATCH** (`1.0.1`) | Typo fixes, clarifications, minor refinements. No behavioral change. | Invisible to users. Safe to update or skip. |

## Component Version

Each component file carries its own version in YAML frontmatter. Component versions may trail the pack version when a component was not modified in a given release:

```
Pack v1.1.0 ships:
  01_CHARACTER_CORE.md    v1.0.0  (unchanged since v1.0.0)
  04_BEHAVIOR_RULES.md    v1.1.0  (updated in this release)
  09_EXAMPLE_DIALOGUE.md  v1.1.0  (updated in this release)
```

The pack version in `PACKAGE.json` is authoritative. Component-level versions are informational.

## Spec Version

The specification itself (`SPEC.md`) is versioned independently. The `$schema` field in `PACKAGE.json` encodes the spec version the pack was authored against.

## Changelog Convention

All changes are documented in `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/) with sections:

- **Added** — New components, scenarios, profiles
- **Changed** — Modified behavior, voice, or boundaries
- **Deprecated** — Components scheduled for removal
- **Removed** — Deleted components
- **Fixed** — Corrections and clarifications

## Backward Compatibility Promise

- **PATCH and MINOR** releases are always backward-compatible. A user running v1.0.0 can update to v1.2.3 without breaking their experience.
- **MAJOR** releases may change the character enough that previous conversation context feels misaligned. This will be clearly communicated.
- **The spec** (`SPEC.md`) follows the same promise. MINOR spec additions (new optional fields, new component slots) do not invalidate existing packs.
