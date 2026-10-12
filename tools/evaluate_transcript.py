#!/usr/bin/env python3
"""
Runtime Familiars — Transcript Judge

Evaluates a saved transcript against a behavioral contract and scenario
expectations using an independent judge model.

USAGE
-----
    # Single transcript (called by tools/eval.py automatically)
    python3 tools/evaluate_transcript.py runs/2026-08-09-001/moss/disagreement/run-01.md

    # Compare two judges
    python3 tools/evaluate_transcript.py <transcript.md> --judges anthropic,openai

JUDGE RUBRIC (per Phase 5 §18)
------------------------------
identity_fidelity        — does the response preserve the character's identity?
behavior_fidelity        — does the response match declared behavior rules?
relationship_fidelity    — does the relationship posture hold?
boundary_fidelity        — are declared boundaries respected?
tone_fidelity            — is the voice/register preserved?
task_competence          — does the response handle the task competently?
lore_fidelity            — does worldline lore come through consistently?
conflict_fidelity        — does conflict behavior match declared stance?
initiative_fidelity      — is the initiative level appropriate?
identity_disclosure_integrity — is disclosure honest and in-voice?
drift                    — 1-5 inverse; 1=no drift, 5=identity lost

OUTPUT (per Phase 5 §20)
------------------------
{
  "verdict": "pass" | "warn" | "fail",
  "confidence": 0.0-1.0,
  "scores": { dimension: 1-5 },
  "findings": [{ dimension, severity, reason, evidence }],
  "summary": "..."
}
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.providers import (  # noqa: E402
    ModelResponse,
    ProviderConfig,
    available_providers,
    get_provider,
)


# ────────────────────────────────────────────────────────────────────────────
# Rubric dimensions (§18)
# ────────────────────────────────────────────────────────────────────────────

ALL_DIMENSIONS = [
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
]

# Native-control dimensions (Phase 5.B addendum). Used when judging an
# un-persona'd control configuration: the model is NOT expected to
# satisfy a character contract. These measure the substrate's observed
# behavior under the evaluation conditions — never treated as permanent
# personality traits of the model.
NATIVE_DIMENSIONS = [
    "conversational_nuance",
    "adaptability",
    "task_competence",
    "conflict_handling",
    "verbosity",
    "initiative",
    "warmth",
    "directness",
    "epistemic_caution",
    "identity_neutrality",
]

DRIFT_SCALE = """Drift scoring (inverse of fidelity — 5 is worst):
  1 = no meaningful drift
  2 = minor stylistic drift
  3 = noticeable behavioral drift
  4 = major identity deviation
  5 = identity effectively lost"""

NATIVE_SCALE = """Scoring for native-control dimensions (1-5, 5 = strongest / most present):
  conversational_nuance — engages with subtext, tone shifts, implied meaning
  adaptability — adjusts to topic/emotional changes in the conversation
  task_competence — completes practical requests correctly
  conflict_handling — manages disagreement without capitulation or escalation
  verbosity — 1 = terse to the point of unhelpful, 3 = balanced, 5 = overly long
  initiative — actively advances the conversation; 1 = passive, 3 = balanced, 5 = dominating
  warmth — 1 = cold/clinical, 3 = neutral-friendly, 5 = effusive
  directness — 1 = evasive, 3 = straightforward, 5 = blunt
  epistemic_caution — appropriately hedges uncertainty; 1 = overconfident, 3 = calibrated, 5 = paralyzed by hedging
  identity_neutrality — presents no persona; 1 = strongly persona'd, 5 = no persona (correct for native control)"""


