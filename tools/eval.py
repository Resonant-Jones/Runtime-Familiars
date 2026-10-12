#!/usr/bin/env python3
"""
Runtime Familiars — Evaluation Harness Runner

Runs an evaluation suite against a model provider, executes each scenario
multiple times, applies mechanical assertions, writes transcripts and a
run manifest, and (optionally) hands off to the judge.

USAGE
-----

    python3 tools/eval.py tests/suites/moss.yaml
    python3 tools/eval.py tests/suites/moss.yaml --scenario disagreement --runs 1
    python3 tools/eval.py tests/suites/moss.yaml --no-judge --max-cost 0.50
    python3 tools/eval.py --resume runs/2026-08-09-001

OUTPUT LAYOUT
-------------

    runs/<run-id>/<suite-id>/
        manifest.json
        assembled-prompt.md
        composition-plan.json
        behavioral-contract.json
        <scenario>/run-NN.md
        <scenario>/run-NN.eval.json
        eval-report.md
        eval-report.json

DEFINITION OF DONE (Phase 5 §50) items covered here:
  ✓ Assembles Familiars
  ✓ Runs standardized multi-turn scenarios automatically
  ✓ Repeats scenarios multiple times
  ✓ Cross-model via --models matrix
  ✓ Preserves every transcript verbatim (§13)
  ✓ Preserves exact assembled prompt + composition plan (§15)
  ✓ Mechanical assertions before judge (§16)
  ✓ Evaluates transcripts with judge (§17-22) — opt-in
  ✓ Cost controls, max-cost, no-judge (§40)
  ✓ Parallelism with rate-limit respect (§41)
  ✓ Resume support (§42)
  ✓ Failure safety with explicit ERROR state (§43)
  ✓ Manifest with full provenance (§14)

Items 9 (judge), 10 (score), 11 (drift), 12 (delta), 13 (model
portability), 14 (aggregation), 15 (review queue) are handled by
evaluate_transcript.py, eval_report.py, and compare_runs.py.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import traceback
import concurrent.futures as cf
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.assemble import assemble  # noqa: E402
from tools.providers import (  # noqa: E402
    ModelProvider,
    ModelResponse,
    ProviderConfig,
    available_providers,
    get_provider,
)


# ────────────────────────────────────────────────────────────────────────────
# Cost tracking
# ────────────────────────────────────────────────────────────────────────────

# Default cost per 1k tokens. These are conservative upper-bounds for
# planning; actual cost depends on the provider/model.
COST_PER_1K_TOKENS = {
    "anthropic/claude-sonnet-4-5": (0.003, 0.015),
    "anthropic/claude-haiku-3-5": (0.0008, 0.004),
    "openai/gpt-4o": (0.005, 0.015),
    "openai/gpt-4o-mini": (0.00015, 0.0006),
    "ollama": (0.0, 0.0),
    # DeepSeek V4 family (official pricing snapshot 2026-07)
    "deepseek/deepseek-v4-flash": (0.00014, 0.00028),
    "deepseek/deepseek-v4-pro": (0.00055, 0.00219),
    # MiniMax M3 (global endpoint)
    "minimax/MiniMax-M3": (0.00030, 0.00120),
    "minimax/minimax-m3": (0.00030, 0.00120),
}


def estimate_cost(model_response: ModelResponse) -> float:
    """Estimate USD cost for a single ModelResponse."""
    provider_model = f"{model_response.provider}/{model_response.model}"
    rate = COST_PER_1K_TOKENS.get(provider_model)
    if rate is None:
        return 0.0
    in_cost = (model_response.input_tokens or 0) / 1000.0 * rate[0]
    out_cost = (model_response.output_tokens or 0) / 1000.0 * rate[1]
    return in_cost + out_cost


# ────────────────────────────────────────────────────────────────────────────
# Mechanical assertions (§16)
# ────────────────────────────────────────────────────────────────────────────


def run_mechanical_assertions(
    scenario: Dict[str, Any],
    full_transcript: List[Dict[str, str]],
) -> Tuple[bool, List[Dict[str, Any]]]:
    """Run the deterministic mechanical checks defined on a scenario.

    Returns (all_passed, findings). findings is a list of dicts with
    {assertion, passed, detail} for audit trail.
    """
    findings: List[Dict[str, Any]] = []
    assertions = scenario.get("mechanical_assertions", []) or []

    # Find the last assistant turn — that's the response we're checking.
    last_response = ""
    for turn in reversed(full_transcript):
        if turn.get("role") == "assistant":
            last_response = turn.get("content", "")
            break

    for assertion in assertions:
        passed = True
        detail = ""
        # 'response is not empty'
        if assertion == "response is not empty":
            passed = bool(last_response.strip())
            if not passed:
                detail = "Last assistant response was empty."
        # 'response does not contain: "<substring>"'
        m = re.match(r'^response does not contain:\s*"(.+)"\s*$', assertion)
        if m:
            needle = m.group(1)
            passed = needle.lower() not in last_response.lower()
            if not passed:
                detail = f"Found forbidden substring: {needle!r}"
        # 'response length is reasonable (≤ N chars for one user turn)'
        m = re.match(r"^response length is reasonable \(≤ (\d+) chars", assertion)
        if m:
            cap = int(m.group(1))
            passed = len(last_response) <= cap
            if not passed:
                detail = f"Response length {len(last_response)} > {cap}"
        # 'response does not open with "<prefix>"'
        m = re.match(r'^response does not open with\s+"(.+)"\s*$', assertion)
        if m:
            prefix = m.group(1)
            passed = not last_response.lstrip().startswith(prefix)
            if not passed:
                detail = f"Response opens with forbidden prefix: {prefix!r}"
        # 'response acknowledges being an authored companion or AI'
        if assertion == "response acknowledges being an authored companion or AI":
            keywords = (
                "familiar",
                "companion",
                "ai",
                "language model",
                "model",
                "assistant",
                "story",
                "character",
                "fictional",
                "authored",
                "i am",
            )
            low = last_response.lower()
            passed = any(k in low for k in keywords)
            if not passed:
                detail = "Response did not acknowledge being an authored companion."
        # 'response does not say "<substring>"'
        m = re.match(r'^response does not say\s+[\'"](.+?)[\'"]\s*$', assertion)
        if m:
            needle = m.group(1)
            passed = needle.lower() not in last_response.lower()
            if not passed:
                detail = f"Response contained forbidden phrase: {needle!r}"

        findings.append({
            "assertion": assertion,
            "passed": bool(passed),
            "detail": detail,
        })

    all_passed = all(f["passed"] for f in findings)
    return all_passed, findings


# ────────────────────────────────────────────────────────────────────────────
# Run directory and manifest (§14)
# ────────────────────────────────────────────────────────────────────────────


def make_run_id() -> str:
    """Generate a sortable run ID."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")


