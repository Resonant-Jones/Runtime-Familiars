#!/usr/bin/env python3
"""
Runtime Familiars — Test Fixture Generator & Test Runner

Creates test fixture packages designed to trigger specific validation errors,
then runs the validator against each and verifies the correct errors are caught.
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.validate import validate_package, ValidationResult

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "test_fixtures")


def write_file(path, content):
    """Write a file, creating directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def frontmatter(fields):
    """Generate YAML frontmatter string."""
    lines = ["---"]
    for k, v in fields.items():
        if isinstance(v, list):
            lines.append(f"{k}: {json.dumps(v)}")
        elif isinstance(v, str) and "\n" in v:
            lines.append(f"{k}: >-")
            for line in v.strip().split("\n"):
                lines.append(f"  {line}")
        elif isinstance(v, str):
            lines.append(f'{k}: "{v}"')
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


def create_fixtures():
    """Create all test fixture packages."""

    base_fm = {
        "component": "character_core",
        "pack": "FIXTURE",
        "version": "1.0.0",
        "authors": ["Test"],
        "language": "en",
        "character_name": "Test Character",
        "short_description": "A test fixture.",
        "license": "personal",
    }
    base_body = "# Test\n\nTest content.\n"

    # ── 1. Valid fixture (baseline) ──────────────────────────────────────
    p = os.path.join(FIXTURES_DIR, "valid", "test-character")
    for ct, filename in [
        ("character_core", "01_CHARACTER_CORE.md"),
        ("voice_and_language", "02_VOICE_AND_LANGUAGE.md"),
        ("boundaries", "05_BOUNDARIES.md"),
        ("example_dialogue", "09_EXAMPLE_DIALOGUE.md"),
    ]:
        fm = dict(base_fm)
        fm["component"] = ct
        fm["pack"] = "test-character"
        fm["character_name"] = "Test Character"
        write_file(os.path.join(p, filename), frontmatter(fm) + "\n\n" + base_body)
    write_file(os.path.join(p, "PACKAGE.json"), json.dumps({
        "pack": "test-character", "version": "1.0.0",
        "display_name": "Test Character", "short_description": "A test.",
        "authors": ["Test"], "language": "en", "license": "personal",
        "tags": ["test"]
    }, indent=2))
    write_file(os.path.join(p, "LICENSE.md"), "# Test License\n\nTest.\n")
    print("  ✅ valid/test-character")

    # ── 2. Missing required component ────────────────────────────────────
    p = os.path.join(FIXTURES_DIR, "missing_required", "no-boundaries")
    for ct, filename in [
        ("character_core", "01_CHARACTER_CORE.md"),
        ("voice_and_language", "02_VOICE_AND_LANGUAGE.md"),
        ("example_dialogue", "09_EXAMPLE_DIALOGUE.md"),
    ]:
        fm = dict(base_fm)
        fm["component"] = ct
        fm["pack"] = "no-boundaries"
        write_file(os.path.join(p, filename), frontmatter(fm) + "\n\n" + base_body)
    write_file(os.path.join(p, "PACKAGE.json"), json.dumps({
        "pack": "no-boundaries", "version": "1.0.0",
        "display_name": "No Boundaries", "short_description": "Missing required file.",
        "authors": ["Test"], "language": "en", "license": "personal", "tags": ["test"]
    }, indent=2))
    write_file(os.path.join(p, "LICENSE.md"), "# License\n")
    print("  ✅ missing_required/no-boundaries")

    # ── 3. Missing optional component ────────────────────────────────────
    p = os.path.join(FIXTURES_DIR, "missing_optional", "no-relationship")
    for ct, filename in [
        ("character_core", "01_CHARACTER_CORE.md"),
        ("voice_and_language", "02_VOICE_AND_LANGUAGE.md"),
        ("boundaries", "05_BOUNDARIES.md"),
        ("example_dialogue", "09_EXAMPLE_DIALOGUE.md"),
    ]:
        fm = dict(base_fm)
        fm["component"] = ct
        fm["pack"] = "no-relationship"
        write_file(os.path.join(p, filename), frontmatter(fm) + "\n\n" + base_body)
    write_file(os.path.join(p, "PACKAGE.json"), json.dumps({
        "pack": "no-relationship", "version": "1.0.0",
        "display_name": "No Relationship", "short_description": "Missing optional.",
        "authors": ["Test"], "language": "en", "license": "personal", "tags": ["test"]
    }, indent=2))
    write_file(os.path.join(p, "LICENSE.md"), "# License\n")
    print("  ✅ missing_optional/no-relationship")

    # ── 4. Malformed YAML ────────────────────────────────────────────────
    p = os.path.join(FIXTURES_DIR, "malformed_yaml", "bad-yaml")
    bad_fm = "---\ncomponent: character_core\npack: bad-yaml\nversion: 1.0.0\nauthors: [unclosed list\n---\n"
    write_file(os.path.join(p, "01_CHARACTER_CORE.md"), bad_fm + base_body)
    for ct, filename in [
        ("voice_and_language", "02_VOICE_AND_LANGUAGE.md"),
        ("boundaries", "05_BOUNDARIES.md"),
        ("example_dialogue", "09_EXAMPLE_DIALOGUE.md"),
    ]:
        fm = dict(base_fm)
        fm["component"] = ct
        fm["pack"] = "bad-yaml"
        write_file(os.path.join(p, filename), frontmatter(fm) + "\n\n" + base_body)
    write_file(os.path.join(p, "PACKAGE.json"), json.dumps({
        "pack": "bad-yaml", "version": "1.0.0",
        "display_name": "Bad YAML", "short_description": "Malformed.",
        "authors": ["Test"], "language": "en", "license": "personal", "tags": ["test"]
    }, indent=2))
    write_file(os.path.join(p, "LICENSE.md"), "# License\n")
    print("  ✅ malformed_yaml/bad-yaml")

    # ── 5. Duplicate pack ID (same slug in two places) ───────────────────
    # We simulate by having two packs with the same slug
    p = os.path.join(FIXTURES_DIR, "duplicate_pack_id", "dup-a")
    for ct, filename in [
        ("character_core", "01_CHARACTER_CORE.md"),
        ("voice_and_language", "02_VOICE_AND_LANGUAGE.md"),
        ("boundaries", "05_BOUNDARIES.md"),
        ("example_dialogue", "09_EXAMPLE_DIALOGUE.md"),
    ]:
        fm = dict(base_fm)
        fm["component"] = ct
        fm["pack"] = "duplicate-slug"
        write_file(os.path.join(p, filename), frontmatter(fm) + "\n\n" + base_body)
    write_file(os.path.join(p, "PACKAGE.json"), json.dumps({
        "pack": "duplicate-slug", "version": "1.0.0",
        "display_name": "Dup A", "short_description": "A.",
        "authors": ["Test"], "language": "en", "license": "personal", "tags": ["test"]
    }, indent=2))
    write_file(os.path.join(p, "LICENSE.md"), "# License\n")

    p2 = os.path.join(FIXTURES_DIR, "duplicate_pack_id", "dup-b")
    for ct, filename in [
        ("character_core", "01_CHARACTER_CORE.md"),
        ("voice_and_language", "02_VOICE_AND_LANGUAGE.md"),
        ("boundaries", "05_BOUNDARIES.md"),
        ("example_dialogue", "09_EXAMPLE_DIALOGUE.md"),
    ]:
        fm = dict(base_fm)
        fm["component"] = ct
        fm["pack"] = "duplicate-slug"
        write_file(os.path.join(p2, filename), frontmatter(fm) + "\n\n" + base_body)
    write_file(os.path.join(p2, "PACKAGE.json"), json.dumps({
        "pack": "duplicate-slug", "version": "1.0.0",
        "display_name": "Dup B", "short_description": "B.",
        "authors": ["Other"], "language": "en", "license": "personal", "tags": ["test"]
    }, indent=2))
    write_file(os.path.join(p2, "LICENSE.md"), "# License\n")
    print("  ✅ duplicate_pack_id/dup-a + dup-b")

    # ── 6. Duplicate component ID ────────────────────────────────────────
    p = os.path.join(FIXTURES_DIR, "duplicate_component_id", "dup-comp")
    # Two files both claiming to be character_core
    fm1 = dict(base_fm)
    fm1["component"] = "character_core"
    fm1["pack"] = "dup-comp"
    write_file(os.path.join(p, "01_CHARACTER_CORE.md"), frontmatter(fm1) + "\n\n" + base_body)

    # Create a second file also claiming character_core (simulate with an extra file)
    fm2 = dict(base_fm)
    fm2["component"] = "character_core"
    fm2["pack"] = "dup-comp"
    write_file(os.path.join(p, "01_CHARACTER_CORE_COPY.md"), frontmatter(fm2) + "\n\n" + base_body)

    for ct, filename in [
        ("voice_and_language", "02_VOICE_AND_LANGUAGE.md"),
        ("boundaries", "05_BOUNDARIES.md"),
        ("example_dialogue", "09_EXAMPLE_DIALOGUE.md"),
    ]:
        fm = dict(base_fm)
        fm["component"] = ct
        fm["pack"] = "dup-comp"
        write_file(os.path.join(p, filename), frontmatter(fm) + "\n\n" + base_body)
    write_file(os.path.join(p, "PACKAGE.json"), json.dumps({
        "pack": "dup-comp", "version": "1.0.0",
        "display_name": "Dup Component", "short_description": "Dup comp.",
        "authors": ["Test"], "language": "en", "license": "personal", "tags": ["test"]
    }, indent=2))
    write_file(os.path.join(p, "LICENSE.md"), "# License\n")
    print("  ✅ duplicate_component_id/dup-comp")

    # ── 7. Incompatible version ──────────────────────────────────────────
    p = os.path.join(FIXTURES_DIR, "incompatible_version", "bad-version")
    for ct, filename in [
        ("character_core", "01_CHARACTER_CORE.md"),
        ("voice_and_language", "02_VOICE_AND_LANGUAGE.md"),
        ("boundaries", "05_BOUNDARIES.md"),
        ("example_dialogue", "09_EXAMPLE_DIALOGUE.md"),
    ]:
        fm = dict(base_fm)
        fm["component"] = ct
        fm["pack"] = "bad-version"
        fm["version"] = "not-a-version"
        write_file(os.path.join(p, filename), frontmatter(fm) + "\n\n" + base_body)
    write_file(os.path.join(p, "PACKAGE.json"), json.dumps({
        "$schema": "https://runtimefamiliarsspec.org/v0/broken.schema.json",
        "pack": "bad-version", "version": "not-semver",
        "display_name": "Bad Version", "short_description": "Bad ver.",
        "authors": ["Test"], "language": "en", "license": "personal", "tags": ["test"]
    }, indent=2))
    write_file(os.path.join(p, "LICENSE.md"), "# License\n")
    print("  ✅ incompatible_version/bad-version")

    # ── 8. Unresolved package references ─────────────────────────────────
    p = os.path.join(FIXTURES_DIR, "unresolved_reference", "missing-dep")
    for ct, filename in [
        ("character_core", "01_CHARACTER_CORE.md"),
        ("voice_and_language", "02_VOICE_AND_LANGUAGE.md"),
        ("boundaries", "05_BOUNDARIES.md"),
        ("example_dialogue", "09_EXAMPLE_DIALOGUE.md"),
    ]:
        fm = dict(base_fm)
        fm["component"] = ct
        fm["pack"] = "missing-dep"
        write_file(os.path.join(p, filename), frontmatter(fm) + "\n\n" + base_body)
    write_file(os.path.join(p, "PACKAGE.json"), json.dumps({
        "pack": "missing-dep", "version": "1.0.0",
        "display_name": "Missing Dep", "short_description": "Has unresolved requires.",
        "authors": ["Test"], "language": "en", "license": "personal",
        "tags": ["test"],
        "requires": ["nonexistent-pack"],
        "worldline": "nonexistent-worldline"
    }, indent=2))
    write_file(os.path.join(p, "LICENSE.md"), "# License\n")
    print("  ✅ unresolved_reference/missing-dep")

    # ── 9. Conflicting overrides ─────────────────────────────────────────
    p = os.path.join(FIXTURES_DIR, "conflicting_override", "conflict")
    # Character has inline behavior, PACKAGE.json also requires external behavior
    for ct, filename in [
        ("character_core", "01_CHARACTER_CORE.md"),
        ("voice_and_language", "02_VOICE_AND_LANGUAGE.md"),
        ("behavior_rules", "04_BEHAVIOR_RULES.md"),
        ("boundaries", "05_BOUNDARIES.md"),
        ("example_dialogue", "09_EXAMPLE_DIALOGUE.md"),
    ]:
        fm = dict(base_fm)
        fm["component"] = ct
        fm["pack"] = "conflict"
        write_file(os.path.join(p, filename), frontmatter(fm) + "\n\n" + base_body)
    write_file(os.path.join(p, "PACKAGE.json"), json.dumps({
        "pack": "conflict", "version": "1.0.0",
        "display_name": "Conflict", "short_description": "Has inline + external.",
        "authors": ["Test"], "language": "en", "license": "personal",
        "tags": ["test"],
        "requires": ["gentle-companion"]
    }, indent=2))
    write_file(os.path.join(p, "LICENSE.md"), "# License\n")
    print("  ✅ conflicting_override/conflict")

    # ── 10. Empty component file ─────────────────────────────────────────
    p = os.path.join(FIXTURES_DIR, "empty_component", "empty-file")
    write_file(os.path.join(p, "01_CHARACTER_CORE.md"), "")  # Empty file
    for ct, filename in [
        ("voice_and_language", "02_VOICE_AND_LANGUAGE.md"),
        ("boundaries", "05_BOUNDARIES.md"),
        ("example_dialogue", "09_EXAMPLE_DIALOGUE.md"),
    ]:
        fm = dict(base_fm)
        fm["component"] = ct
        fm["pack"] = "empty-file"
        write_file(os.path.join(p, filename), frontmatter(fm) + "\n\n" + base_body)
    write_file(os.path.join(p, "PACKAGE.json"), json.dumps({
        "pack": "empty-file", "version": "1.0.0",
        "display_name": "Empty File", "short_description": "Has empty component.",
        "authors": ["Test"], "language": "en", "license": "personal", "tags": ["test"]
    }, indent=2))
    write_file(os.path.join(p, "LICENSE.md"), "# License\n")
    print("  ✅ empty_component/empty-file")

    # ── 11. Wrong assembly order fixture ─────────────────────────────────
    # Create a pack with components but verify the canonical order is enforced
    # (This is tested in the assembler, not the validator directly)
    p = os.path.join(FIXTURES_DIR, "wrong_assembly_order", "reordered")
    for ct, filename in [
        ("character_core", "01_CHARACTER_CORE.md"),
        ("voice_and_language", "02_VOICE_AND_LANGUAGE.md"),
        ("boundaries", "05_BOUNDARIES.md"),
        ("example_dialogue", "09_EXAMPLE_DIALOGUE.md"),
        ("behavior_rules", "04_BEHAVIOR_RULES.md"),
    ]:
        fm = dict(base_fm)
        fm["component"] = ct
        fm["pack"] = "reordered"
        write_file(os.path.join(p, filename), frontmatter(fm) + "\n\n" + base_body)
    write_file(os.path.join(p, "PACKAGE.json"), json.dumps({
        "pack": "reordered", "version": "1.0.0",
        "display_name": "Reordered", "short_description": "Test assembly order.",
        "authors": ["Test"], "language": "en", "license": "personal", "tags": ["test"]
    }, indent=2))
    write_file(os.path.join(p, "LICENSE.md"), "# License\n")
    print("  ✅ wrong_assembly_order/reordered")

    print(f"\n✅ All {11} test fixtures created.")


