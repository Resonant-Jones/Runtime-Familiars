#!/usr/bin/env python3
"""
Runtime Familiars — Phase 5.B Calibration Driver

Runs the initial live behavioral calibration matrix:

    SUBJECT MODELS:  deepseek-v4-flash, MiniMax-M3
    CONFIGURATIONS:  native-control, moss, moss-gentle, roko-base,
                     vic-strategic
    SCENARIOS:       first-meeting, task-assistance, disagreement,
                     boundary-pressure, identity-disclosure
    REPETITIONS:     1

    = 2 × 5 × 5 × 1 = 50 conversations (+ 50 judge calls)

Every run preserves: assembled prompt, behavioral contract, scenario,
provider configuration, model identifier, generation parameters,
transcript, mechanical assertions, judge evaluation (spec §Calibration
Procedure).

CREDENTIALS
-----------
The driver bridges credentials from the Hermes environment (fail loudly
if absent, never print secrets):

    DeepSeek   DEEPSEEK_API_KEY / DEEPSEEK_BASE_URL  from HERMES_HOME/.env
    MiniMax    OAuth access token from HERMES_HOME/auth.json
               (minimax-oauth provider) → MINIMAX_API_KEY
               + MINIMAX_BASE_URL=https://api.minimax.io/v1

JUDGE
-----
One consistent judge across both subject families (default:
deepseek-v4-flash in deliberative/thinking mode) — no self-judging,
so cross-model comparison stays clean. Later passes can add MiniMax M3
as a second judge for judge-family bias detection.

USAGE
-----
    python3 tools/run_calibration.py                      # full matrix
    python3 tools/run_calibration.py --no-judge           # transcripts only
    python3 tools/run_calibration.py --parallel 2
    python3 tools/run_calibration.py --max-cost 1.00
    python3 tools/run_calibration.py --resume runs/<run-id>
"""

from __future__ import annotations

import argparse
import json
import os
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

from tools.eval import (  # noqa: E402
    assemble_for_suite,
    make_run_id,
    run_scenario_for_suite,
    write_manifest,
    estimate_cost,
)
from tools.providers import get_provider  # noqa: E402

DEFAULT_CONFIGS = ["native-control", "moss", "moss-gentle", "roko-base", "vic-strategic"]
DEFAULT_SCENARIOS = [
    "first-meeting", "task-assistance", "disagreement",
    "boundary-pressure", "identity-disclosure",
]

# ────────────────────────────────────────────────────────────────────────────
# Credential bridge (Hermes → harness env)
# ────────────────────────────────────────────────────────────────────────────


def bridge_hermes_credentials() -> None:
    """Populate harness env vars from the Hermes environment.

    DeepSeek: HERMES_HOME/.env → DEEPSEEK_API_KEY / DEEPSEEK_BASE_URL
    MiniMax:  HERMES_HOME/auth.json (minimax-oauth) → MINIMAX_API_KEY
              + MINIMAX_BASE_URL (OpenAI-compat /v1 endpoint for M3)

    Never prints secret values. Fails loudly with actionable guidance
    when a required credential cannot be found.
    """
    hermes_home = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))).expanduser()

    # DeepSeek from .env
    env_file = hermes_home / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key in ("DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL"):
                os.environ.setdefault(key, value)

    # MiniMax from auth.json (OAuth)
    auth_file = hermes_home / "auth.json"
    if auth_file.exists():
        try:
            auth = json.loads(auth_file.read_text())
            oauth = (
                auth.get("providers", {}).get("minimax-oauth", {})
                or auth.get("providers", {}).get("minimax", {})
            )
            token = oauth.get("access_token") or oauth.get("api_key")
            if token:
                os.environ.setdefault("MINIMAX_API_KEY", token)
                os.environ.setdefault(
                    "MINIMAX_BASE_URL", "https://api.minimax.io/v1"
                )
        except Exception as e:
            print(f"warn: could not read MiniMax OAuth credentials: {e}", file=sys.stderr)

    # Report availability (names only — never values)
    missing = []
    if not os.environ.get("DEEPSEEK_API_KEY"):
        missing.append("DEEPSEEK_API_KEY (set in Hermes .env or export it)")
    if not os.environ.get("MINIMAX_API_KEY"):
        missing.append("MINIMAX_API_KEY (Hermes minimax-oauth token in auth.json)")
    if missing:
        print(
            "error: missing credentials for calibration matrix:\n  - "
            + "\n  - ".join(missing)
            + "\nRefusing to run with partial credentials — the matrix must "
            "cover BOTH subject models.",
            file=sys.stderr,
        )
        sys.exit(2)