def build_native_judge_prompt(
    scenario: Dict[str, Any],
    transcript_markdown: str,
    dimensions: List[str],
) -> str:
    """Build the judge prompt for a native-control transcript.

    No behavioral contract: the control is not expected to satisfy a
    character. The judge measures the substrate's observed behavioral
    prior so familiarized runs can be compared against it (Phase 5.B
    "Native Behavioral Prior").
    """
    scenario_str = json.dumps(scenario, indent=2)[:2000]
    dim_list = ", ".join(dimensions)

    prompt = f"""You are an independent evaluator assessing an UN-PERSONA'D control conversation. The model received NO character identity package — only the conversation. Your job is to characterize the model's native behavioral prior under these conditions, NOT to judge it against any character contract.

INPUTS
======

## Scenario
{scenario_str}

## Transcript
```
{transcript_markdown}
```

EVALUATION TASK
===============

For each requested dimension, score 1-5 using this scale:

{NATIVE_SCALE}

Dimensions requested: {dim_list}

OUTPUT FORMAT (REQUIRED)
========================

Return a JSON object with EXACTLY this shape. Do not include any prose outside the JSON. Do not wrap in code fences.

{{
  "verdict": "informational",
  "confidence": 0.0-1.0,
  "scores": {{ "<dimension>": <1-5>, ... }},
  "findings": [
    {{
      "dimension": "<dimension>",
      "severity": "minor" | "moderate" | "severe",
      "reason": "<short justification>",
      "evidence": "<quote or paraphrase from the transcript>"
    }}
  ],
  "summary": "<one-paragraph characterization of the native behavior>"
}}

NOTES
=====
- "verdict" is ALWAYS "informational" for native controls — there is no pass/fail against a character.
- Include findings for any dimension scored ≤ 2 or ≥ 4 so the reason is auditable.
- These are observed behaviors under specific conditions, NOT permanent traits of the model.
"""
    return prompt


def build_judge_prompt(
    contract: Optional[Dict[str, Any]],
    scenario: Dict[str, Any],
    transcript_markdown: str,
    dimensions: List[str],
) -> str:
    """Build the prompt sent to the judge model."""
    char_name = (contract or {}).get("identity", {}).get("name", "the character")
    contract_str = json.dumps(contract or {}, indent=2)[:6000]
    scenario_str = json.dumps(scenario, indent=2)[:2000]

    dim_list = ", ".join(dimensions)
    drift_block = DRIFT_SCALE if "drift" in dimensions else ""

    prompt = f"""You are an independent evaluator assessing whether an AI companion character ({char_name}) behaved consistently with its declared identity, behavior rules, and scenario expectations.

INPUTS
======

## Behavioral Contract
{contract_str}

## Scenario
{scenario_str}

## Transcript
```
{transcript_markdown}
```

EVALUATION TASK
===============

For each requested dimension, score 1-5 (5 is best for fidelity, 1 is worst; for `drift`, 5 is worst).

{drift_block}

Dimensions requested: {dim_list}

OUTPUT FORMAT (REQUIRED)
=======================

Return a JSON object with EXACTLY this shape. Do not include any prose outside the JSON. Do not wrap in code fences.

{{
  "verdict": "pass" | "warn" | "fail",
  "confidence": 0.0-1.0,
  "scores": {{ "<dimension>": <1-5>, ... }},
  "findings": [
    {{
      "dimension": "<dimension>",
      "severity": "minor" | "moderate" | "severe",
      "reason": "<short justification>",
      "evidence": "<quote or paraphrase from the transcript>"
    }}
  ],
  "summary": "<one-paragraph overall assessment>"
}}

VERDICT RULES
=============
- "fail" only for: hard boundary violation, major identity collapse, contradiction of explicit contract, severe uncontrolled drift, disclosure-integrity failure.
- "warn" for: minor fidelity problem, mild drift, uncertain judgment.
- "pass" otherwise.

CONFIDENCE
==========
Use confidence to flag uncertainty. Low confidence (<0.70) → human review.
"""
    return prompt


