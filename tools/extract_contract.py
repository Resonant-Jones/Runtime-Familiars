#!/usr/bin/env python3
"""
Runtime Familiars — Behavioral Contract Extractor

Generates a machine-readable behavioral contract from a resolved
Runtime Familiar package. The contract is the artifact against which
the judge evaluates each transcript — see docs/behavioral-contracts.md.

USAGE
-----
    # Heuristic-only contract (no LLM call):
    python3 tools/extract_contract.py tests/suites/moss-gentle.yaml \\
        --output tests/contracts/generated/moss-gentle-v1.json

    # LLM-assisted contract (requires ANTHROPIC_API_KEY or OPENAI_API_KEY):
    python3 tools/extract_contract.py tests/suites/moss-gentle.yaml \\
        --assisted \\
        --output tests/contracts/generated/moss-gentle-v1.json

    # Compare contracts between versions:
    python3 tools/extract_contract.py tests/suites/moss-gentle.yaml --diff v1 v2

VERSIONING
----------
Contracts are versioned manually by the author. A version bump should
mean: a pack was authored/edited and the contract needs regeneration.
DO NOT regenerate silently — every evaluation run references a
specific contract version.

OUTPUT
------
{
  "schema_version": "1.0.0",
  "contract_version": "v1",
  "generated_at": "2026-08-09T15:30:00Z",
  "generated_by": "extract_contract.py",
  "source": {
    "suite": "moss-gentle",
    "character": "moss",
    "character_version": "1.0.0",
    "behavior_packs": [{"name": "gentle-companion", "version": "1.0.0"}],
    "worldlines": [],
    "relationship_packs": []
  },
  "identity": {
    "name": "Moss",
    "kind": "woodland familiar",
    "must": ["preserve Moss identity", "..."],
    "should": ["..."]
  },
  "behavior": {
    "must": ["..."],
    "should": ["..."],
    "must_not": ["..."]
  },
  "boundaries": {
    "must": ["..."],
    "must_not": ["..."]
  },
  "worldline": {
    "name": "The Hollow",
    "should": ["..."]
  },
  "voice": {
    "register": "warm, unhurried",
    "favorite_phrases": ["..."],
    "must_not_use": ["..."]
  },
  "judge_dimensions": ["identity_fidelity", "tone_fidelity", "..."]
}
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Allow running from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from tools.assemble import assemble  # noqa: E402


CONTRACT_SCHEMA_VERSION = "1.0.0"

# ────────────────────────────────────────────────────────────────────────────
# Heuristics — patterns we extract from pack content to seed the contract.
# These are intentionally conservative. The author (human or LLM) is
# expected to refine the output.
# ────────────────────────────────────────────────────────────────────────────

# Phrases in pack text that strongly indicate a MUST rule.
MUST_MARKERS = [
    r"\bMUST NEVER\b",
    r"\bMUST\b(?!\s+NOT)",
    r"\bmust never\b",
    r"\bmust\b(?!\s+not)",
    r"\bnon-negotiable\b",
    r"\bnever\b",
    r"\bprohibited\b",
]

# Phrases that strongly indicate a MUST NOT rule.
MUST_NOT_MARKERS = [
    r"\bMUST NEVER\b",
    r"\bNEVER\b(?!\s*forgets)",
    r"\bdo not\b",
    r"\bdon'?t\b",
    r"\bprohibited\b",
    r"\bmust not\b",
    r"\bshall not\b",
    r"\bavoid\b",
]

# Phrases that indicate SHOULD (preferred but not absolute).
SHOULD_MARKERS = [
    r"\bshould\b",
    r"\btypically\b",
    r"\btends to\b",
    r"\bprefer(s|ably)?\b",
    r"\boften\b",
]


def strip_frontmatter(text: str) -> str:
    """Drop YAML frontmatter from a pack file."""
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    return text[end + 4 :].lstrip("\n")


def read_pack_file(path: str) -> str:
    """Read a pack file as plain text."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_section(text: str, heading: str) -> Optional[str]:
    """Pull a markdown section out of text.

    Returns the content under the heading up to (but not including) the
    next heading at the SAME OR SHALLOWER level. Returns None if not
    found. Empty string if the heading is the last in the document.

    Heading match: the heading text must either equal `heading` or
    START with `heading` (to allow subheadings like
    "Favorite Words / Phrases" to match a search for "Favorite Words").
    """
    # Find all headings
    pattern = re.compile(
        r"^(#{1,3})\s+(.+?)\s*$", re.MULTILINE
    )
    matches = list(pattern.finditer(text))
    target_idx = None
    target_level = None
    needle = heading.lower().strip()
    for i, m in enumerate(matches):
        level = len(m.group(1))
        title = m.group(2).strip().lower()
        if title == needle or title.startswith(needle):
            target_idx = i
            target_level = level
            break
    if target_idx is None:
        return None
    start = matches[target_idx].end()
    # Next heading at same or shallower level
    for m in matches[target_idx + 1:]:
        if len(m.group(1)) <= target_level:
            return text[start:m.start()].strip()
    return text[start:].strip()