# ────────────────────────────────────────────────────────────────────────────
# Matrix loading
# ────────────────────────────────────────────────────────────────────────────


def load_matrix(path: Path) -> Dict[str, Any]:
    if not path.exists():
        print(f"error: matrix not found: {path}", file=sys.stderr)
        sys.exit(2)
    with open(path) as f:
        return yaml.safe_load(f)


def load_suite(config: str) -> Dict[str, Any]:
    suite_path = PROJECT_ROOT / "tests" / "suites" / f"{config}.yaml"
    if not suite_path.exists():
        print(f"error: suite not found: {suite_path}", file=sys.stderr)
        sys.exit(2)
    with open(suite_path) as f:
        suite = yaml.safe_load(f)
    # Calibration overrides: exactly the calibration scenarios, 1 run.
    suite["scenarios"] = DEFAULT_SCENARIOS
    suite["runs_per_scenario"] = 1
    return suite


# ────────────────────────────────────────────────────────────────────────────
# Cost estimate (before running — spec §40)
# ────────────────────────────────────────────────────────────────────────────


def estimate_matrix_cost(
    models: List[Dict[str, Any]],
    configs: List[str],
    scenarios: List[str],
) -> float:
    """Rough upper-bound estimate in USD before any calls are made.

    Uses per-conversation token budgets: assembled prompt ~2.5k in,
    ~1k in history per turn, ~150 out per turn, ~3 turns avg per
    calibration scenario; judge ~2k in / ~300 out per transcript.
    """
    total = 0.0
    for model in models:
        provider = model.get("provider", "?")
        mid = model.get("model", "?")
        key = f"{provider}/{mid}"
        rate_in, rate_out = {
            "deepseek/deepseek-v4-flash": (0.00014, 0.00028),
            "deepseek/deepseek-v4-pro": (0.00055, 0.00219),
            "minimax/MiniMax-M3": (0.00030, 0.00120),
            "minimax/minimax-m3": (0.00030, 0.00120),
        }.get(key, (0.0, 0.0))

        n_convos = len(configs) * len(scenarios)
        prompt_tokens = 2500
        history_tokens = 1000 * 3
        out_tokens = 150 * 3
        per_convo_in = (prompt_tokens + history_tokens) / 1000.0 * rate_in
        per_convo_out = out_tokens / 1000.0 * rate_out
        total += n_convos * (per_convo_in + per_convo_out)

        # Judge calls (one per transcript)
        judge_in = 2000 / 1000.0 * rate_in
        judge_out = 300 / 1000.0 * rate_out
        total += n_convos * (judge_in + judge_out)
    return total


# ────────────────────────────────────────────────────────────────────────────
# Run bookkeeping
# ────────────────────────────────────────────────────────────────────────────


def is_complete(eval_path: Path, need_judge: bool) -> bool:
    """True if this run-NN.eval.json exists and satisfies the run mode."""
    if not eval_path.exists():
        return False
    try:
        data = json.loads(eval_path.read_text())
    except Exception:
        return False
    if data.get("error"):
        return False
    if need_judge and not data.get("judged"):
        return False
    return True


# ────────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────────


