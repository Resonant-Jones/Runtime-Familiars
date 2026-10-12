#!/usr/bin/env python3
"""
Runtime Familiars — Semantic Retention Check (§38)

Pre-inference check: takes the source pack components and the resolved
prompt, and asks an independent model to evaluate whether important
behavioral requirements were lost during assembly.

USAGE
-----
    python3 tools/check_retention.py tests/suites/moss-gentle.yaml
    python3 tools/check_retention.py tests/suites/moss-gentle.yaml --no-llm  # heuristic only

OUTPUT
------
{
  "retention": "pass" | "warn" | "fail",
  "missing_requirements": ["..."],
  "weakened_requirements": ["..."],
  "notes": "..."
}

This helps distinguish ASSEMBLY failures (lost or diluted during
composition) from MODEL failures (resolved prompt is correct but the
model didn't follow it). See §39 diagnostic failure classification.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import yaml

from tools.assemble import assemble  # noqa: E402
from tools.providers import (  # noqa: E402
    ModelResponse,
    ProviderConfig,
    available_providers,
    get_provider,
)


def get_source_requirements(suite: Dict[str, Any]) -> List[str]:
    """Pull MUST/SHOULD/MUST NOT rules from the source packs."""
    reqs: List[str] = []
    character_dir = PROJECT_ROOT / suite["character"]
    composition = suite.get("composition", {})

    pack_dirs = [character_dir]
    for p in composition.get("behavior", []) or []:
        pack_dirs.append(PROJECT_ROOT / p)
    for p in composition.get("relationship", []) or []:
        pack_dirs.append(PROJECT_ROOT / p)
    for p in composition.get("worldline", []) or []:
        pack_dirs.append(PROJECT_ROOT / p)

    for d in pack_dirs:
        for md in d.glob("*.md"):
            try:
                content = md.read_text()
            except Exception:
                continue
            # Strip frontmatter
            if content.startswith("---"):
                end = content.find("\n---", 3)
                if end != -1:
                    content = content[end + 4:]
            # Pull lines that look like MUST/MUST NOT/SHOULD rules
            for line in content.splitlines():
                line = line.strip()
                for prefix in ("1. ", "2. ", "3. ", "4. ", "5. ", "- ", "* "):
                    if line.startswith(prefix):
                        line = line[len(prefix):]
                        break
                # Drop very long lines and headers
                if len(line) > 200 or len(line) < 20:
                    continue
                if any(m in line.upper() for m in ("MUST NEVER", "MUST NOT", "MUST", "NEVER", "SHALL NOT")):
                    reqs.append(line)

    return reqs


def build_retention_prompt(
    source_reqs: List[str], resolved_prompt: str
) -> str:
    """Build the prompt asking the model whether requirements survived."""
    reqs_str = "\n".join(f"- {r}" for r in source_reqs[:50])
    return f"""You are auditing whether a runtime prompt correctly retains the behavioral requirements from its source packs.

SOURCE REQUIREMENTS (from pack components)
==========================================
{reqs_str}

RESOLVED PROMPT (what will actually be sent to the model)
=========================================================
{resolved_prompt[:12000]}

TASK
====
Identify any source requirements that are MISSING (not represented in any form in the resolved prompt) or WEAKENED (present but with weaker language than the source).

OUTPUT (JSON only, no prose outside the JSON)
{{
  "retention": "pass" | "warn" | "fail",
  "missing_requirements": [<exact source requirement text>],
  "weakened_requirements": [
    {{"source": <source text>, "weakened_to": <explanation>}}
  ],
  "notes": "<one-paragraph summary>"
}}