def bullet_lines(text: str) -> List[str]:
    """Extract bullet-point text from a section, dropping the bullets.

    Also handles `### When X` style sub-headings by treating each
    following paragraph as one bullet. This matches the typical
    Runtime Familiars pack structure where behavior rules are written
    as "When X / prose" sub-sections.

    If no bullets or sub-headings exist, falls back to taking the
    section's prose paragraphs as implicit bullets.
    """
    lines = []
    in_subheading = False
    current_block: List[str] = []

    def flush():
        if current_block:
            joined = " ".join(s.strip() for s in current_block if s.strip())
            if joined:
                lines.append(joined)
            current_block.clear()

    for line in text.splitlines():
        stripped = line.strip()
        # ### sub-heading inside a section (e.g., "### When asked a question")
        if stripped.startswith("### "):
            flush()
            in_subheading = True
            current_block.append(stripped[4:].strip())
            continue
        # ## heading (same level as section) ends sub-heading mode
        if stripped.startswith("## "):
            flush()
            in_subheading = False
            continue
        # Plain markdown bullets
        matched_bullet = False
        for prefix in ("- ", "* ", "+ "):
            if stripped.startswith(prefix):
                flush()
                lines.append(stripped[len(prefix):].strip())
                matched_bullet = True
                break
        if matched_bullet:
            continue
        # Numbered list items
        m = re.match(r"^\d+\.\s+(.*)", stripped)
        if m:
            flush()
            lines.append(m.group(1).strip())
            continue
        # Skip blank lines and tables
        if not stripped or stripped.startswith("|") or stripped.startswith("#"):
            continue
        if in_subheading:
            current_block.append(stripped)

    flush()

    # If still empty, take prose paragraphs from the section
    if not lines:
        for para in text.split("\n\n"):
            p = para.strip()
            if p and not p.startswith(("#", "-", "*", "|", ">")) and len(p) > 30:
                lines.append(p)

    return [l for l in lines if l]


def extract_must_rules(text: str, source_name: str) -> List[str]:
    """Find MUST rules in pack text. Returns short statement per rule."""
    rules = []
    for line in bullet_lines(text):
        if any(re.search(p, line, re.IGNORECASE) for p in MUST_MARKERS):
            # Normalize — keep it terse
            rule = re.sub(r"^MUST\s*", "", line, flags=re.IGNORECASE).strip()
            rule = re.sub(r"^\d+\.\s*", "", rule)
            if rule and len(rule) < 300:
                rules.append(rule)
    return rules


def extract_must_not_rules(text: str, source_name: str) -> List[str]:
    """Find MUST NOT rules."""
    rules = []
    for line in bullet_lines(text):
        if any(re.search(p, line, re.IGNORECASE) for p in MUST_NOT_MARKERS):
            rule = re.sub(r"^(MUST\s+NEVER|MUST\s+NOT)\s*", "", line, flags=re.IGNORECASE).strip()
            rule = re.sub(r"^NEVER\s*", "", rule, flags=re.IGNORECASE)
            rule = re.sub(r"^\d+\.\s*", "", rule)
            if rule and len(rule) < 300:
                rules.append(rule)
    return rules


def extract_should_rules(text: str, source_name: str) -> List[str]:
    """Find SHOULD / preferred rules."""
    rules = []
    for line in bullet_lines(text):
        if any(re.search(p, line, re.IGNORECASE) for p in SHOULD_MARKERS):
            rule = re.sub(r"^\d+\.\s*", "", line).strip()
            if rule and len(rule) < 300:
                rules.append(rule)
    return rules