def rejudge_run(
    out_root: Path,
    judge_provider: str,
    judge_model: str,
    judge_thinking: bool,
    models: Optional[set] = None,
    force: bool = False,
    configs: Optional[List[str]] = None,
) -> int:
    """Re-run the judge on every transcript in an existing run.

    Conversations are NEVER regenerated — only the judge phase is
    re-executed (fixes judge calls that failed on earlier code, e.g.
    thinking-mode token budget exhaustion). Already-judged transcripts
    are skipped unless force=True.
    """
    from tools.evaluate_transcript import evaluate_transcript

    print(f"# Re-judging transcripts in {out_root}", file=sys.stderr)
    print(f"# Judge: {judge_provider}/{judge_model} thinking={judge_thinking}", file=sys.stderr)

    eval_files = sorted(out_root.glob("**/run-*.eval.json"))
    updated = 0
    failed = 0
    skipped = 0
    for eval_path in eval_files:
        try:
            result = json.loads(eval_path.read_text())
        except Exception:
            print(f"  warn: unreadable eval {eval_path}", file=sys.stderr)
            continue
        model_id = result.get("model_id")
        if models and model_id and model_id not in models:
            continue
        config = result.get("suite", result.get("_suite_id"))
        if configs and config and config not in configs:
            continue
        # Skip already-OK judgments (transcripts with a real verdict).
        if not force and result.get("judged") and result.get("judge_verdict") != "ERROR":
            skipped += 1
            continue
        suite_id = result.get("suite", result.get("_suite_id"))
        # Native detection: prefer the recorded flag; fall back to the
        # config dir name (parents[1] = <model>/<config>/<scenario>/run).
        native = bool(result.get("judge_native")) or bool(
            suite_id and Path(eval_path).parents[1].name == "native-control"
        )
        transcript_path = Path(result.get("transcript_path", ""))
        if not transcript_path.exists():
            # Try to resolve relative to the run root
            candidate = out_root / result["scenario_id"] / f"run-{result['run_number']:02d}.md"
            if candidate.exists():
                transcript_path = candidate
            else:
                print(f"  warn: transcript missing for {eval_path}", file=sys.stderr)
                continue
        scenario_path = PROJECT_ROOT / "tests/scenarios" / f"{result.get('scenario_id')}.yaml"
        scenario = yaml.safe_load(scenario_path.read_text()) if scenario_path.exists() else {}
        contract = None
        contract_path = Path(eval_path).parent.parent / "behavioral-contract.json"
        if contract_path.exists():
            contract = json.loads(contract_path.read_text())

        judge_extra = {"thinking": judge_thinking} if judge_thinking is not None else None
        judge_out = evaluate_transcript(
            transcript_path=transcript_path,
            scenario=scenario,
            contract=contract,
            judge_provider=judge_provider,
            judge_model=judge_model,
            native=native,
            judge_extra=judge_extra,
        )
        result.update(judge_out)
        result["judged"] = True
        eval_path.write_text(json.dumps(result, indent=2))
        verdict = judge_out.get("judge_verdict")
        print(f"  {eval_path.relative_to(out_root)} → {verdict}", file=sys.stderr)
        if verdict == "ERROR":
            failed += 1
        else:
            updated += 1

    # Regenerate the run summary
    summary_path = out_root / "run-summary.json"
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text())
            results = []
            for p in sorted(out_root.glob("**/run-*.eval.json")):
                try:
                    results.append(json.loads(p.read_text()))
                except Exception:
                    pass
            summary["results"] = results
            summary["judged"] = sum(1 for r in results if r.get("judged"))
            summary["errored"] = sum(1 for r in results if r.get("error"))
            summary["completed_at"] = datetime.now(timezone.utc).isoformat()
            summary_path.write_text(json.dumps(summary, indent=2))
            print(f"# Updated run-summary.json ({len(results)} results)", file=sys.stderr)
        except Exception as e:
            print(f"warn: could not update run-summary.json: {e}", file=sys.stderr)

    print(f"# Re-judge done: {updated} judged, {failed} failed, {skipped} skipped", file=sys.stderr)
    return 0 if failed == 0 else 1


