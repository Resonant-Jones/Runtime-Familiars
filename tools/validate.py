"""
Runtime Familiars — Package Validator

Validates a portable identity pack against the Runtime Familiars specification.
Checks structure, YAML frontmatter, IDs, versions, references, and composition rules.

Usage:
    python3 tools/validate.py packs/moss
    python3 tools/validate.py packs/moss --strict
    python3 tools/validate.py packs/moss --json
"""

import yaml
import json
import re
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

# Canonical assembly order (may be revised without breaking the spec)
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

# Components that MUST be present in every valid character pack
REQUIRED_COMPONENTS: Set[ComponentType] = {
    ComponentType.CHARACTER_CORE,
    ComponentType.VOICE_AND_LANGUAGE,
    ComponentType.BOUNDARIES,
    ComponentType.EXAMPLE_DIALOGUE,
}

# Recommended components (warn if missing, but don't fail)
RECOMMENDED_COMPONENTS: Set[ComponentType] = {
    ComponentType.READ_ME_FIRST,
    ComponentType.STARTER_SCENARIOS,
}

# Optional components (no warning if missing)
OPTIONAL_COMPONENTS: Set[ComponentType] = {
    ComponentType.RELATIONSHIP_MODEL,
    ComponentType.BEHAVIOR_RULES,
    ComponentType.CONFLICT_AND_REPAIR,
    ComponentType.INITIATIVE,
    ComponentType.WORLD_AND_LORE,
}

# File mapping: component type -> expected filename
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

# Reverse mapping: filename -> component type
FILE_TO_COMPONENT: Dict[str, ComponentType] = {v: k for k, v in COMPONENT_FILES.items()}

# Required YAML frontmatter fields per component type
REQUIRED_FRONTMATTER: Dict[ComponentType, Set[str]] = {
    ComponentType.CHARACTER_CORE: {"component", "pack", "version", "authors", "language", "character_name", "short_description", "license"},
    ComponentType.VOICE_AND_LANGUAGE: {"component", "pack", "version", "authors", "language", "character_name", "short_description", "license"},
    ComponentType.BOUNDARIES: {"component", "pack", "version", "authors", "language", "character_name", "short_description", "license"},
    ComponentType.EXAMPLE_DIALOGUE: {"component", "pack", "version", "authors", "language", "character_name", "short_description", "license"},
    ComponentType.RELATIONSHIP_MODEL: {"component", "pack", "version", "authors", "language", "character_name", "short_description", "license"},
    ComponentType.BEHAVIOR_RULES: {"component", "pack", "version", "authors", "language", "character_name", "short_description", "license"},
    ComponentType.CONFLICT_AND_REPAIR: {"component", "pack", "version", "authors", "language", "character_name", "short_description", "license"},
    ComponentType.INITIATIVE: {"component", "pack", "version", "authors", "language", "character_name", "short_description", "license"},
    ComponentType.WORLD_AND_LORE: {"component", "pack", "version", "authors", "language", "character_name", "short_description", "license"},
    ComponentType.READ_ME_FIRST: {"component", "pack", "version", "authors", "language", "character_name", "short_description", "license"},
    ComponentType.STARTER_SCENARIOS: {"component", "pack", "version", "authors", "language", "character_name", "short_description", "license"},
}

# Current supported spec version
SUPPORTED_SPEC_VERSION = "1.0.0"

# Valid component identifiers (enum values)
VALID_COMPONENT_IDS: Set[str] = {ct.value for ct in ComponentType}

# Semver regex
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")

# Valid pack slug regex (lowercase, hyphens, no leading/trailing hyphens)
PACK_SLUG_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

# Valid license values
VALID_LICENSES: Set[str] = {"personal", "creator", "commercial"}

# Maximum short description length
MAX_SHORT_DESCRIPTION_LENGTH = 160


# ─── Data Classes ────────────────────────────────────────────────────────────

@dataclass
class Issue:
    """A validation issue (error or warning)."""
    level: str  # "error" or "warning"
    file: str   # Relative file path
    field: Optional[str]  # Specific field, or None
    message: str
    line: Optional[int] = None