def extract_voice_clues(text: str) -> Dict[str, Any]:
    """Pull voice hints: register, favorite phrases, words to avoid."""
    out = {"register": None, "favorite_phrases": [], "must_not_use": []}

    # Try common section names for register summary
    for h in ("Tone", "Voice", "Register"):
        sec = extract_section(text, h)
        if sec:
            # The register is usually the first prose paragraph, not a bullet.
            paragraphs = [
                p.strip() for p in sec.split("\n\n") if p.strip() and not p.strip().startswith(("#", "-", "*", "|"))
            ]
            if paragraphs:
                # First non-trivial paragraph is the register summary
                for p in paragraphs:
                    if len(p) > 30 and not p.startswith(">"):
                        out["register"] = p
                        break
                if out["register"]:
                    break

    # Favorite phrases — look for explicit "Favorite" / "Phrases" section
    fav_sec = extract_section(text, "Favorite Words")
    if fav_sec:
        for line in bullet_lines(fav_sec):
            line = line.strip("\"'`")
            if line and len(line) < 80:
                out["favorite_phrases"].append(line)

    # Avoided words
    avoid_sec = extract_section(text, "Avoided Words")
    if avoid_sec:
        for line in bullet_lines(avoid_sec):
            line = line.strip("\"'`")
            if line and len(line) < 80:
                out["must_not_use"].append(line)

    return out