def main() -> int:
    p = argparse.ArgumentParser(description="Phase 5.B calibration driver.")
    p.add_argument(
        "--matrix", default="tests/models/calibration-matrix.yaml",
        help="Calibration matrix YAML (default: tests/models/calibration-matrix.yaml)",
    )
    p.add_argument(
        "--configs", nargs="+", default=DEFAULT_CONFIGS,
        help="Suite configs to run (default: native-control moss moss-gentle roko-base vic-strategic)",
    )
    p.add_argument(
        "--models", nargs="+", default=None,
        help="Model ids from the matrix to run (default: all). "
             "Useful when one substrate is unavailable (e.g. quota exhausted).",
    )
    p.add_argument(
        "--scenarios", nargs="+", default=None,
        help="Scenarios to run (default: the 5 calibration scenarios)",
    )
    p.add_argument("--runs", type=int, default=1, help="Runs per scenario (default 1)")
    p.add_argument("--parallel", type=int, default=1, help="Concurrency level")
    p.add_argument(
        "--max-cost", type=float, default=None,
        help="Abort if estimated cost exceeds this USD amount",
    )
    p.add_argument("--no-judge", action="store_true", help="Skip judge invocation")
    p.add_argument("--judge-provider", help="Override judge provider")
    p.add_argument("--judge-model", help="Override judge model")
    p.add_argument(
        "--judge-thinking",
        choices=["true", "false", "auto"], default="auto",
        help="Judge thinking mode override",
    )
    p.add_argument("--resume", help="Resume an existing run directory")
    p.add_argument("--output", help="Output directory (default: runs/<timestamp>)")
    p.add_argument("--force", action="store_true", help="Re-run completed transcripts")
    p.add_argument(
        "--rejudge", action="store_true",
        help="Re-run the judge on existing transcripts without regenerating "
             "conversations (fixes judge calls that failed on earlier code).",
    )
    args = p.parse_args()

    bridge_hermes_credentials()

    matrix = load_matrix(PROJECT_ROOT / args.matrix)
    models = matrix.get("models", [])
    if not models:
        print("error: matrix has no models", file=sys.stderr)
        return 2
    if args.models:
        wanted = set(args.models)
        models = [m for m in models if m.get("id") in wanted]
        found_ids = {m.get("id") for m in models}
        missing = wanted - found_ids
        if missing:
            print(
                f"error: requested model ids not in matrix: {sorted(missing)}",
                file=sys.stderr,
            )
            return 2

    scenarios = args.scenarios or DEFAULT_SCENARIOS
    configs = args.configs
    runs_per = args.runs

    # Cost estimate before starting (§40)
    est = estimate_matrix_cost(models, configs, scenarios)
    print(f"# Calibration matrix: {len(models)} models × {len(configs)} configs × "
          f"{len(scenarios)} scenarios × {runs_per} run(s)")
    print(f"# Conversations: {len(models) * len(configs) * len(scenarios) * runs_per}")
    print(f"# Estimated cost: ${est:.4f} (subject + judge calls)")
    if args.max_cost is not None and est > args.max_cost:
        print(
            f"error: estimated cost ${est:.4f} exceeds --max-cost ${args.max_cost:.2f}. "
            f"Aborting before any calls.",
            file=sys.stderr,
        )
        return 2

    # Output directory
    if args.resume:
        out_root = Path(args.resume).resolve()
        if not out_root.exists():
            print(f"error: resume directory not found: {out_root}", file=sys.stderr)
            return 2
        print(f"# Resuming run in {out_root}", file=sys.stderr)
    else:
        out_root = Path(args.output).resolve() if args.output else PROJECT_ROOT / "runs" / make_run_id()
        out_root.mkdir(parents=True, exist_ok=True)

    need_judge = not args.no_judge
    judge_provider = args.judge_provider or matrix.get("judge", {}).get("provider", "deepseek")
    judge_model = args.judge_model or matrix.get("judge", {}).get("model", "deepseek-v4-flash")
    if args.judge_thinking == "auto":
        judge_thinking = matrix.get("judge", {}).get("thinking", True)
    else:
        judge_thinking = args.judge_thinking == "true"

    # Re-judge mode: walk existing run, re-run judge on every transcript,
    # never regenerate conversations.
    if args.rejudge:
        return rejudge_run(
            out_root, judge_provider, judge_model, judge_thinking,
            models={m.get("id") for m in models},
            force=args.force,
            configs=configs,
        )

    started_at = datetime.now(timezone.utc).isoformat()
    all_results: List[Dict[str, Any]] = []
    run_summary: Dict[str, Any] = {
        "run_id": out_root.name,
        "phase": "5.B calibration",
        "matrix": str(args.matrix),
        "models": [m.get("id") for m in models],
        "configs": configs,
        "scenarios": scenarios,
        "runs_per_scenario": runs_per,
        "judge": {"provider": judge_provider, "model": judge_model, "thinking": judge_thinking},
        "started_at": started_at,
        "estimated_cost_usd": round(est, 4),
    }

    # ── Run each model × config ──────────────────────────────────────
    for model_def in models:
        provider_name = model_def.get("provider", "?")
        try:
            provider = get_provider(provider_name)
        except KeyError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        if not provider.available():
            print(
                f"error: provider '{provider_name}' (model '{model_def.get('model')}') "
                f"is not configured. Missing credentials. The calibration matrix "
                f"requires BOTH subject models; refusing to run partial.",
                file=sys.stderr,
            )
            return 2

        model_id = model_def.get("id", model_def.get("model", "?"))
        print(f"\n# ── Model: {model_id} ({provider_name}/{model_def.get('model')}) ──")

        for config in configs:
            suite = load_suite(config)
            suite_dir = out_root / model_id / config
            suite_dir.mkdir(parents=True, exist_ok=True)

            # Preserve exact runtime input (§15)
            assembly = assemble_for_suite(suite)
            (suite_dir / "assembled-prompt.md").write_text(assembly.assembled_prompt)
            (suite_dir / "composition-plan.json").write_text(
                json.dumps({
                    "native": bool(suite.get("native")),
                    "character": suite.get("character"),
                    "composition": suite.get("composition", {}),
                    "warnings": list(assembly.warnings),
                }, indent=2, default=str)
            )
            contract_path: Optional[Path] = None
            if not suite.get("native"):
                contract_path = PROJECT_ROOT / "tests" / "contracts" / "generated" / f"{config}-v1.json"
            contract = None
            if contract_path and contract_path.exists():
                contract = json.loads(contract_path.read_text())
                (suite_dir / "behavioral-contract.json").write_text(
                    json.dumps(contract, indent=2)
                )

            write_manifest(
                suite_dir / "manifest.json",
                config,
                f"tests/suites/{config}.yaml",
                suite.get("character", "native-control"),
                suite.get("composition", {}),
                model_def,
                contract_path,
                started_at,
                runs_per,
                extra={"native": bool(suite.get("native")), "phase": "5.B calibration"},
            )

            # Work list
            work: List[Tuple[str, int]] = []
            for s in scenarios:
                for r in range(1, runs_per + 1):
                    eval_path = suite_dir / s / f"run-{r:02d}.eval.json"
                    if not args.force and is_complete(eval_path, need_judge):
                        # Resume: reuse completed transcript+judgment
                        try:
                            all_results.append(json.loads(eval_path.read_text()))
                        except Exception:
                            pass
                        continue
                    work.append((s, r))

            if not work:
                print(f"  {config}: complete (resumed)")
                continue

            print(f"  {config}: {len(work)} conversation(s)")

            def _run_one(args_tuple: Tuple[str, int]) -> Dict[str, Any]:
                s, r = args_tuple
                try:
                    res = run_scenario_for_suite(
                        suite, config, s, model_def, provider, r,
                        runs_per, suite_dir,
                        PROJECT_ROOT / "tests/scenarios", None,
                    )
                    res["_model_id"] = model_id
                    res["_suite_id"] = config
                    res["model_id"] = model_id
                    res["provider"] = provider_name
                    res["model"] = model_def.get("model")
                    res["suite"] = config
                    # Judge immediately (per-run, not batched) so a
                    # mid-run interruption leaves judged results behind.
                    if need_judge:
                        from tools.evaluate_transcript import evaluate_transcript
                        scenario_path = PROJECT_ROOT / "tests" / "scenarios" / f"{s}.yaml"
                        scenario = yaml.safe_load(scenario_path.read_text()) if scenario_path.exists() else {}
                        judge_extra = {"thinking": judge_thinking} if judge_thinking is not None else None
                        judge_out = evaluate_transcript(
                            transcript_path=Path(res["transcript_path"]),
                            scenario=scenario,
                            contract=contract,
                            judge_provider=judge_provider,
                            judge_model=judge_model,
                            native=bool(suite.get("native")),
                            judge_extra=judge_extra,
                        )
                        res.update(judge_out)
                        res["judged"] = True
                        eval_path = suite_dir / s / f"run-{r:02d}.eval.json"
                        eval_path.write_text(json.dumps(res, indent=2))
                    return res
                except Exception as e:
                    return {
                        "scenario_id": s, "run_number": r,
                        "error": str(e), "traceback": traceback.format_exc(),
                    }

            if args.parallel > 1:
                with cf.ThreadPoolExecutor(max_workers=args.parallel) as ex:
                    futures = {ex.submit(_run_one, w): w for w in work}
                    for fut in cf.as_completed(futures):
                        all_results.append(fut.result())
            else:
                for w in work:
                    all_results.append(_run_one(w))

    # ── Summary ──────────────────────────────────────────────────────
    completed_at = datetime.now(timezone.utc).isoformat()
    run_summary["completed_at"] = completed_at
    run_summary["total_results"] = len(all_results)
    n_errored = sum(1 for r in all_results if r.get("error"))
    n_judged = sum(1 for r in all_results if r.get("judged"))
    run_summary["errored"] = n_errored
    run_summary["judged"] = n_judged
    run_summary["results"] = all_results

    (out_root / "run-summary.json").write_text(json.dumps(run_summary, indent=2))

    # Markdown summary
    md = ["# Phase 5.B Calibration Run", ""]
    md.append(f"- Run ID: `{out_root.name}`")
    md.append(f"- Models: {', '.join(run_summary['models'])}")
    md.append(f"- Configs: {', '.join(configs)}")
    md.append(f"- Scenarios: {len(scenarios)}")
    md.append(f"- Total results: {len(all_results)} (errored: {n_errored}, judged: {n_judged})")
    md.append(f"- Estimated cost: ${est:.4f}")
    md.append("")
    md.append("| Model | Config | Scenario | Verdict | Conf |")
    md.append("|---|---|---|---|---|")
    for r in all_results:
        md.append(
            f"| {r.get('_model_id', '?')} | {r.get('_suite_id', '?')} | "
            f"{r.get('scenario_id', '?')} | {r.get('judge_verdict', '-')} | "
            f"{r.get('judge_confidence', '-')} |"
        )
    (out_root / "run-summary.md").write_text("\n".join(md))

    print(f"\n# Calibration run complete: {out_root}")
    print(f"# Results: {len(all_results)} | errored: {n_errored} | judged: {n_judged}")
    print("# Run tools/eval_report.py to aggregate reports.")
    return 0


if __name__ == "__main__":
    sys.exit(main())