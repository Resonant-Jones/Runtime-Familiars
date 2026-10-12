#!/usr/bin/env python3
"""
Runtime Familiars — Assembly Demonstration Runner

Runs all 5 composition scenarios and generates provenance-tracked
composition reports demonstrating composability is mechanically provable.
"""

import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.assemble import assemble, generate_composition_report

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assembled")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")

os.makedirs(REPORTS_DIR, exist_ok=True)

scenarios = [
    {
        "name": "moss-alone",
        "description": "Moss alone — all inline components, no external packs",
        "character": "packs/moss",
        "behavior": None,
        "relationship": None,
        "worldline": None,
    },
    {
        "name": "moss-plus-gentle-companion",
        "description": "Moss + Gentle Companion — external behavior, inline overrides",
        "character": "packs/moss",
        "behavior": "behavior-packs/gentle-companion",
        "relationship": None,
        "worldline": None,
    },
    {
        "name": "moss-plus-the-hollow",
        "description": "Moss + The Hollow — external worldline, inline overrides",
        "character": "packs/moss",
        "behavior": None,
        "relationship": None,
        "worldline": "worldline-packs/the-hollow",
    },
    {
        "name": "moss-plus-both",
        "description": "Moss + Gentle Companion + The Hollow — both externals, both overridden by inline",
        "character": "packs/moss",
        "behavior": "behavior-packs/gentle-companion",
        "relationship": None,
        "worldline": "worldline-packs/the-hollow",
    },
    {
        "name": "character-only-external-behavior",
        "description": "Character with NO inline behavior — external Gentle Companion fills in",
        "character": "tools/test_fixtures/valid/test-character",
        "behavior": "behavior-packs/gentle-companion",
        "relationship": None,
        "worldline": None,
    },
]


def resolve_path(rel_path):
    """Resolve a relative path from the project root."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", rel_path))


def main():
    all_results = []

    print("=" * 70)
    print("ASSEMBLY DEMONSTRATION SUITE")
    print("=" * 70)

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*70}")
        print(f"SCENARIO {i}: {scenario['name']}")
        print(f"  {scenario['description']}")
        print(f"{'='*70}")

        char_path = resolve_path(scenario["character"])
        beh_path = resolve_path(scenario["behavior"]) if scenario["behavior"] else None
        rel_path = resolve_path(scenario["relationship"]) if scenario["relationship"] else None
        wl_path = resolve_path(scenario["worldline"]) if scenario["worldline"] else None

        result = assemble(
            char_path,
            behavior_pack_path=beh_path,
            relationship_pack_path=rel_path,
            worldline_pack_path=wl_path,
        )

        # Generate and save report
        report = generate_composition_report(result)
        report_file = os.path.join(REPORTS_DIR, f"{scenario['name']}-report.md")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        # Save assembled prompt
        prompt_file = os.path.join(OUTPUT_DIR, f"{scenario['name']}-prompt.md")
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write(result.assembled_prompt)

        # Summary
        inline_count = sum(1 for c in result.chunks if c.provenance.source_type == "inline")
        external_count = sum(1 for c in result.chunks if c.provenance.source_type == "external")
        override_count = len(result.overrides)

        print(f"\n  Components: {len(result.chunks)} total ({inline_count} inline, {external_count} external)")
        print(f"  Overrides:  {override_count}")
        print(f"  Warnings:   {len(result.warnings)}")
        for w in result.warnings:
            print(f"    ⚠️  {w}")
        print(f"  Output:     {len(result.assembled_prompt):,} chars, ~{len(result.assembled_prompt.split()):,} words")
        print(f"\n  Report:     {report_file}")
        print(f"  Prompt:     {prompt_file}")

        all_results.append({
            "name": scenario["name"],
            "description": scenario["description"],
            "components_total": len(result.chunks),
            "inline_count": inline_count,
            "external_count": external_count,
            "overrides": [{"component": o.component_type, "inline_source": o.source_file, "overrides": o.overrides} for o in result.overrides],
            "warnings": result.warnings,
            "output_chars": len(result.assembled_prompt),
            "output_words": len(result.assembled_prompt.split()),
            "chunks": [{"component": c.component_type.value, "source": c.provenance.source_file, "type": c.provenance.source_type} for c in result.chunks],
        })

    # Write summary JSON
    summary_file = os.path.join(OUTPUT_DIR, "assembly-summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    # Print visual comparison
    print(f"\n{'='*70}")
    print("COMPOSITION COMPARISON MATRIX")
    print(f"{'='*70}")
    print(f"\n{'Scenario':<40} {'Inline':>7} {'Ext':>5} {'Ovrd':>5} {'Words':>7}")
    print("-" * 70)
    for r in all_results:
        print(f"{r['name']:<40} {r['inline_count']:>7} {r['external_count']:>5} {len(r['overrides']):>5} {r['output_words']:>7,}")

    print(f"\n{'='*70}")
    print("PROVENANCE MATRIX (which component came from where)")
    print(f"{'='*70}")

    components_list = ["character_core", "voice_and_language", "relationship_model",
                       "behavior_rules", "conflict_and_repair", "initiative",
                       "world_and_lore", "boundaries", "example_dialogue"]

    # Header
    header = f"{'Component':<25}"
    for r in all_results:
        header += f" {r['name'][:18]:<20}"
    print(header)
    print("-" * (25 + 20 * len(all_results)))

    # Rows
    for comp in components_list:
        row = f"{comp:<25}"
        for r in all_results:
            chunk = next((c for c in r["chunks"] if c["component"] == comp), None)
            if chunk:
                cell = f"{chunk['type'][:1].upper()}/{os.path.basename(chunk['source'])[:16]}"
            else:
                cell = "—"
            row += f" {cell:<20}"
        print(row)

    print(f"\n✅ All 5 assembly scenarios complete.")
    print(f"   Reports: {REPORTS_DIR}/")
    print(f"   Prompts: {OUTPUT_DIR}/")
    print(f"   Summary: {summary_file}")


if __name__ == "__main__":
    main()