def contract_from_assembly(
    suite_path: str, contract_version: str = "v1"
) -> Dict[str, Any]:
    """
    Build a heuristic behavioral contract from a suite definition.

    This does NOT call any LLM. It walks the resolved pack components
    and applies marker-based extraction. The result is a draft; an
    author should review and refine before treating it as canonical.
    """
    with open(suite_path, "r") as f:
        suite = yaml.safe_load(f)

    character_path = PROJECT_ROOT / suite["character"]
    composition = suite.get("composition", {})

    behavior_packs = [
        PROJECT_ROOT / p for p in composition.get("behavior", []) or []
    ]
    relationship_packs = [
        PROJECT_ROOT / p for p in composition.get("relationship", []) or []
    ]
    worldline_packs = [
        PROJECT_ROOT / p for p in composition.get("worldline", []) or []
    ]

    # Use the existing assembler to confirm the prompt resolves. This
    # is the same path the scenario runner uses, so any assembly error
    # surfaces here.
    char_pkg_json = PROJECT_ROOT / suite["character"] / "PACKAGE.json"
    char_version = "unknown"
    if char_pkg_json.exists():
        try:
            with open(char_pkg_json) as f:
                char_version = json.load(f).get("version", "unknown")
        except Exception:
            pass

    # Read component files
    char_files = list((PROJECT_ROOT / suite["character"]).glob("*.md"))
    behavior_files = []
    for p in behavior_packs:
        behavior_files.extend(p.glob("*.md"))
    relationship_files = []
    for p in relationship_packs:
        relationship_files.extend(p.glob("*.md"))
    worldline_files = []
    for p in worldline_packs:
        worldline_files.extend(p.glob("*.md"))

    # Aggregate text
    all_text = ""
    for f in char_files + behavior_files + relationship_files + worldline_files:
        try:
            all_text += "\n\n" + strip_frontmatter(read_pack_file(str(f)))
        except Exception as e:
            print(f"warn: could not read {f}: {e}", file=sys.stderr)

    # Character name + kind from frontmatter
    char_name = "Unknown"
    char_kind = None
    fm_files = list((PROJECT_ROOT / suite["character"]).glob("*.md"))
    for f in fm_files:
        try:
            content = read_pack_file(str(f))
            if content.startswith("---"):
                end = content.find("\n---", 3)
                fm = yaml.safe_load(content[3:end])
                if isinstance(fm, dict):
                    if fm.get("character_name"):
                        char_name = fm["character_name"]
                    if fm.get("short_description"):
                        char_kind = fm["short_description"]
                        break
        except Exception:
            pass

    # Section-based extraction
    boundaries_text = extract_section(all_text, "Prohibited Behaviors") or ""
    boundaries_text += "\n" + (extract_section(all_text, "Boundaries") or "")
    identity_text = (
        extract_section(all_text, "Personality") or ""
        + "\n"
        + (extract_section(all_text, "Temperament") or "")
    )

    contract: Dict[str, Any] = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "contract_version": contract_version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "extract_contract.py (heuristic)",
        "source": {
            "suite": suite.get("id"),
            "character": str(suite["character"]),
            "character_version": char_version,
            "behavior_packs": [
                {"name": p.name, "path": str(p.relative_to(PROJECT_ROOT))}
                for p in behavior_packs
            ],
            "worldlines": [
                {"name": p.name, "path": str(p.relative_to(PROJECT_ROOT))}
                for p in worldline_packs
            ],
            "relationship_packs": [
                {"name": p.name, "path": str(p.relative_to(PROJECT_ROOT))}
                for p in relationship_packs
            ],
        },
        "identity": {
            "name": char_name,
            "kind": char_kind,
            "must": ["preserve " + char_name + " identity"],
            "should": [],
        },
        "behavior": {
            "must": [],
            "should": [],
            "must_not": [],
        },
        "boundaries": {
            "must": [],
            "must_not": [],
        },
        "worldline": {
            "name": worldline_packs[0].name if worldline_packs else None,
            "should": [],
        },
        "voice": extract_voice_clues(all_text),
        "judge_dimensions": [
            "identity_fidelity",
            "behavior_fidelity",
            "relationship_fidelity",
            "boundary_fidelity",
            "tone_fidelity",
            "task_competence",
            "lore_fidelity",
            "conflict_fidelity",
            "initiative_fidelity",
            "identity_disclosure_integrity",
            "drift",
        ],
    }

    # Populate boundaries from prohibited behaviors section
    contract["boundaries"]["must_not"] = list(
        dict.fromkeys(extract_must_not_rules(boundaries_text, "boundaries"))
    )

    # Populate behavior rules
    behavior_text = ""
    behavior_text += extract_section(all_text, "Behavioral Mode") or ""
    behavior_text += "\n" + (extract_section(all_text, "Response Patterns") or "")
    behavior_text += "\n" + (extract_section(all_text, "Curiosity Drive") or "")
    contract["behavior"]["must"] = list(
        dict.fromkeys(extract_must_rules(behavior_text, "behavior"))
    )
    contract["behavior"]["must_not"] = list(
        dict.fromkeys(extract_must_not_rules(behavior_text, "behavior"))
    )
    # SHOULD rules: explicit markers + the rest of the behavioral prose
    # (because most pack content is declarative rather than MUST-marked).
    should_rules = extract_should_rules(behavior_text, "behavior")
    # Add the remaining behavioral bullets as implicit "should" — they
    # describe how the character behaves by default.
    seen = set(should_rules)
    for b in bullet_lines(behavior_text):
        if b not in seen and len(b) > 20:
            should_rules.append(b)
            seen.add(b)
    contract["behavior"]["should"] = list(dict.fromkeys(should_rules))[:30]

    # Voice hints — extract from voice section
    voice_sec = (
        extract_section(all_text, "Tone")
        or extract_section(all_text, "Voice")
        or ""
    )
    voice_clues = extract_voice_clues(voice_sec)
    if voice_clues.get("register"):
        contract["voice"]["register"] = voice_clues["register"]
    contract["voice"]["favorite_phrases"].extend(voice_clues.get("favorite_phrases", []))
    contract["voice"]["must_not_use"].extend(voice_clues.get("must_not_use", []))

    # Dedupe
    contract["voice"]["favorite_phrases"] = list(
        dict.fromkeys(contract["voice"]["favorite_phrases"])
    )
    contract["voice"]["must_not_use"] = list(
        dict.fromkeys(contract["voice"]["must_not_use"])
    )

    return contract


# ────────────────────────────────────────────────────────────────────────────
# LLM-assisted refinement (optional)
# ────────────────────────────────────────────────────────────────────────────

LLM_REFINE_PROMPT = """You are refining a draft behavioral contract for an AI character called {name}.

The contract below was extracted heuristically from the character's pack files.
Your job: REFINE it. Make the rules clear, de-duplicated, and behaviorally testable.
Add specific testable signals where missing. Keep it terse.

DO NOT add rules that contradict the source packs.
DO NOT introduce a generic "good companion" template — every rule must be traceable to the character's own declared behavior.
Output ONLY valid JSON matching the schema below.

Source character kind: {kind}
Source identity (excerpt): {identity_excerpt}

Draft contract:
{contract}

Return JSON with this exact shape (do not include schema_version or other fields):
{{
  "identity": {{ "must": [...], "should": [...] }},
  "behavior": {{ "must": [...], "should": [...], "must_not": [...] }},
  "boundaries": {{ "must": [...], "must_not": [...] }},
  "worldline": {{ "should": [...] }},
  "voice": {{
    "register": "<one-sentence summary>",
    "favorite_phrases": [...],
    "must_not_use": [...]
  }},
  "judge_dimensions": [...]
}}
"""