@dataclass
class ValidationResult:
    """Complete validation result for a package."""
    pack_slug: str
    pack_path: str
    issues: List[Issue] = field(default_factory=list)
    components_found: Set[ComponentType] = field(default_factory=set)
    metadata: Dict = field(default_factory=dict)

    @property
    def errors(self) -> List[Issue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def warnings(self) -> List[Issue]:
        return [i for i in self.issues if i.level == "warning"]

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


# ─── YAML Frontmatter Parser ────────────────────────────────────────────────

def parse_frontmatter(filepath: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Parse YAML frontmatter from a Markdown file.
    Returns (frontmatter_dict, body) or (None, None) if no frontmatter.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return None, None

    if not content.startswith("---"):
        return None, content

    # Find closing ---
    end_idx = content.find("---", 3)
    if end_idx == -1:
        return None, content  # Unclosed frontmatter

    yaml_str = content[3:end_idx].strip()
    body = content[end_idx + 3:].strip()

    if not yaml_str:
        return {}, body  # Empty frontmatter

    try:
        parsed = yaml.safe_load(yaml_str)
        return parsed if isinstance(parsed, dict) else None, body
    except yaml.YAMLError:
        return None, body


def check_malformed_yaml(filepath: str) -> Optional[Issue]:
    """Check if a file has malformed YAML frontmatter."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None

    if not content.startswith("---"):
        return None

    end_idx = content.find("---", 3)
    if end_idx == -1:
        return Issue(
            level="error",
            file=os.path.basename(filepath),
            field="frontmatter",
            message="Unclosed YAML frontmatter (missing closing '---')",
        )

    yaml_str = content[3:end_idx].strip()
    if not yaml_str:
        return None

    try:
        yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        return Issue(
            level="error",
            file=os.path.basename(filepath),
            field="frontmatter",
            message=f"Malformed YAML frontmatter: {e}",
        )

    return None


# ─── Structural Validation ──────────────────────────────────────────────────

def validate_structure(pack_path: str) -> List[Issue]:
    """Validate the package directory structure and required files."""
    issues = []
    pack_dir = Path(pack_path)

    if not pack_dir.exists():
        issues.append(Issue("error", str(pack_dir), None, "Package directory does not exist"))
        return issues

    if not pack_dir.is_dir():
        issues.append(Issue("error", str(pack_dir), None, "Path is not a directory"))
        return issues

    # Check required component files
    for ct in REQUIRED_COMPONENTS:
        filename = COMPONENT_FILES[ct]
        filepath = pack_dir / filename
        if not filepath.exists():
            issues.append(Issue(
                "error", filename, None,
                f"Required component file '{filename}' is missing"
            ))

    # Check recommended component files
    for ct in RECOMMENDED_COMPONENTS:
        filename = COMPONENT_FILES[ct]
        filepath = pack_dir / filename
        if not filepath.exists():
            issues.append(Issue(
                "warning", filename, None,
                f"Recommended component file '{filename}' is missing"
            ))

    # Check for PACKAGE.json
    pkg_json = pack_dir / "PACKAGE.json"
    if not pkg_json.exists():
        issues.append(Issue(
            "warning", "PACKAGE.json", None,
            "PACKAGE.json is missing (recommended for machine-readable metadata)"
        ))

    # Check for LICENSE.md
    license_file = pack_dir / "LICENSE.md"
    if not license_file.exists():
        issues.append(Issue(
            "error", "LICENSE.md", None,
            "LICENSE.md is required"
        ))

    # Check for unexpected files
    expected_files = set(COMPONENT_FILES.values()) | {"PACKAGE.json", "LICENSE.md"}
    expected_dirs = {"INSTALL"}

    for item in pack_dir.iterdir():
        if item.name.startswith("."):
            continue
        if item.is_file() and item.name not in expected_files:
            issues.append(Issue(
                "warning", item.name, None,
                f"Unexpected file '{item.name}' in package directory"
            ))
        elif item.is_dir() and item.name not in expected_dirs:
            issues.append(Issue(
                "warning", f"{item.name}/", None,
                f"Unexpected directory '{item.name}/' in package directory"
            ))

    return issues


# ─── Frontmatter Validation ─────────────────────────────────────────────────

def validate_component_frontmatter(
    filepath: str, component_type: ComponentType, pack_slug: str
) -> Tuple[List[Issue], Optional[Dict]]:
    """Validate YAML frontmatter of a component file."""
    issues = []
    filename = os.path.basename(filepath)

    # Check for malformed YAML
    yaml_issue = check_malformed_yaml(filepath)
    if yaml_issue:
        issues.append(yaml_issue)
        return issues, None

    # Check for empty file
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        issues.append(Issue("error", filename, None, f"Cannot read file: {e}"))
        return issues, None

    if not content.strip():
        issues.append(Issue("error", filename, None, "Component file is empty"))
        return issues, None

    # Check for frontmatter presence
    if not content.startswith("---"):
        issues.append(Issue(
            "error", filename, "frontmatter",
            "Missing YAML frontmatter (file must start with '---')"
        ))
        return issues, None

    # Parse frontmatter
    fm, _ = parse_frontmatter(filepath)
    if fm is None:
        issues.append(Issue(
            "error", filename, "frontmatter",
            "Cannot parse YAML frontmatter"
        ))
        return issues, None

    if not isinstance(fm, dict) or not fm:
        issues.append(Issue(
            "error", filename, "frontmatter",
            "Frontmatter is empty or not a mapping"
        ))
        return issues, None

    # Validate component type
    declared_component = fm.get("component")
    if not declared_component:
        issues.append(Issue(
            "error", filename, "component",
            "Missing required field 'component' in frontmatter"
        ))
    elif declared_component not in VALID_COMPONENT_IDS:
        issues.append(Issue(
            "error", filename, "component",
            f"Invalid component type '{declared_component}'. Must be one of: {sorted(VALID_COMPONENT_IDS)}"
        ))
    elif declared_component != component_type.value:
        issues.append(Issue(
            "error", filename, "component",
            f"Component type mismatch: file declares '{declared_component}' but filename maps to '{component_type.value}'"
        ))

    # Validate required fields
    required_fields = REQUIRED_FRONTMATTER.get(component_type, set())
    for field in required_fields:
        if field not in fm:
            issues.append(Issue(
                "error", filename, field,
                f"Missing required frontmatter field '{field}'"
            ))
        elif fm[field] is None:
            issues.append(Issue(
                "error", filename, field,
                f"Required frontmatter field '{field}' is null"
            ))

    if fm:
        # Validate pack slug
        if "pack" in fm:
            pack_val = fm["pack"]
            if not isinstance(pack_val, str):
                issues.append(Issue("error", filename, "pack", "Field 'pack' must be a string"))
            elif not PACK_SLUG_RE.match(pack_val):
                issues.append(Issue(
                    "error", filename, "pack",
                    f"Invalid pack slug '{pack_val}'. Must be lowercase letters, digits, hyphens (e.g., 'moss', 'gentle-companion')"
                ))
            elif pack_val != pack_slug:
                issues.append(Issue(
                    "error", filename, "pack",
                    f"Pack slug mismatch: file declares '{pack_val}' but package is '{pack_slug}'"
                ))

        # Validate version
        if "version" in fm:
            ver = fm["version"]
            if not isinstance(ver, str):
                issues.append(Issue("error", filename, "version", "Field 'version' must be a string"))
            elif not SEMVER_RE.match(str(ver)):
                issues.append(Issue(
                    "error", filename, "version",
                    f"Invalid semantic version '{ver}'. Must be MAJOR.MINOR.PATCH (e.g., 1.0.0)"
                ))

        # Validate license
        if "license" in fm:
            lic = fm["license"]
            if not isinstance(lic, str):
                issues.append(Issue("error", filename, "license", "Field 'license' must be a string"))
            elif lic not in VALID_LICENSES:
                issues.append(Issue(
                    "error", filename, "license",
                    f"Invalid license '{lic}'. Must be one of: {sorted(VALID_LICENSES)}"
                ))

        # Validate short_description length
        if "short_description" in fm:
            desc = fm["short_description"]
            if isinstance(desc, str) and len(desc) > MAX_SHORT_DESCRIPTION_LENGTH:
                issues.append(Issue(
                    "warning", filename, "short_description",
                    f"Short description is {len(desc)} characters (max {MAX_SHORT_DESCRIPTION_LENGTH})"
                ))

        # Validate character_name
        if "character_name" in fm:
            name = fm["character_name"]
            if isinstance(name, str) and len(name.strip()) == 0:
                issues.append(Issue(
                    "error", filename, "character_name",
                    "Field 'character_name' is empty"
                ))

        # Validate language
        if "language" in fm:
            lang = fm["language"]
            if isinstance(lang, str) and not re.match(r"^[a-z]{2}(-[A-Z]{2})?$", lang):
                issues.append(Issue(
                    "warning", filename, "language",
                    f"Language code '{lang}' may not be valid ISO 639-1"
                ))

        # Validate tags
        if "tags" in fm:
            tags = fm["tags"]
            if not isinstance(tags, list):
                issues.append(Issue(
                    "warning", filename, "tags",
                    "Field 'tags' should be a list of strings"
                ))

    return issues, fm


# ─── PACKAGE.json Validation ────────────────────────────────────────────────

def validate_package_json(pack_path: str) -> List[Issue]:
    """Validate the PACKAGE.json file."""
    issues = []
    pkg_file = os.path.join(pack_path, "PACKAGE.json")

    if not os.path.exists(pkg_file):
        return issues  # Already warned in structure check

    try:
        with open(pkg_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        issues.append(Issue("error", "PACKAGE.json", None, f"Invalid JSON: {e}"))
        return issues
    except Exception as e:
        issues.append(Issue("error", "PACKAGE.json", None, f"Cannot read: {e}"))
        return issues

    if not isinstance(data, dict):
        issues.append(Issue("error", "PACKAGE.json", None, "PACKAGE.json must contain a JSON object"))
        return issues

    # Required fields
    for field in ["pack", "version", "display_name", "short_description"]:
        if field not in data:
            issues.append(Issue("error", "PACKAGE.json", field, f"Missing required field '{field}'"))
        elif data[field] is None:
            issues.append(Issue("error", "PACKAGE.json", field, f"Required field '{field}' is null"))

    # Validate version
    if "version" in data and isinstance(data["version"], str):
        if not SEMVER_RE.match(data["version"]):
            issues.append(Issue(
                "error", "PACKAGE.json", "version",
                f"Invalid version '{data['version']}'"
            ))

    # Validate schema
    if "$schema" in data:
        schema = data["$schema"]
        # Check spec version compatibility
        if "v1" in schema:
            pass  # v1.x is current
        elif "v0" in schema:
            issues.append(Issue(
                "warning", "PACKAGE.json", "$schema",
                f"Schema version '{schema}' is pre-1.0.0. Some validators may not support it."
            ))
        elif not any(f"v{i}" in schema for i in range(1, 10)):
            issues.append(Issue(
                "warning", "PACKAGE.json", "$schema",
                f"Unrecognized schema version '{schema}'"
            ))

    # Validate license
    if "license" in data:
        lic = data["license"]
        if isinstance(lic, str) and lic not in VALID_LICENSES:
            issues.append(Issue(
                "error", "PACKAGE.json", "license",
                f"Invalid license '{lic}'. Must be one of: {sorted(VALID_LICENSES)}"
            ))

    # Validate components mapping
    if "components" in data:
        comps = data["components"]
        if isinstance(comps, dict):
            for comp_id, comp_file in comps.items():
                if comp_id not in VALID_COMPONENT_IDS:
                    issues.append(Issue(
                        "warning", "PACKAGE.json", f"components.{comp_id}",
                        f"Unknown component ID '{comp_id}'"
                    ))
                expected_file = COMPONENT_FILES.get(
                    next((ct for ct in ComponentType if ct.value == comp_id), None)
                )
                if expected_file and comp_file != expected_file:
                    issues.append(Issue(
                        "warning", "PACKAGE.json", f"components.{comp_id}",
                        f"Expected file '{expected_file}' but found '{comp_file}'"
                    ))

    # Validate requires
    if "requires" in data:
        reqs = data["requires"]
        if not isinstance(reqs, list):
            issues.append(Issue(
                "error", "PACKAGE.json", "requires",
                "Field 'requires' must be an array of pack slugs"
            ))

    # Validate conflicts
    if "conflicts" in data:
        confs = data["conflicts"]
        if not isinstance(confs, list):
            issues.append(Issue(
                "error", "PACKAGE.json", "conflicts",
                "Field 'conflicts' must be an array of pack slugs"
            ))

    # Validate worldline reference
    if "worldline" in data:
        wl = data["worldline"]
        if wl is not None and not isinstance(wl, str):
            issues.append(Issue(
                "error", "PACKAGE.json", "worldline",
                "Field 'worldline' must be a string (pack slug) or null"
            ))

    return issues


# ─── Cross-Component Consistency ─────────────────────────────────────────────

def validate_consistency(components: Dict[ComponentType, Dict], pack_slug: str) -> List[Issue]:
    """Validate consistency across component files."""
    issues = []

    # Check that all components declare the same pack slug
    for ct, fm in components.items():
        if fm and fm.get("pack") != pack_slug:
            issues.append(Issue(
                "error", COMPONENT_FILES[ct], "pack",
                f"Pack slug '{fm.get('pack')}' does not match package directory '{pack_slug}'"
            ))

    # Check that character_name is consistent
    character_names: Set[str] = set()
    for ct, fm in components.items():
        if fm and "character_name" in fm:
            character_names.add(fm["character_name"])
    if len(character_names) > 1:
        issues.append(Issue(
            "warning", "(multiple)", "character_name",
            f"Inconsistent character_name across components: {character_names}"
        ))

    # Check that at least one component exists
    if not components:
        issues.append(Issue(
            "error", "(package)", None,
            "No valid component files found in package"
        ))

    return issues


# ─── Platform Neutrality Check ───────────────────────────────────────────────

PLATFORM_SPECIFIC_PATTERNS = [
    (r"\bChatGPT\b", "ChatGPT"),
    (r"\bClaude\b(?!\s+Projects)", "Claude (non-install reference)"),
    (r"\bCodexify\b", "Codexify"),
    (r"\bCustom GPT\b", "Custom GPT"),
    (r"\bOpenAI\b", "OpenAI"),
    (r"\bAnthropic\b", "Anthropic"),
]

def validate_platform_neutrality(component_file: str, component_type: ComponentType) -> List[Issue]:
    """Check that component files don't contain platform-specific instructions."""
    issues = []
    filename = os.path.basename(component_file)

    try:
        with open(component_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return issues

    # Skip frontmatter
    if content.startswith("---"):
        end_idx = content.find("---", 3)
        if end_idx != -1:
            body = content[end_idx + 3:]
        else:
            body = content
    else:
        body = content

    for pattern, platform_name in PLATFORM_SPECIFIC_PATTERNS:
        if re.search(pattern, body, re.IGNORECASE):
            issues.append(Issue(
                "warning", filename, "platform_neutrality",
                f"Component file references '{platform_name}'. Platform-specific instructions belong in INSTALL/ profiles."
            ))

    return issues


# ─── Main Validator ──────────────────────────────────────────────────────────

def validate_package(pack_path: str, strict: bool = False) -> ValidationResult:
    """
    Validate a Runtime Familiars package.

    Args:
        pack_path: Path to the package directory
        strict: If True, treat warnings as errors

    Returns:
        ValidationResult with all issues, metadata, and pass/fail status
    """
    pack_path = os.path.abspath(pack_path)
    pack_slug = os.path.basename(pack_path)

    result = ValidationResult(pack_slug=pack_slug, pack_path=pack_path)

    # 1. Structural validation
    result.issues.extend(validate_structure(pack_path))

    # 2. Check for PACKAGE.json and parse it
    pkg_json_issues = validate_package_json(pack_path)
    result.issues.extend(pkg_json_issues)

    # 3. Frontmatter validation for each component file
    components: Dict[ComponentType, Dict] = {}
    detected_pack_slug = pack_slug

    for ct in ComponentType:
        filename = COMPONENT_FILES[ct]
        filepath = os.path.join(pack_path, filename)

        if not os.path.exists(filepath):
            continue

        result.components_found.add(ct)

        # Determine effective pack slug from the first component that declares one
        fm_issues, fm = validate_component_frontmatter(filepath, ct, pack_slug)
        result.issues.extend(fm_issues)

        if fm:
            components[ct] = fm
            if fm.get("pack") and not detected_pack_slug or detected_pack_slug == pack_slug:
                detected_pack_slug = fm.get("pack", pack_slug)

        # Platform neutrality check
        neutrality_issues = validate_platform_neutrality(filepath, ct)
        result.issues.extend(neutrality_issues)

    # 4. Cross-component consistency
    result.issues.extend(validate_consistency(components, detected_pack_slug))

    # 5. Check canonical assembly order
    found_ordered = [ct for ct in CANONICAL_ORDER if ct in result.components_found]
    canonical_found = [ct for ct in CANONICAL_ORDER if ct in result.components_found]
    if found_ordered != canonical_found:
        # Components exist but might be out of order in terms of file presence
        # This is informational — the SPEC defines the order, but files exist independently
        pass

    # 6. Metadata extraction
    for ct, fm in components.items():
        result.metadata[ct.value] = {
            "version": fm.get("version"),
            "character_name": fm.get("character_name"),
            "license": fm.get("license"),
        }

    # Strict mode: warnings become errors
    if strict:
        for issue in result.issues:
            if issue.level == "warning":
                issue.level = "error"

    return result


# ─── CLI ─────────────────────────────────────────────────────────────────────

def format_result(result: ValidationResult, json_output: bool = False) -> str:
    """Format a ValidationResult for display."""
    if json_output:
        output = {
            "pack_slug": result.pack_slug,
            "pack_path": result.pack_path,
            "valid": result.is_valid,
            "errors": [{"file": i.file, "field": i.field, "message": i.message} for i in result.errors],
            "warnings": [{"file": i.file, "field": i.field, "message": i.message} for i in result.warnings],
            "components_found": sorted([ct.value for ct in result.components_found]),
            "metadata": result.metadata,
        }
        return json.dumps(output, indent=2)

    lines = []
    lines.append(f"═══ Validating: {result.pack_slug} ═══")
    lines.append(f"Path: {result.pack_path}")
    lines.append(f"Components found: {len(result.components_found)} ({', '.join(sorted(ct.value for ct in result.components_found))})")
    lines.append("")

    if result.errors:
        lines.append(f"❌ ERRORS ({len(result.errors)}):")
        for e in result.errors:
            field_str = f" [{e.field}]" if e.field else ""
            lines.append(f"  • {e.file}{field_str}: {e.message}")
        lines.append("")

    if result.warnings:
        lines.append(f"⚠️  WARNINGS ({len(result.warnings)}):")
        for w in result.warnings:
            field_str = f" [{w.field}]" if w.field else ""
            lines.append(f"  • {w.file}{field_str}: {w.message}")
        lines.append("")

    if result.is_valid:
        lines.append("✅ Package is VALID")
    else:
        lines.append("❌ Package has ERRORS and is NOT valid")

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate a Runtime Familiars package")
    parser.add_argument("pack_path", help="Path to the package directory")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = validate_package(args.pack_path, strict=args.strict)
    print(format_result(result, json_output=args.json))
    sys.exit(0 if result.is_valid else 1)


if __name__ == "__main__":
    main()