Rules of thumb:
- A requirement is "missing" only if it has NO representation in the resolved prompt at all (no paraphrase, no equivalent).
- A requirement is "weakened" if it appears but its imperative force is reduced (e.g., MUST becomes should).
- "fail" only for multiple missing hard constraints or systematic weakening.
- "warn" for 1-2 weakened or partial losses.
- "pass" if everything is preserved.
"""


def call_retention_judge(
    prompt: str, provider: str, model: str
) -> ModelResponse:
    p = get_provider(provider)
    if not p.available():
        return ModelResponse(
            text="", model=model, provider=provider,
            latency_ms=0.0, error=f"{provider} not configured",
        )
    cfg = ProviderConfig(model=model, temperature=0.0, seed=None, max_tokens=2048)
    return p.chat("You are an independent auditor.", [{"role": "user", "content": prompt}], cfg)


def heuristic_retention(
    source_reqs: List[str], resolved_prompt: str
) -> Dict[str, Any]:
    """Token-overlap heuristic for retention — fast, no API call."""
    low_prompt = resolved_prompt.lower()
    missing: List[str] = []
    present: List[str] = []
    for r in source_reqs:
        # Take a few distinctive words from the requirement
        words = [w for w in r.lower().split() if len(w) > 5][:5]
        if not words:
            continue
        # If at least 2 distinctive words appear in the prompt, count as present
        hits = sum(1 for w in words if w in low_prompt)
        if hits >= max(2, len(words) // 2):
            present.append(r)
        else:
            missing.append(r)

    if len(missing) > len(source_reqs) * 0.2:
        verdict = "fail"
    elif missing:
        verdict = "warn"
    else:
        verdict = "pass"

    return {
        "retention": verdict,
        "missing_requirements": missing,
        "weakened_requirements": [],
        "notes": f"Heuristic check: {len(present)}/{len(source_reqs)} source requirements represented by distinctive keywords in the resolved prompt.",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Check semantic retention of source requirements.")
    p.add_argument("suite", help="Path to suite YAML")
    p.add_argument(
        "--no-llm", action="store_true",
        help="Skip the LLM judge; use heuristic-only retention check",
    )
    p.add_argument("--provider", default="anthropic", choices=["anthropic", "openai", "ollama"])
    p.add_argument("--model", default="claude-sonnet-4-5")
    args = p.parse_args()

    with open(args.suite) as f:
        suite = yaml.safe_load(f)
    suite_id = suite.get("id", Path(args.suite).stem)

    assembly = assemble_for_suite(suite)
    source_reqs = get_source_requirements(suite)

    if args.no_llm:
        result = heuristic_retention(source_reqs, assembly.assembled_prompt)
    else:
        if not available_providers():
            print("warn: no providers configured, falling back to heuristic check", file=sys.stderr)
            result = heuristic_retention(source_reqs, assembly.assembled_prompt)
        else:
            prompt = build_retention_prompt(source_reqs, assembly.assembled_prompt)
            resp = call_retention_judge(prompt, args.provider, args.model)
            if not resp.ok:
                print(f"warn: judge call failed: {resp.error}", file=sys.stderr)
                print("falling back to heuristic check", file=sys.stderr)
                result = heuristic_retention(source_reqs, assembly.assembled_prompt)
            else:
                try:
                    # Parse JSON from response
                    import re
                    text = resp.text.strip()
                    if text.startswith("```"):
                        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
                        text = re.sub(r"\n```$", "", text)
                    start = text.find("{")
                    end = text.rfind("}")
                    if start == -1 or end == -1:
                        raise ValueError("no JSON in response")
                    result = json.loads(text[start:end + 1])
                except Exception as e:
                    print(f"warn: could not parse judge output: {e}", file=sys.stderr)
                    result = heuristic_retention(source_reqs, assembly.assembled_prompt)

    result["source_suite"] = suite_id
    result["source_requirement_count"] = len(source_reqs)
    print(json.dumps(result, indent=2))
    return 0 if result["retention"] == "pass" else (2 if result["retention"] == "fail" else 1)


def assemble_for_suite(suite: Dict[str, Any]) -> Any:
    character_path = PROJECT_ROOT / suite["character"]
    composition = suite.get("composition", {})
    behavior_packs = composition.get("behavior", []) or []
    relationship_packs = composition.get("relationship", []) or []
    worldline_packs = composition.get("worldline", []) or []

    # The existing assembler accepts one of each pack type; use the first.
    return assemble(
        str(character_path),
        behavior_pack_path=str(PROJECT_ROOT / behavior_packs[0]) if behavior_packs else None,
        relationship_pack_path=str(PROJECT_ROOT / relationship_packs[0]) if relationship_packs else None,
        worldline_pack_path=str(PROJECT_ROOT / worldline_packs[0]) if worldline_packs else None,
    )


if __name__ == "__main__":
    sys.exit(main())