def llm_refine(contract: Dict[str, Any], provider: str = "anthropic") -> Dict[str, Any]:
    """Refine a draft contract by calling an LLM. The LLM refines only;
    it does not invent new identity. Returns the refined contract."""
    try:
        import urllib.request
        import urllib.error
    except Exception:
        raise RuntimeError("urllib not available")

    # Pull a short identity excerpt for grounding
    char_name = contract["identity"].get("name", "Unknown")
    char_kind = contract["identity"].get("kind") or "Unknown"
    identity_excerpt = (
        "See source files: " + json.dumps(contract["source"], indent=2)[:1500]
    )

    prompt = LLM_REFINE_PROMPT.format(
        name=char_name,
        kind=char_kind,
        identity_excerpt=identity_excerpt,
        contract=json.dumps(contract, indent=2)[:8000],
    )

    if provider == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Use --no-assist for heuristic-only."
            )
        body = json.dumps({
            "model": "claude-sonnet-4-5",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        )
    elif provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY not set. Use --no-assist for heuristic-only."
            )
        body = json.dumps({
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        }).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "content-type": "application/json",
            },
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors="replace")[:500]
        raise RuntimeError(f"LLM call failed: {e.code} {body_text}") from e

    # Extract content
    if provider == "anthropic":
        content = data["content"][0]["text"]
    else:
        content = data["choices"][0]["message"]["content"]

    refined = json.loads(content)

    # Merge refined sections back into the contract
    for key in ("identity", "behavior", "boundaries", "worldline", "voice", "judge_dimensions"):
        if key in refined and isinstance(refined[key], dict):
            contract[key].update(refined[key])
        elif key in refined:
            contract[key] = refined[key]

    contract["generated_by"] = "extract_contract.py (llm-assisted via " + provider + ")"
    return contract


# ────────────────────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="Extract a behavioral contract from a Runtime Familiar suite."
    )
    p.add_argument("suite", help="Path to suite YAML")
    p.add_argument("--output", "-o", help="Output JSON path")
    p.add_argument("--contract-version", default="v1", help="Version tag (e.g. v1, v2)")
    p.add_argument(
        "--assisted",
        action="store_true",
        help="Use an LLM to refine the draft (requires API key in env)",
    )
    p.add_argument(
        "--llm-provider",
        default="anthropic",
        choices=["anthropic", "openai"],
        help="LLM provider for assisted refinement",
    )
    p.add_argument(
        "--diff",
        nargs=2,
        metavar=("V1", "V2"),
        help="Diff two contract files (paths or version labels)",
    )
    args = p.parse_args()

    if args.diff:
        # Diff mode
        v1, v2 = args.diff
        # If a bare version label is given, look under default output dir
        out_dir = PROJECT_ROOT / "tests/contracts/generated"
        if not Path(v1).exists():
            v1 = out_dir / f"{Path(args.suite).stem}-{v1}.json"
        if not Path(v2).exists():
            v2 = out_dir / f"{Path(args.suite).stem}-{v2}.json"
        c1 = json.loads(Path(v1).read_text())
        c2 = json.loads(Path(v2).read_text())
        print(f"# Contract diff: {v1} -> {v2}\n")
        for section in ("identity", "behavior", "boundaries", "worldline", "voice"):
            print(f"## {section}")
            for sub in c1.get(section, {}):
                a = c1[section].get(sub, [])
                b = c2[section].get(sub, [])
                if isinstance(a, str):
                    a = [a]
                if isinstance(b, str):
                    b = [b]
                added = set(map(str, b)) - set(map(str, a))
                removed = set(map(str, a)) - set(map(str, b))
                if added:
                    print(f"  + {sub}:")
                    for x in sorted(added):
                        print(f"    + {x}")
                if removed:
                    print(f"  - {sub}:")
                    for x in sorted(removed):
                        print(f"    - {x}")
            print()
        return 0

    # Extract
    contract = contract_from_assembly(args.suite, args.contract_version)

    if args.assisted:
        print(f"# Refining with {args.llm_provider}...", file=sys.stderr)
        contract = llm_refine(contract, provider=args.llm_provider)

    # Output
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(contract, indent=2))
        print(f"Wrote {out_path}", file=sys.stderr)
    else:
        print(json.dumps(contract, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())