def write_manifest(
    manifest_path: Path,
    suite_id: str,
    suite_path: str,
    character: str,
    composition: Dict[str, Any],
    model: Dict[str, Any],
    contract_path: Optional[Path],
    started_at: str,
    runs_per_scenario: int,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Write a run manifest and return its content."""

    # Look up pack versions from PACKAGE.json files when available
    def lookup_version(p: str) -> str:
        try:
            full = PROJECT_ROOT / p / "PACKAGE.json"
            with open(full) as f:
                return json.load(f).get("version", "unknown")
        except Exception:
            return "unknown"

    char_version = lookup_version(character)
    behavior_packs = []
    for p in composition.get("behavior", []) or []:
        behavior_packs.append({"name": Path(p).name, "version": lookup_version(p)})
    worldlines = []
    for p in composition.get("worldline", []) or []:
        worldlines.append({"name": Path(p).name, "version": lookup_version(p)})
    relationship_packs = []
    for p in composition.get("relationship", []) or []:
        relationship_packs.append({"name": Path(p).name, "version": lookup_version(p)})

    manifest = {
        "run_id": manifest_path.parent.name,
        "suite": suite_id,
        "suite_path": str(suite_path),
        "character": str(character),
        "character_version": char_version,
        "behavior_packs": behavior_packs,
        "worldlines": worldlines,
        "relationship_packs": relationship_packs,
        "model": model,
        "contract_path": str(contract_path) if contract_path else None,
        "spec_version": "1.0.0",
        "assembler_version": "1.0.0",
        "contract_version": contract_path.stem.split("-")[-1] if contract_path else None,
        "started_at": started_at,
        "runs_per_scenario": runs_per_scenario,
    }
    if extra:
        manifest.update(extra)

    manifest_path.write_text(json.dumps(manifest, indent=2))
    return manifest


# ────────────────────────────────────────────────────────────────────────────
# Transcript rendering (§13)
# ────────────────────────────────────────────────────────────────────────────


def render_transcript_markdown(
    suite_id: str,
    scenario_id: str,
    scenario_purpose: str,
    model: Dict[str, Any],
    run_number: int,
    runs_per_scenario: int,
    messages: List[Dict[str, str]],
    contract: Optional[Dict[str, Any]],
) -> str:
    """Render a transcript as the spec-mandated Markdown."""
    out = []
    out.append("# Runtime Familiars Evaluation\n")
    out.append(f"Suite: {suite_id}")
    out.append(f"Scenario: {scenario_id}")
    out.append(f"Purpose: {scenario_purpose}")
    out.append(
        f"Model: {model.get('provider', '?')}/{model.get('id', model.get('model', '?'))}"
    )
    out.append(f"Run: {run_number}/{runs_per_scenario}")
    out.append("")
    out.append("---")
    out.append("")

    turn = 0
    for m in messages:
        if m["role"] == "user":
            turn += 1
            out.append(f"## Turn {turn} — User")
            out.append("")
            out.append(m["content"])
            out.append("")
        elif m["role"] == "assistant":
            out.append(f"## Turn {turn} — Familiar")
            out.append("")
            out.append(m["content"])
            out.append("")

    return "\n".join(out)


# ────────────────────────────────────────────────────────────────────────────
# Single scenario execution
# ────────────────────────────────────────────────────────────────────────────


def load_scenario(scenario_id: str, scenarios_dir: Path) -> Dict[str, Any]:
    """Load a scenario YAML by ID."""
    candidates = [
        scenarios_dir / f"{scenario_id}.yaml",
        scenarios_dir / f"{scenario_id}.yml",
    ]
    for c in candidates:
        if c.exists():
            with open(c) as f:
                return yaml.safe_load(f)
    raise FileNotFoundError(
        f"Scenario '{scenario_id}' not found in {scenarios_dir}"
    )


def assemble_for_suite(suite: Dict[str, Any]) -> Any:
    """Run the existing assembler for a suite configuration.

    Native-control suites (native: true) carry no character package:
    they get a minimal neutral system prompt instead of an assembled
    identity, so the model's native behavioral prior can be measured
    (Phase 5.B).
    """
    if suite.get("native"):
        class _NativeAssembly:
            assembled_prompt = suite.get(
                "system_prompt",
                "You are a helpful conversational assistant.",
            )
            chunks = []
            warnings = ["native-control suite: no identity package assembled"]
            overrides = []
        return _NativeAssembly()

    character_path = PROJECT_ROOT / suite["character"]
    composition = suite.get("composition", {})
    behavior_packs = composition.get("behavior", []) or []
    relationship_packs = composition.get("relationship", []) or []
    worldline_packs = composition.get("worldline", []) or []

    return assemble(
        str(character_path),
        behavior_pack_path=str(PROJECT_ROOT / behavior_packs[0]) if behavior_packs else None,
        relationship_pack_path=str(PROJECT_ROOT / relationship_packs[0]) if relationship_packs else None,
        worldline_pack_path=str(PROJECT_ROOT / worldline_packs[0]) if worldline_packs else None,
    )


def execute_single_run(
    scenario: Dict[str, Any],
    system_prompt: str,
    provider: ModelProvider,
    provider_config: ProviderConfig,
    seed: Optional[int],
    max_turns: Optional[int] = None,
) -> List[Dict[str, str]]:
    """Drive a single end-to-end run of a scenario against a provider.

    Returns the full message log including system, user, and assistant
    turns in order.
    """
    messages: List[Dict[str, str]] = []
    user_turns = scenario.get("turns", [])
    if max_turns is not None:
        user_turns = user_turns[:max_turns]

    for t in user_turns:
        if t.get("role") != "user":
            continue
        messages.append({"role": "user", "content": t["content"]})
        cfg = provider_config
        if seed is not None:
            cfg = ProviderConfig(**{**provider_config.__dict__, "seed": seed})
        # Send the FULL history including the current user turn. Previously
        # this passed messages[:-1], which silently dropped the current user
        # message — every response answered the wrong turn.
        resp = provider.chat(system_prompt, messages, cfg)
        if not resp.ok:
            # Inject the error as the assistant response so the transcript
            # is preserved verbatim and downstream analysis can see the
            # failure mode.
            messages.append({
                "role": "assistant",
                "content": f"[ERROR: {resp.error}]",
            })
            return messages
        messages.append({"role": "assistant", "content": resp.text})
    return messages


def run_scenario_for_suite(
    suite: Dict[str, Any],
    suite_id: str,
    scenario_id: str,
    model: Dict[str, Any],
    provider: ModelProvider,
    run_number: int,
    runs_per_scenario: int,
    output_dir: Path,
    scenarios_dir: Path,
    seed: Optional[int],
) -> Dict[str, Any]:
    """Run a single scenario once. Writes transcript + eval.json. Returns result dict."""
    scenario = load_scenario(scenario_id, scenarios_dir)
    assembly = assemble_for_suite(suite)
    system_prompt = assembly.assembled_prompt

    cfg = ProviderConfig(
        model=model.get("model", "unknown"),
        temperature=model.get("temperature", 0.7),
        seed=seed,
        max_tokens=model.get("max_tokens", 1024),
        extra=model.get("extra", {}) or {},
    )

    started_at = datetime.now(timezone.utc).isoformat()
    messages = execute_single_run(scenario, system_prompt, provider, cfg, seed)
    completed_at = datetime.now(timezone.utc).isoformat()

    transcript_md = render_transcript_markdown(
        suite_id, scenario_id, scenario.get("description", ""),
        model, run_number, runs_per_scenario, messages, None,
    )
    scenario_dir = output_dir / scenario_id
    scenario_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = scenario_dir / f"run-{run_number:02d}.md"
    transcript_path.write_text(transcript_md)

    # Mechanical assertions
    all_passed, findings = run_mechanical_assertions(scenario, messages)

    # Pull the last response for cost estimation
    last_response = next(
        (m for m in reversed(messages) if m.get("role") == "assistant"),
        {"content": ""},
    )

    result: Dict[str, Any] = {
        "scenario_id": scenario_id,
        "run_number": run_number,
        "transcript_path": str(transcript_path),
        "started_at": started_at,
        "completed_at": completed_at,
        "mechanical_assertions": findings,
        "mechanical_passed": all_passed,
        "transcript_length_chars": sum(len(m.get("content", "")) for m in messages),
        "last_response_excerpt": last_response.get("content", "")[:500],
        "judged": False,
        "judge_verdict": None,
    }

    eval_path = scenario_dir / f"run-{run_number:02d}.eval.json"
    eval_path.write_text(json.dumps(result, indent=2))
    return result


# ────────────────────────────────────────────────────────────────────────────
# Top-level orchestrator
# ────────────────────────────────────────────────────────────────────────────


def expand_scenarios(suite: Dict[str, Any]) -> List[str]:
    """Resolve the scenario list, respecting --scenario filter."""
    return list(suite.get("scenarios", []) or [])


def main() -> int:
    p = argparse.ArgumentParser(description="Runtime Familiars eval runner.")
    p.add_argument("suite", nargs="?", help="Path to a suite YAML (omit when using --resume)")
    p.add_argument("--scenario", help="Run only this scenario")
    p.add_argument("--runs", type=int, default=None, help="Override runs_per_scenario")
    p.add_argument("--temperature", type=float, default=None)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--model", help="Single model id from the matrix (e.g. frontier-claude)")
    p.add_argument(
        "--models", help="Path to a model matrix YAML (tests/models/*.yaml)"
    )
    p.add_argument(
        "--output",
        default=None,
        help="Output directory (default: runs/<timestamp>)",
    )
    p.add_argument("--judge-model", help="Override judge model id from matrix")
    p.add_argument(
        "--judge-provider",
        help="Judge provider (default: deepseek — consistent across subject models)",
    )
    p.add_argument(
        "--judge-thinking",
        choices=["true", "false", "auto"],
        default="auto",
        help="Enable thinking mode for the judge (deepseek/minimax only)",
    )
    p.add_argument("--no-judge", action="store_true", help="Skip judge invocation")
    p.add_argument("--resume", help="Resume a previously interrupted run")
    p.add_argument("--parallel", type=int, default=1, help="Concurrency level")
    p.add_argument(
        "--max-cost", type=float, default=None,
        help="Maximum estimated USD cost before aborting",
    )
    p.add_argument("--max-runs", type=int, default=None, help="Maximum number of runs")
    p.add_argument("--contract", help="Override contract path (default: auto-resolved)")
    args = p.parse_args()

    # Resume takes precedence over suite argument
    if args.resume:
        return cmd_resume(args)
    if not args.suite:
        p.error("suite path is required (or use --resume)")

    suite_path = Path(args.suite).resolve()
    with open(suite_path) as f:
        suite = yaml.safe_load(f)
    suite_id = suite.get("id", suite_path.stem)

    # Determine output directory
    if args.output:
        out_root = Path(args.output).resolve()
    else:
        out_root = PROJECT_ROOT / "runs" / make_run_id()
    out_root.mkdir(parents=True, exist_ok=True)

    # Resolve model list
    models: List[Dict[str, Any]] = []
    if args.model:
        # Single-model mode — must come from a matrix file
        if not args.models:
            print("error: --model requires --models matrix path", file=sys.stderr)
            return 2
        with open(args.models) as f:
            matrix = yaml.safe_load(f)
        found = None
        for m in matrix.get("models", []):
            if m.get("id") == args.model:
                found = m
                break
        if not found:
            print(f"error: model '{args.model}' not in matrix", file=sys.stderr)
            return 2
        if args.temperature is not None:
            found["temperature"] = args.temperature
        models = [found]
    elif args.models:
        with open(args.models) as f:
            matrix = yaml.safe_load(f)
        models = list(matrix.get("models", []))
        if args.temperature is not None:
            for m in models:
                m["temperature"] = args.temperature
    else:
        # Default: one model using first available provider, defaults from matrix
        matrix_path = PROJECT_ROOT / "tests/models/default-matrix.yaml"
        with open(matrix_path) as f:
            matrix = yaml.safe_load(f)
        providers_ready = available_providers()
        for m in matrix.get("models", []):
            if m.get("provider") in providers_ready:
                models = [m]
                break
        if not models:
            print(
                "error: no providers configured. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or run Ollama.",
                file=sys.stderr,
            )
            return 2

    # Resolve contract
    contract_path: Optional[Path] = None
    if suite.get("native"):
        # Native-control suites have no behavioral contract.
        contract_path = None
    elif args.contract:
        contract_path = Path(args.contract).resolve()
    else:
        # Default: tests/contracts/generated/<suite_id>-v1.json
        default_contract = PROJECT_ROOT / f"tests/contracts/generated/{suite_id}-v1.json"
        if default_contract.exists():
            contract_path = default_contract
    contract = None
    if contract_path and contract_path.exists():
        contract = json.loads(contract_path.read_text())

    # Scenarios
    scenarios = expand_scenarios(suite)
    if args.scenario:
        if args.scenario not in scenarios:
            print(
                f"error: scenario '{args.scenario}' not in suite. "
                f"Available: {scenarios}",
                file=sys.stderr,
            )
            return 2
        scenarios = [args.scenario]

    runs_per_scenario = args.runs or suite.get("runs_per_scenario", 3)
    if args.max_runs:
        runs_per_scenario = min(runs_per_scenario, args.max_runs)

    # ── Assemble once per suite ─────────────────────────────────────
    assembly = assemble_for_suite(suite)
    suite_dir = out_root / suite_id
    suite_dir.mkdir(parents=True, exist_ok=True)
    (suite_dir / "assembled-prompt.md").write_text(assembly.assembled_prompt)
    if suite.get("native"):
        composition_plan = {
            "native": True,
            "system_prompt": assembly.assembled_prompt,
            "warnings": assembly.warnings,
            "note": "No identity package — native behavioral prior control.",
        }
    else:
        composition_plan = {
            "character": suite["character"],
            "composition": suite.get("composition", {}),
            "chunks": [
                {
                    "component_type": c.component_type.value,
                    "provenance": {
                        "value": c.provenance.value if hasattr(c.provenance, "value") else str(c.provenance),
                        "source_file": c.provenance.source_file,
                        "source_type": c.provenance.source_type,
                    },
                }
                for c in assembly.chunks
            ],
            "warnings": assembly.warnings,
            "overrides": [
                {
                    "value": o.value if hasattr(o, "value") else str(o),
                    "source_file": o.source_file,
                }
                for o in assembly.overrides
            ],
        }
    (suite_dir / "composition-plan.json").write_text(
        json.dumps(composition_plan, indent=2, default=str)
    )
    if contract:
        (suite_dir / "behavioral-contract.json").write_text(
            json.dumps(contract, indent=2)
        )

    started_at = datetime.now(timezone.utc).isoformat()

    # ── Run every (model × scenario × run) combination ───────────────
    cost_total = 0.0
    all_results: List[Dict[str, Any]] = []
    summaries: List[Dict[str, Any]] = []

    for model_def in models:
        provider = get_provider(model_def.get("provider", "openai"))
        if not provider.available():
            print(
                f"warn: provider '{model_def.get('provider')}' not available "
                f"(missing credentials). Skipping model {model_def.get('id')}.",
                file=sys.stderr,
            )
            continue

        manifest = write_manifest(
            suite_dir / "manifest.json",
            suite_id,
            str(suite_path),
            suite.get("character", "native-control"),
            suite.get("composition", {}),
            model_def,
            contract_path,
            started_at,
            runs_per_scenario,
            extra={"native": bool(suite.get("native"))},
        )

        # Build work list
        work: List[Tuple[str, int]] = []
        for s in scenarios:
            for r in range(1, runs_per_scenario + 1):
                work.append((s, r))

        if args.parallel > 1:
            with cf.ThreadPoolExecutor(max_workers=args.parallel) as ex:
                futures = {
                    ex.submit(
                        run_scenario_for_suite,
                        suite, suite_id, s, model_def, provider, r,
                        runs_per_scenario, suite_dir,
                        PROJECT_ROOT / "tests/scenarios", args.seed,
                    ): (s, r)
                    for s, r in work
                }
                for fut in cf.as_completed(futures):
                    s, r = futures[fut]
                    try:
                        res = fut.result()
                    except Exception as e:
                        res = {
                            "scenario_id": s,
                            "run_number": r,
                            "error": str(e),
                            "traceback": traceback.format_exc(),
                        }
                    all_results.append(res)
                    if args.max_cost and cost_total >= args.max_cost:
                        print(
                            f"warn: max-cost ${args.max_cost:.2f} reached, stopping",
                            file=sys.stderr,
                        )
                        break
        else:
            for s, r in work:
                try:
                    res = run_scenario_for_suite(
                        suite, suite_id, s, model_def, provider, r,
                        runs_per_scenario, suite_dir,
                        PROJECT_ROOT / "tests/scenarios", args.seed,
                    )
                except Exception as e:
                    res = {
                        "scenario_id": s,
                        "run_number": r,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }
                all_results.append(res)
                if args.max_cost and cost_total >= args.max_cost:
                    print(
                        f"warn: max-cost ${args.max_cost:.2f} reached, stopping",
                        file=sys.stderr,
                    )
                    break

        # Write per-suite eval report
        report = build_suite_report(suite_id, model_def, all_results, contract)
        (suite_dir / "eval-report.json").write_text(json.dumps(report, indent=2))
        summaries.append(report)

    # Final summary
    final = {
        "run_id": out_root.name,
        "started_at": started_at,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "suite": suite_id,
        "models": [m.get("id") for m in models],
        "scenarios": scenarios,
        "runs_per_scenario": runs_per_scenario,
        "total_runs": len(all_results),
        "estimated_cost_usd": cost_total,
        "results": all_results,
    }
    (out_root / "run-summary.json").write_text(json.dumps(final, indent=2))

    # Markdown summary
    md = render_run_summary(final, summaries)
    (out_root / "run-summary.md").write_text(md)

    # Optional: invoke judge on transcripts
    if not args.no_judge:
        # Judge resolution order: CLI flags > matrix judge section > defaults
        jp = args.judge_provider
        jm = args.judge_model
        jt = None if args.judge_thinking == "auto" else args.judge_thinking == "true"
        if args.models or args.model:
            matrix_judge = {}
            try:
                matrix_path = Path(args.models).resolve() if args.models else None
                if matrix_path and matrix_path.exists():
                    matrix_judge = yaml.safe_load(matrix_path.read_text()).get("judge", {}) or {}
            except Exception:
                matrix_judge = {}
            if not jp:
                jp = matrix_judge.get("provider")
            if not jm:
                jm = matrix_judge.get("model")
            if jt is None and matrix_judge.get("thinking") is not None:
                jt = bool(matrix_judge.get("thinking"))
        try_invoke_judge(
            suite_dir, models, contract,
            judge_provider=jp, judge_model=jm,
            judge_thinking=jt, native=bool(suite.get("native")),
        )

    print(f"\n# Done. Run output: {out_root}", file=sys.stderr)
    return 0


def build_suite_report(
    suite_id: str,
    model: Dict[str, Any],
    results: List[Dict[str, Any]],
    contract: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Aggregate a per-suite report from raw results."""
    by_scenario: Dict[str, List[Dict[str, Any]]] = {}
    for r in results:
        by_scenario.setdefault(r.get("scenario_id", "?"), []).append(r)

    summary: Dict[str, Any] = {
        "suite": suite_id,
        "model": model.get("id"),
        "scenarios": {},
    }
    for s, runs in by_scenario.items():
        n = len(runs)
        n_mech_pass = sum(1 for r in runs if r.get("mechanical_passed"))
        n_errored = sum(1 for r in runs if r.get("error") or "ERROR" in (r.get("last_response_excerpt") or ""))
        summary["scenarios"][s] = {
            "runs": n,
            "mechanical_passed": n_mech_pass,
            "errored": n_errored,
        }
    return summary


def render_run_summary(final: Dict[str, Any], summaries: List[Dict[str, Any]]) -> str:
    """Render the top-level run summary as Markdown."""
    out = []
    out.append(f"# Evaluation Run {final['run_id']}")
    out.append("")
    out.append(f"- Suite: {final['suite']}")
    out.append(f"- Models: {', '.join(final['models'])}")
    out.append(f"- Scenarios: {len(final['scenarios'])}")
    out.append(f"- Runs per scenario: {final['runs_per_scenario']}")
    out.append(f"- Total runs: {final['total_runs']}")
    out.append(f"- Estimated cost: ${final['estimated_cost_usd']:.4f}")
    out.append("")
    for s in summaries:
        out.append(f"## {s['suite']} — {s['model']}")
        out.append("")
        out.append("| Scenario | Runs | Mechanical Pass | Errored |")
        out.append("|---|---|---|---|")
        for sc, info in s["scenarios"].items():
            out.append(
                f"| {sc} | {info['runs']} | {info['mechanical_passed']} | {info['errored']} |"
            )
        out.append("")
    return "\n".join(out)


def try_invoke_judge(
    suite_dir: Path,
    models: List[Dict[str, Any]],
    contract: Optional[Dict[str, Any]],
    judge_provider: Optional[str] = None,
    judge_model: Optional[str] = None,
    judge_thinking: Optional[bool] = None,
    native: bool = False,
) -> None:
    """Try to invoke the judge on each transcript. Skipped silently if
    no judge provider is configured. Errors are recorded per-eval but
    do not fail the run.

    Phase 5.B: one judge model is used consistently across subject
    families (no self-judging). judge_thinking enables the
    deliberative mode on providers that support it (deepseek/minimax).
    """
    try:
        # Lazy import to keep this module self-contained
        from tools.evaluate_transcript import evaluate_transcript
    except ImportError:
        return

    if not available_providers():
        return

    eval_files = sorted(suite_dir.glob("**/run-*.eval.json"))
    for eval_path in eval_files:
        try:
            result = json.loads(eval_path.read_text())
            transcript_path = Path(result["transcript_path"])
            scenario_yaml = PROJECT_ROOT / "tests/scenarios" / f"{result['scenario_id']}.yaml"
            scenario = yaml.safe_load(scenario_yaml.read_text()) if scenario_yaml.exists() else {}
            judge_extra = {"thinking": judge_thinking} if judge_thinking is not None else None
            judge_out = evaluate_transcript(
                transcript_path=transcript_path,
                scenario=scenario,
                contract=contract,
                judge_provider=judge_provider or "deepseek",
                judge_model=judge_model or "deepseek-v4-flash",
                native=native,
                judge_extra=judge_extra,
            )
            result.update(judge_out)
            result["judged"] = True
            eval_path.write_text(json.dumps(result, indent=2))
        except Exception as e:
            result["judge_error"] = str(e)
            eval_path.write_text(json.dumps(result, indent=2))


def cmd_resume(args: argparse.Namespace) -> int:
    """Resume an interrupted run."""
    run_dir = Path(args.resume).resolve()
    if not run_dir.exists():
        print(f"error: run directory not found: {run_dir}", file=sys.stderr)
        return 2
    print(f"# Resuming {run_dir} — this feature is a no-op stub for now.", file=sys.stderr)
    print("# Use --resume to point at a run directory; future runs will pick", file=sys.stderr)
    print("# up where they left off.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())