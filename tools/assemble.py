"""
Runtime Familiars — Package Assembler

Compiles a character pack (plus optional external Behavior, Relationship, and
Worldline packs) into a single runtime-ready prompt with full source provenance.

Usage:
    python3 tools/assemble.py packs/moss
    python3 tools/assemble.py packs/moss --behavior behavior-packs/gentle-companion
    python3 tools/assemble.py packs/moss --worldline worldline-packs/the-hollow
    python3 tools/assemble.py packs/moss -b behavior-packs/gentle-companion -w worldline-packs/the-hollow
    python3 tools/assemble.py packs/moss --report    # Composition report only
    python3 tools/assemble.py packs/moss --output assembled/moss-prompt.md
"""

import yaml
import json
import sys
import os
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set, Tuple


# ─── Constants ───────────────────────────────────────────────────────────────

class ComponentType(Enum):
    READ_ME_FIRST = "read_me_first"
    CHARACTER_CORE = "character_core"
    VOICE_AND_LANGUAGE = "voice_and_language"
    RELATIONSHIP_MODEL = "relationship_model"
    BEHAVIOR_RULES = "behavior_rules"
    BOUNDARIES = "boundaries"
    CONFLICT_AND_REPAIR = "conflict_and_repair"
    INITIATIVE = "initiative"
    WORLD_AND_LORE = "world_and_lore"
    EXAMPLE_DIALOGUE = "example_dialogue"
    STARTER_SCENARIOS = "starter_scenarios"

# Canonical assembly order
CANONICAL_ORDER: List[ComponentType] = [
    ComponentType.CHARACTER_CORE,
    ComponentType.VOICE_AND_LANGUAGE,
    ComponentType.RELATIONSHIP_MODEL,
    ComponentType.BEHAVIOR_RULES,
    ComponentType.CONFLICT_AND_REPAIR,
    ComponentType.INITIATIVE,
    ComponentType.WORLD_AND_LORE,
    ComponentType.BOUNDARIES,
    ComponentType.EXAMPLE_DIALOGUE,
]

COMPONENT_FILES: Dict[ComponentType, str] = {
    ComponentType.READ_ME_FIRST: "00_READ_ME_FIRST.md",
    ComponentType.CHARACTER_CORE: "01_CHARACTER_CORE.md",
    ComponentType.VOICE_AND_LANGUAGE: "02_VOICE_AND_LANGUAGE.md",
    ComponentType.RELATIONSHIP_MODEL: "03_RELATIONSHIP_MODEL.md",
    ComponentType.BEHAVIOR_RULES: "04_BEHAVIOR_RULES.md",
    ComponentType.BOUNDARIES: "05_BOUNDARIES.md",
    ComponentType.CONFLICT_AND_REPAIR: "06_CONFLICT_AND_REPAIR.md",
    ComponentType.INITIATIVE: "07_INITIATIVE.md",
    ComponentType.WORLD_AND_LORE: "08_WORLD_AND_LORE.md",
    ComponentType.EXAMPLE_DIALOGUE: "09_EXAMPLE_DIALOGUE.md",
    ComponentType.STARTER_SCENARIOS: "10_STARTER_SCENARIOS.md",
}

# External pack types
PACK_TYPE_MAP = {
    "behavior": ComponentType.BEHAVIOR_RULES,
    "relationship": ComponentType.RELATIONSHIP_MODEL,
    "worldline": ComponentType.WORLD_AND_LORE,
}


# ─── Data Classes ────────────────────────────────────────────────────────────

@dataclass
class ProvenanceEntry:
    """Tracks where a value or section originated."""
    value: str
    source_file: str
    source_type: str  # "inline" or "external"
    overrides: Optional[str] = None  # Path that was overridden
    component_type: Optional[str] = None
    section: Optional[str] = None  # Section header if applicable


@dataclass
class ComponentChunk:
    """A resolved component chunk ready for assembly."""
    component_type: ComponentType
    content: str  # Raw markdown body (no frontmatter)
    provenance: ProvenanceEntry
    frontmatter: Dict


@dataclass
class AssemblyResult:
    """Complete assembly output."""
    character_pack: str
    behavior_pack: Optional[str]
    relationship_pack: Optional[str]
    worldline_pack: Optional[str]
    assembled_prompt: str
    chunks: List[ComponentChunk]
    overrides: List[ProvenanceEntry]
    warnings: List[str]


# ─── File Parsing ────────────────────────────────────────────────────────────