def run_tests():
    """Run the validator against all test fixtures and report results."""
    results = {}

    test_cases = [
        # (fixture_path, expected_valid, description)
        ("valid/test-character", True, "Valid package should pass"),
        ("missing_required/no-boundaries", False, "Missing required component (boundaries)"),
        ("missing_optional/no-relationship", True, "Missing optional component should pass"),
        ("malformed_yaml/bad-yaml", False, "Malformed YAML frontmatter"),
        ("empty_component/empty-file", False, "Empty component file"),
        ("incompatible_version/bad-version", False, "Invalid semantic version"),
        ("wrong_assembly_order/reordered", True, "Reordered files still validate (assembly order tested separately)"),
        ("unresolved_reference/missing-dep", True, "Unresolved references are warnings, not errors"),
        ("conflicting_override/conflict", True, "Conflicting overrides are assembly-time, not validation errors"),
    ]

    print("\n" + "=" * 70)
    print("VALIDATION TEST SUITE")
    print("=" * 70)

    all_passed = True
    for fixture_path, expected_valid, description in test_cases:
        full_path = os.path.join(FIXTURES_DIR, fixture_path)
        if not os.path.exists(full_path):
            print(f"  ⚠️  SKIP: {fixture_path} — directory not found")
            continue

        result = validate_package(full_path)
        actual_valid = result.is_valid
        passed = actual_valid == expected_valid

        status = "✅ PASS" if passed else "❌ FAIL"
        if not passed:
            all_passed = False

        print(f"\n{status}: {description}")
        print(f"     Expected valid={expected_valid}, got valid={actual_valid}")
        print(f"     Errors: {len(result.errors)}, Warnings: {len(result.warnings)}")
        for e in result.errors:
            print(f"       ❌ {e.file}: {e.message}")
        for w in result.warnings[:3]:  # Show first 3 warnings
            print(f"       ⚠️  {w.file}: {w.message}")

        results[fixture_path] = {
            "description": description,
            "expected_valid": expected_valid,
            "actual_valid": actual_valid,
            "passed": passed,
            "errors": [{"file": e.file, "message": e.message} for e in result.errors],
            "warnings": [{"file": w.file, "message": w.message} for w in result.warnings],
        }

    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70)

    # Write results JSON for programmatic consumption
    results_path = os.path.join(FIXTURES_DIR, "test_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to: {results_path}")

    return all_passed


if __name__ == "__main__":
    create_fixtures()
    success = run_tests()
    sys.exit(0 if success else 1)