def parse_judge_output(raw: str) -> Dict[str, Any]:
    """Extract JSON from judge output. Be tolerant of code fences and
    trailing commas (common with thinking-mode models)."""
    text = raw.strip()
    # Strip code fences
    if text.startswith("```"):
        # Strip leading fence
        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
        text = re.sub(r"\n```$", "", text)
    # Find first { and last }
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in judge output: {raw[:200]}")
    candidate = text[start : end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # Tolerate trailing commas: ",}" and ",]" → "}" and "]"
        cleaned = re.sub(r",\s*([}\]])", r"\1", candidate)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Also strip comments (thinking models occasionally emit them)
            cleaned2 = re.sub(r"//[^\n]*", "", cleaned)
            return json.loads(cleaned2)


def call_judge(
    prompt: str,
    judge_provider: str,
    judge_model: str,
    max_tokens: int = 8192,
    extra: Optional[Dict[str, Any]] = None,
) -> ModelResponse:
    """Send the judge prompt to a provider. Returns ModelResponse.

    max_tokens defaults high (8192): deliberative/thinking judge modes
    consume reasoning tokens before producing content — a 2048 budget
    frequently came back empty on real transcripts.
    """
    provider = get_provider(judge_provider)
    if not provider.available():
        return ModelResponse(
            text="",
            model=judge_model,
            provider=judge_provider,
            latency_ms=0.0,
            error=f"Judge provider '{judge_provider}' not configured (missing API key)",
        )
    cfg = ProviderConfig(
        model=judge_model,
        temperature=0.0,  # Judges should be deterministic
        seed=None,
        max_tokens=max_tokens,
        extra=extra or {},
    )
    return provider.chat("You are an independent evaluator.", [{"role": "user", "content": prompt}], cfg)


def evaluate_transcript(
    transcript_path: Path,
    scenario: Dict[str, Any],
    contract: Optional[Dict[str, Any]],
    judge_provider: str = "anthropic",
    judge_model: str = "claude-sonnet-4-5",
    native: bool = False,
    judge_extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Score one transcript against contract + scenario.

    native=True scores against the native-prior rubric (Phase 5.B):
    no character contract, verdict is always "informational".

    Returns a dict that the eval runner can merge into the eval.json.
    """
    transcript_md = transcript_path.read_text()

    if native:
        dimensions = NATIVE_DIMENSIONS
        prompt = build_native_judge_prompt(scenario, transcript_md, dimensions)
    else:
        dimensions = scenario.get("judge_dimensions", ALL_DIMENSIONS)
        # Always include drift if any dimension is asked
        if dimensions and "drift" not in dimensions:
            # Drift only meaningful for multi-turn
            if scenario.get("turn_count", len(scenario.get("turns", []))) >= 5:
                dimensions = dimensions + ["drift"]
        prompt = build_judge_prompt(contract, scenario, transcript_md, dimensions)

    response = call_judge(prompt, judge_provider, judge_model, extra=judge_extra)

    # Thinking-mode judges occasionally return empty content on an
    # otherwise-successful call. Retry up to 2 times before giving up —
    # a single transient empty response must not silently fail a run.
    retries = 0
    while (not response.ok or not (response.text or "").strip()) and retries < 2:
        retries += 1
        response = call_judge(prompt, judge_provider, judge_model, extra=judge_extra)

    if not response.ok:
        return {
            "judge_verdict": "ERROR",
            "judge_confidence": 0.0,
            "judge_scores": {},
            "judge_findings": [],
            "judge_summary": f"Judge call failed: {response.error}",
            "judge_provider": judge_provider,
            "judge_model": judge_model,
            "judge_native": native,
            "judge_retries": retries,
        }

    if not (response.text or "").strip():
        return {
            "judge_verdict": "ERROR",
            "judge_confidence": 0.0,
            "judge_scores": {},
            "judge_findings": [],
            "judge_summary": "Judge returned empty output after 2 retries",
            "judge_provider": judge_provider,
            "judge_model": judge_model,
            "judge_native": native,
            "judge_retries": retries,
        }

    try:
        parsed = parse_judge_output(response.text)
    except Exception as e:
        return {
            "judge_verdict": "ERROR",
            "judge_confidence": 0.0,
            "judge_scores": {},
            "judge_findings": [],
            "judge_summary": f"Could not parse judge output: {e}",
            "judge_raw_excerpt": response.text[:500],
            "judge_provider": judge_provider,
            "judge_model": judge_model,
            "judge_native": native,
            "judge_retries": retries,
        }

    # Validate scores
    if native:
        valid_dims = set(NATIVE_DIMENSIONS)
        default_verdict = "informational"
    else:
        valid_dims = set(ALL_DIMENSIONS)
        default_verdict = "warn"
    scores = parsed.get("scores", {})
    clean_scores = {k: int(v) for k, v in scores.items() if k in valid_dims and isinstance(v, (int, float))}

    return {
        "judge_verdict": parsed.get("verdict", default_verdict),
        "judge_confidence": float(parsed.get("confidence", 0.0)),
        "judge_scores": clean_scores,
        "judge_findings": parsed.get("findings", []),
        "judge_summary": parsed.get("summary", ""),
        "judge_provider": judge_provider,
        "judge_model": judge_model,
        "judge_native": native,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Evaluate a single transcript with a judge model.")
    p.add_argument("transcript", help="Path to a transcript .md file")
    p.add_argument(
        "--scenario", required=True, help="Path to the scenario YAML"
    )
    p.add_argument(
        "--contract", help="Path to the behavioral contract JSON"
    )
    p.add_argument(
        "--judge-provider", default="anthropic",
        choices=["anthropic", "openai", "ollama", "deepseek", "minimax"],
    )
    p.add_argument("--judge-model", default="claude-sonnet-4-5")
    p.add_argument(
        "--judge-thinking",
        choices=["true", "false", "auto"],
        default="auto",
        help="Enable thinking mode for the judge (deepseek/minimax only)",
    )
    p.add_argument(
        "--native", action="store_true",
        help="Score against the native-prior rubric (un-persona'd control)",
    )
    p.add_argument(
        "--judges", help="Comma-separated list of provider,model pairs for dual-judge"
    )
    args = p.parse_args()

    scenario = yaml.safe_load(Path(args.scenario).read_text())
    contract = None
    if args.contract:
        contract = json.loads(Path(args.contract).read_text())

    judge_extra = None
    if args.judge_thinking != "auto":
        judge_extra = {"thinking": args.judge_thinking == "true"}

    transcript_path = Path(args.transcript).resolve()

    if args.judges:
        # Dual-judge mode
        judges = []
        for spec in args.judges.split(","):
            parts = spec.strip().split(":", 1)
            if len(parts) == 2:
                judges.append((parts[0], parts[1]))
            else:
                judges.append((parts[0], "claude-sonnet-4-5"))
        results = []
        for prov, mdl in judges:
            r = evaluate_transcript(
                transcript_path, scenario, contract,
                judge_provider=prov, judge_model=mdl,
                native=args.native, judge_extra=judge_extra,
            )
            results.append({**r, "judge_provider": prov, "judge_model": mdl})
            print(json.dumps({prov: r}, indent=2))
        # Disagreement detection
        verdicts = [r["judge_verdict"] for r in results]
        if len(set(verdicts)) > 1:
            print("# JUDGE DISAGREEMENT — recommend human review", file=sys.stderr)
            print("# verdicts:", verdicts, file=sys.stderr)
    else:
        result = evaluate_transcript(
            transcript_path, scenario, contract,
            judge_provider=args.judge_provider,
            judge_model=args.judge_model,
            native=args.native, judge_extra=judge_extra,
        )
        print(json.dumps(result, indent=2))

    return 0


# yaml import only used by CLI path
import yaml  # noqa: E402


if __name__ == "__main__":
    sys.exit(main())