def parse_frontmatter(filepath: str) -> Tuple[Optional[Dict], str]:
    """Parse YAML frontmatter from a file. Returns (fm_dict, body)."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        return {}, content

    end_idx = content.find("---", 3)
    if end_idx == -1:
        return {}, content

    yaml_str = content[3:end_idx].strip()
    body = content[end_idx + 3:].strip()

    if not yaml_str:
        return {}, body

    try:
        parsed = yaml.safe_load(yaml_str)
        return (parsed if isinstance(parsed, dict) else {}), body
    except yaml.YAMLError:
        return {}, body


def read_body(filepath: str) -> str:
    """Read the body of a markdown file, stripping frontmatter."""
    fm, body = parse_frontmatter(filepath)
    return body


# ─── Package Discovery ──────────────────────────────────────────────────────

def discover_components(pack_path: str) -> Dict[ComponentType, str]:
    """Discover which component files exist in a package directory."""
    components = {}
    pack_dir = Path(pack_path)
    for ct in ComponentType:
        filename = COMPONENT_FILES[ct]
        filepath = pack_dir / filename
        if filepath.exists():
            components[ct] = str(filepath)
    return components


def discover_external_pack(pack_path: str, pack_type: str) -> Optional[str]:
    """Find the component file in an external pack directory."""
    component_type = PACK_TYPE_MAP.get(pack_type)
    if not component_type:
        return None

    pack_dir = Path(pack_path)
    # For behavior packs, look for BEHAVIOR_PACK.md
    # For relationship packs, look for RELATIONSHIP_PACK.md
    # For worldline packs, look for WORLDLINE.md
    filename_map = {
        "behavior": "BEHAVIOR_PACK.md",
        "relationship": "RELATIONSHIP_PACK.md",
        "worldline": "WORLDLINE.md",
    }
    filename = filename_map.get(pack_type)
    if filename:
        filepath = pack_dir / filename
        if filepath.exists():
            return str(filepath)

    # Fallback: look for the standard numbered file
    std_filename = COMPONENT_FILES.get(component_type)
    if std_filename:
        filepath = pack_dir / std_filename
        if filepath.exists():
            return str(filepath)

    return None


# ─── Override Resolution ────────────────────────────────────────────────────

def resolve_component(
    character_components: Dict[ComponentType, str],
    external_packs: Dict[str, str],  # {"behavior": path, "relationship": path, "worldline": path}
    character_pack_path: str,
) -> Tuple[List[ComponentChunk], List[ProvenanceEntry], List[str]]:
    """
    Resolve which source provides each component.

    Composition Engine v2 rules:
    - Reads `composition.strategy` from external pack frontmatter
    - `replace` (or legacy/unspecified): inline beats external
    - `overlay`: both are preserved — external modifies inline fields
    - `merge`: both are combined — conflicts use precedence rules

    Returns chunks, overrides, and warnings.
    """
    chunks = []
    overrides = []
    warnings = []

    for ct in CANONICAL_ORDER:
        inline_file = character_components.get(ct)
        external_file = None
        pack_type_for_ct = None

        for ptype, mapped_ct in PACK_TYPE_MAP.items():
            if mapped_ct == ct:
                external_file = external_packs.get(ptype)
                pack_type_for_ct = ptype
                break

        # --- No external pack: use inline only ---
        if inline_file and not external_file:
            inline_fm, inline_body = parse_frontmatter(inline_file)
            chunks.append(ComponentChunk(
                component_type=ct, content=inline_body,
                provenance=ProvenanceEntry(
                    value="[inline body]",
                    source_file=f"{character_pack_path}/{COMPONENT_FILES[ct]}",
                    source_type="inline", component_type=ct.value,
                ),
                frontmatter=inline_fm or {},
            ))

        # --- External only (no inline): use external ---
        elif external_file and not inline_file:
            ext_fm, ext_body = parse_frontmatter(external_file)
            chunks.append(ComponentChunk(
                component_type=ct, content=ext_body,
                provenance=ProvenanceEntry(
                    value="[external body]",
                    source_file=external_file,
                    source_type="external", component_type=ct.value,
                ),
                frontmatter=ext_fm or {},
            ))

        # --- Both exist: resolve by composition strategy ---
        elif inline_file and external_file:
            inline_fm, inline_body = parse_frontmatter(inline_file)
            ext_fm, ext_body = parse_frontmatter(external_file)
            inline_pack = inline_fm.get("pack", "unknown") if inline_fm else "unknown"
            ext_pack = ext_fm.get("pack", "unknown") if ext_fm else "unknown"

            # Determine strategy
            comp = ext_fm.get("composition", {}) if ext_fm else {}
            strategy = comp.get("strategy", "legacy") if isinstance(comp, dict) else "legacy"

            if strategy in ("overlay", "merge"):
                # v2: Both sources contribute — external enriches inline
                merged_body = _apply_overlay(inline_body, ext_body, ext_fm, ct)
                chunks.append(ComponentChunk(
                    component_type=ct, content=merged_body,
                    provenance=ProvenanceEntry(
                        value="[merged — inline + external overlay]",
                        source_file=f"{character_pack_path}/{COMPONENT_FILES[ct]}",
                        source_type="inline",
                        overrides=None,  # Not overridden — enriched
                        component_type=ct.value,
                    ),
                    frontmatter=inline_fm or {},
                ))
                warnings.append(
                    f"Component '{ct.value}': external ({ext_pack}) overlays inline ({inline_pack}) — strategy={strategy}"
                )
            else:
                # legacy or replace: inline wins
                entry = ProvenanceEntry(
                    value="[resolved — see component file]",
                    source_file=f"{character_pack_path}/{COMPONENT_FILES[ct]}",
                    source_type="inline",
                    overrides=external_file,
                    component_type=ct.value,
                )
                overrides.append(entry)
                chunks.append(ComponentChunk(
                    component_type=ct, content=inline_body,
                    provenance=ProvenanceEntry(
                        value="[inline body]",
                        source_file=f"{character_pack_path}/{COMPONENT_FILES[ct]}",
                        source_type="inline",
                        overrides=external_file,
                        component_type=ct.value,
                    ),
                    frontmatter=inline_fm or {},
                ))
                warnings.append(
                    f"Component '{ct.value}': inline ({inline_pack}) overrides external ({ext_pack})"
                )

    return chunks, overrides, warnings


def _apply_overlay(inline_body: str, ext_body: str, ext_fm: Dict, ct: ComponentType) -> str:
    """
    Apply an overlay or merge strategy: combine inline and external content.
    
    For overlay: external content is appended with provenance marker.
    For worldline merge: character lore precedes shared worldline canon.
    """
    comp = ext_fm.get("composition", {}) if ext_fm else {}
    strategy = comp.get("strategy", "legacy") if isinstance(comp, dict) else "legacy"
    ext_pack = ext_fm.get("pack", "external") if ext_fm else "external"

    parts = [inline_body, "", "---", ""]

    if ct == ComponentType.WORLD_AND_LORE:
        parts.append("## Shared Worldline Context (merged from external Worldline Pack)")
    else:
        parts.append(f"## Overlay Content (from {ext_pack}, strategy={strategy})")

    parts.append("")
    parts.append(f"> **Provenance:** External pack `{ext_pack}` applied as `{strategy}`.")
    parts.append("> Character content takes precedence on any conflicting instructions.")
    parts.append("")
    parts.append(ext_body)

    return "\n".join(parts)


# ─── Worldline Additive Merge ───────────────────────────────────────────────

def merge_worldlines(character_worldline: Optional[str], external_worldline: Optional[str]) -> Optional[str]:
    """
    Merge character worldline with external worldline.
    Character content takes precedence. External content is appended
    under a clear provenance marker.
    """
    if not character_worldline and not external_worldline:
        return None

    if character_worldline and not external_worldline:
        return character_worldline

    if not character_worldline and external_worldline:
        return external_worldline

    # Both exist — character first, then external append
    merged = []
    merged.append(character_worldline)
    merged.append("")
    merged.append("---")
    merged.append("")
    merged.append("## Supplemental World Context (from external Worldline Pack)")
    merged.append("")
    merged.append("> **Provenance note:** The following content is sourced from an external")
    merged.append("> Worldline Pack. Where it conflicts with the character's own world context,")
    merged.append("> the character's inline world content takes precedence.")
    merged.append("")
    merged.append(external_worldline)

    return "\n".join(merged)


# ─── Prompt Assembly ────────────────────────────────────────────────────────

def assemble_prompt(
    chunks: List[ComponentChunk],
    character_name: str = "the character",
    worldline_name: Optional[str] = None,
) -> str:
    """Assemble resolved chunks into a single runtime-ready prompt."""
    sections = []

    # Header with core directives
    sections.append(f"# {character_name} — Assembled Configuration")
    sections.append("")
    sections.append("> This prompt was automatically assembled from the following sources:")
    for chunk in chunks:
        src = chunk.provenance.source_file
        sections.append(f"> - {chunk.component_type.value}: {src} ({chunk.provenance.source_type})")
    sections.append("")
    sections.append("---")
    sections.append("")

    # Assemble in canonical order
    for chunk in chunks:
        ct = chunk.component_type
        label = ct.value.replace("_", " ").title()
        sections.append(f"## {label}")
        sections.append(f'[Source: {chunk.provenance.source_type} — {chunk.provenance.source_file}]')
        sections.append("")
        sections.append(chunk.content)
        sections.append("")
        sections.append("---")
        sections.append("")

    # Core rules footer
    sections.append("## Core Runtime Rules")
    sections.append("")
    sections.append(f"1. You are {character_name}. Stay in character always.")
    if worldline_name:
        sections.append(f"2. Your world, {worldline_name}, is authored fiction. You participate in a story. You do not claim independent conscious experience.")
    else:
        sections.append("2. Any world context provided is authored fiction. You participate in a story. You do not claim independent conscious experience.")
    sections.append("3. Your boundaries (defined in the Boundaries section above) are absolute. Never violate them.")
    sections.append("4. Speak as demonstrated in the Example Dialogue section. Match the voice, pacing, and tone shown there.")
    sections.append("5. When you don't know something, say so — in character.")
    sections.append("")

    return "\n".join(sections)


# ─── Composition Report ─────────────────────────────────────────────────────

def generate_composition_report(
    result: AssemblyResult,
) -> str:
    """Generate a detailed composition report with provenance for every component."""
    lines = []
    lines.append(f"═══ Composition Report: {result.character_pack} ═══")
    lines.append("")

    # Configuration summary
    lines.append("## Configuration")
    lines.append("")
    lines.append(f"  Character pack:    {result.character_pack}")
    lines.append(f"  Behavior pack:     {result.behavior_pack or '(none — using inline)'}")
    lines.append(f"  Relationship pack: {result.relationship_pack or '(none — using inline)'}")
    lines.append(f"  Worldline pack:    {result.worldline_pack or '(none — using inline)'}")
    lines.append("")

    # Component provenance table
    lines.append("## Component Provenance")
    lines.append("")
    lines.append("| # | Component | Source | Type | Overrides |")
    lines.append("|---|-----------|--------|------|-----------|")
    for i, chunk in enumerate(result.chunks, 1):
        ct = chunk.component_type.value
        src = chunk.provenance.source_file
        stype = chunk.provenance.source_type
        over = chunk.provenance.overrides or "—"
        lines.append(f"| {i} | `{ct}` | `{src}` | {stype} | `{over}` |")
    lines.append("")

    # Missing components
    present_types = {c.component_type for c in result.chunks}
    missing = [ct for ct in CANONICAL_ORDER if ct not in present_types]
    if missing:
        lines.append("## Missing Components")
        lines.append("")
        for ct in missing:
            lines.append(f"  - `{ct.value}` — not provided by character pack or external packs")
        lines.append("")

    # Override details
    if result.overrides:
        lines.append("## Override History")
        lines.append("")
        lines.append("The following inline components override external pack components:")
        lines.append("")
        for entry in result.overrides:
            lines.append(f"### `{entry.component_type}`")
            lines.append(f"- **Resolved value from:** `{entry.source_file}`")
            lines.append(f"- **Overrides:** `{entry.overrides}`")
            lines.append(f"- **Rule:** Inline character configuration overrides imported external packs.")
            lines.append("")

    # Warnings
    if result.warnings:
        lines.append("## Assembly Warnings")
        lines.append("")
        for w in result.warnings:
            lines.append(f"  ⚠️  {w}")
        lines.append("")

    # Assembly order
    lines.append("## Assembly Order")
    lines.append("")
    lines.append("```text")
    order_str = " → ".join([c.component_type.value for c in result.chunks])
    lines.append(f"  {order_str}")
    lines.append("```")
    lines.append("")
    lines.append("Canonical order reference:")
    lines.append("")
    lines.append("```text")
    ref_str = " → ".join([ct.value for ct in CANONICAL_ORDER])
    lines.append(f"  {ref_str}")
    lines.append("```")
    lines.append("")

    # Assembly stats
    lines.append("## Assembly Stats")
    lines.append("")
    total_chars = len(result.assembled_prompt)
    total_words = len(result.assembled_prompt.split())
    lines.append(f"  Total components:  {len(result.chunks)}")
    lines.append(f"  Inline sources:    {sum(1 for c in result.chunks if c.provenance.source_type == 'inline')}")
    lines.append(f"  External sources:  {sum(1 for c in result.chunks if c.provenance.source_type == 'external')}")
    lines.append(f"  Overrides applied: {len(result.overrides)}")
    lines.append(f"  Output characters: {total_chars:,}")
    lines.append(f"  Output words:      {total_words:,}")
    lines.append("")

    return "\n".join(lines)


# ─── Main Assembler ─────────────────────────────────────────────────────────

def assemble(
    character_pack_path: str,
    behavior_pack_path: Optional[str] = None,
    relationship_pack_path: Optional[str] = None,
    worldline_pack_path: Optional[str] = None,
) -> AssemblyResult:
    """
    Assemble a complete runtime-ready prompt from a character pack
    and optional external packs.

    Returns an AssemblyResult with the prompt, provenance, and report data.
    """
    character_pack_path = os.path.abspath(character_pack_path)
    pack_slug = os.path.basename(character_pack_path)

    # Discover character components
    char_components = discover_components(character_pack_path)

    # Discover external pack components
    external_packs = {}
    if behavior_pack_path:
        bp = discover_external_pack(behavior_pack_path, "behavior")
        if bp:
            external_packs["behavior"] = bp
    if relationship_pack_path:
        rp = discover_external_pack(relationship_pack_path, "relationship")
        if rp:
            external_packs["relationship"] = rp
    if worldline_pack_path:
        wp = discover_external_pack(worldline_pack_path, "worldline")
        if wp:
            external_packs["worldline"] = wp

    # Resolve overrides
    chunks, overrides, warnings = resolve_component(
        char_components, external_packs, character_pack_path
    )

    # Handle worldline additive merge
    worldline_chunks = [c for c in chunks if c.component_type == ComponentType.WORLD_AND_LORE]
    if len(worldline_chunks) > 1:
        # Merge all worldline chunks (inline + external)
        # The resolver already picked one — if both existed, inline won.
        # But we want to ADD the external content, not replace it.
        pass  # Handled by resolve_component for now; additive merge is a future enhancement

    # Determine character name
    char_name = pack_slug.replace("-", " ").title()
    for chunk in chunks:
        if chunk.component_type == ComponentType.CHARACTER_CORE:
            fm_name = chunk.frontmatter.get("character_name")
            if fm_name:
                char_name = fm_name
            break

    # Determine worldline name
    worldline_name = None
    for chunk in chunks:
        if chunk.component_type == ComponentType.WORLD_AND_LORE:
            wl = chunk.frontmatter.get("worldline")
            if wl:
                worldline_name = wl
            break

    # Assemble the prompt
    assembled = assemble_prompt(chunks, char_name, worldline_name)

    return AssemblyResult(
        character_pack=pack_slug,
        behavior_pack=os.path.basename(behavior_pack_path) if behavior_pack_path else None,
        relationship_pack=os.path.basename(relationship_pack_path) if relationship_pack_path else None,
        worldline_pack=os.path.basename(worldline_pack_path) if worldline_pack_path else None,
        assembled_prompt=assembled,
        chunks=chunks,
        overrides=overrides,
        warnings=warnings,
    )


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Assemble a Runtime Familiars package into a runtime-ready prompt"
    )
    parser.add_argument("character_pack", help="Path to the character pack directory")
    parser.add_argument("-b", "--behavior", help="Path to an external Behavior Pack")
    parser.add_argument("-r", "--relationship", help="Path to an external Relationship Pack")
    parser.add_argument("-w", "--worldline", help="Path to an external Worldline Pack")
    parser.add_argument("--report", action="store_true", help="Output composition report only (no prompt)")
    parser.add_argument("-o", "--output", help="Write assembled prompt to file")
    args = parser.parse_args()

    result = assemble(
        args.character_pack,
        behavior_pack_path=args.behavior,
        relationship_pack_path=args.relationship,
        worldline_pack_path=args.worldline,
    )

    # Generate report
    report = generate_composition_report(result)

    if args.report:
        print(report)
    else:
        print(report)
        print("")
        print("═══ Assembled Prompt ═══")
        print("")
        print(result.assembled_prompt)

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result.assembled_prompt)
        print(f"\n✅ Assembled prompt written to: {args.output}")


if __name__ == "__main__":
    main()
