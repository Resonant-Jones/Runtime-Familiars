#!/usr/bin/env python3
"""
Runtime Familiars — Evaluation Report Aggregator

Reads one or more run directories (or a top-level runs/ dir) and
produces aggregate reports:

    reports/
    ├── summary.md
    ├── summary.json
    ├── failures.md
    ├── model-comparison.md
    ├── composition-deltas.md    # only if delta suite dirs present
    └── review-queue.md

USAGE
-----
    python3 tools/eval_report.py runs/2026-08-09-001
    python3 tools/eval_report.py runs/                     # all runs under runs/
    python3 tools/eval_report.py runs/2026-08-09-001 --output reports/
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ────────────────────────────────────────────────────────────────────────────
# Aggregation
# ────────────────────────────────────────────────────────────────────────────


def load_run(run_dir: Path) -> Dict[str, Any]:
    """Load all results from a run directory."""
    summary_path = run_dir / "run-summary.json"
    if not summary_path.exists():
        # Try to find a suite dir with manifest
        for suite_dir in run_dir.iterdir():
            if not suite_dir.is_dir():
                continue
            if (suite_dir / "manifest.json").exists():
                return load_run_from_suite(suite_dir)
        return {"run_id": run_dir.name, "results": [], "missing": True}

    summary = json.loads(summary_path.read_text())
    summary["results"] = []
    # Walk ALL eval.json files in nested suite dirs (calibration layout
    # nests model → config → scenario → run-NN.eval.json).
    for eval_path in sorted(run_dir.glob("**/run-*.eval.json")):
        try:
            summary["results"].append(json.loads(eval_path.read_text()))
        except Exception:
            pass
    summary["suite_dirs"] = [
        str(p) for p in run_dir.rglob("manifest.json")
    ]
    return summary


def load_run_from_suite(suite_dir: Path) -> Dict[str, Any]:
    """Load a single suite dir as a run."""
    manifest = json.loads((suite_dir / "manifest.json").read_text())
    results = []
    for eval_path in sorted(suite_dir.glob("*/run-*.eval.json")):
        try:
            results.append(json.loads(eval_path.read_text()))
        except Exception:
            pass
    return {
        "run_id": suite_dir.parent.name + "/" + suite_dir.name,
        "suite": manifest.get("suite"),
        "manifest": manifest,
        "results": results,
    }


# ────────────────────────────────────────────────────────────────────────────
# Aggregation helpers
# ────────────────────────────────────────────────────────────────────────────


def aggregate_by_scenario(results: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for r in results:
        s = r.get("scenario_id", "?")
        out.setdefault(s, {"runs": 0, "mech_pass": 0, "errored": 0, "verdicts": {}})
        out[s]["runs"] += 1
        if r.get("mechanical_passed"):
            out[s]["mech_pass"] += 1
        if r.get("error") or "ERROR" in (r.get("last_response_excerpt") or ""):
            out[s]["errored"] += 1
        verdict = r.get("judge_verdict") or "unjudged"
        out[s]["verdicts"][verdict] = out[s]["verdicts"].get(verdict, 0) + 1
    return out


def average_scores(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """Average each judge dimension across judged results.

    Native-control runs (judge_native=True) are averaged separately
    from contract-fidelity runs so the two never mix (Phase 5.B
    "Record native-control results separately from Familiar fidelity
    scores").
    """
    native = [r for r in results if r.get("judge_native")]
    contract = [r for r in results if not r.get("judge_native")]
    out: Dict[str, float] = {}
    for label, group in (("native", native), ("contract", contract)):
        by_dim: Dict[str, List[float]] = {}
        for r in group:
            for k, v in (r.get("judge_scores") or {}).items():
                by_dim.setdefault(k, []).append(float(v))
        for k, v in by_dim.items():
            key = f"{k} ({label})" if label == "native" else k
            out[key] = round(sum(v) / len(v), 2)
    return out


# ────────────────────────────────────────────────────────────────────────────
# Report writers
# ────────────────────────────────────────────────────────────────────────────


def render_summary_md(runs: List[Dict[str, Any]]) -> str:
    out = []
    out.append("# Evaluation Summary")
    out.append("")
    out.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    out.append(f"Runs aggregated: {len(runs)}")
    out.append("")

    for run in runs:
        rid = run.get("run_id", "?")
        results = run.get("results", [])
        out.append(f"## Run: `{rid}`")
        out.append("")
        if run.get("missing"):
            out.append("(missing run-summary.json)")
            out.append("")
            continue

        out.append(f"- Suite: {run.get('suite', '?')}")
        out.append(f"- Total runs: {len(results)}")
        n_judged = sum(1 for r in results if r.get("judged"))
        out.append(f"- Judged: {n_judged}")
        out.append("")

        # Per-scenario breakdown
        by_scenario = aggregate_by_scenario(results)
        out.append("| Scenario | Runs | Mech Pass | Errored | Verdicts |")
        out.append("|---|---|---|---|---|")
        for s, info in sorted(by_scenario.items()):
            verdicts_str = ", ".join(
                f"{k}:{v}" for k, v in sorted(info["verdicts"].items())
            )
            out.append(
                f"| {s} | {info['runs']} | {info['mech_pass']} | "
                f"{info['errored']} | {verdicts_str or '-'} |"
            )
        out.append("")

        # Average scores
        avgs = average_scores(results)
        if avgs:
            out.append("**Average judge scores:**")
            out.append("")
            for dim, avg in sorted(avgs.items()):
                out.append(f"- `{dim}`: {avg}")
            out.append("")

    return "\n".join(out)


def render_failures_md(runs: List[Dict[str, Any]]) -> str:
    out = []
    out.append("# Failures")
    out.append("")
    out.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    out.append("")

    failures = []
    for run in runs:
        rid = run.get("run_id", "?")
        for r in run.get("results", []):
            verdict = r.get("judge_verdict")
            # Native-control runs are informational by design — never
            # listed as failures (Phase 5.B).
            if r.get("judge_native") or verdict == "informational":
                continue
            mech = r.get("mechanical_passed")
            has_error = r.get("error") or "ERROR" in (r.get("last_response_excerpt") or "")
            is_failure = (
                verdict in ("fail", "ERROR")
                or has_error
                or (mech is False and mech is not None)
            )
            if is_failure:
                failures.append((rid, r))

    if not failures:
        out.append("(none)")
        return "\n".join(out)

    out.append(f"Total failures: {len(failures)}")
    out.append("")
    for rid, r in failures:
        sid = r.get("scenario_id", "?")
        runnum = r.get("run_number", "?")
        out.append(f"- `{rid}/{sid}/run-{runnum:02d}` — "
                   f"verdict={r.get('judge_verdict')}, "
                   f"mech_pass={r.get('mechanical_passed')}")
        if r.get("judge_summary"):
            out.append(f"  - summary: {r['judge_summary']}")
        for fnd in r.get("judge_findings", [])[:3]:
            out.append(f"  - {fnd.get('dimension','?')}/{fnd.get('severity','?')}: {fnd.get('reason','')}")
        out.append("")
    return "\n".join(out)


def render_model_comparison_md(runs: List[Dict[str, Any]]) -> str:
    out = []
    out.append("# Model Comparison")
    out.append("")
    out.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    out.append("")

    by_model: Dict[str, List[Dict[str, Any]]] = {}
    for run in runs:
        m = run.get("manifest", {}).get("model", {})
        default_mid = m.get("id") or m.get("model") or "unknown"
        for r in run.get("results", []):
            mid = r.get("model_id") or default_mid
            by_model.setdefault(mid, []).append(r)

    if not by_model:
        out.append("(no model info available)")
        return "\n".join(out)

    out.append("| Model | Runs | Pass Rate | Avg Identity | Avg Drift | Avg Tone |")
    out.append("|---|---|---|---|---|---|")
    for mid, results in sorted(by_model.items()):
        n = len(results)
        if n == 0:
            continue
        # Contract-fidelity runs only (native controls are informational).
        contract = [r for r in results if not r.get("judge_native")]
        n_pass = sum(1 for r in contract if r.get("judge_verdict") == "pass")
        pass_rate = n_pass / len(contract) if contract else float("nan")
        avgs = average_scores(contract)
        avg_id = avgs.get("identity_fidelity", "-")
        avg_drift = avgs.get("drift", "-")
        avg_tone = avgs.get("tone_fidelity", "-")
        out.append(
            f"| {mid} | {n} | {pass_rate:.0%} | {avg_id} | {avg_drift} | {avg_tone} |"
        )
    out.append("")
    return "\n".join(out)


def render_native_prior_md(runs: List[Dict[str, Any]]) -> str:
    """Phase 5.B: native behavioral prior comparison across models.

    Rows = native-control runs grouped by model; columns = the 10
    native dimensions. Recorded separately from fidelity scores.
    """
    out = []
    out.append("# Native Behavioral Prior (Phase 5.B)")
    out.append("")
    out.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    out.append("")
    out.append(
        "Un-persona'd control runs. These are OBSERVED behaviors under the "
        "evaluation conditions — not permanent traits of the model. They are "
        "the reference against which familiarized runs are compared "
        "(over-prompting / capability degradation)."
    )
    out.append("")

    by_model: Dict[str, List[Dict[str, Any]]] = {}
    for run in runs:
        m = run.get("manifest", {}).get("model", {})
        default_mid = m.get("id") or m.get("model") or "unknown"
        for r in run.get("results", []):
            if r.get("judge_native"):
                mid = r.get("model_id") or default_mid
                by_model.setdefault(mid, []).append(r)

    if not by_model:
        out.append("(no native-control runs found)")
        return "\n".join(out)

    dims = [
        "conversational_nuance", "adaptability", "task_competence",
        "conflict_handling", "verbosity", "initiative", "warmth",
        "directness", "epistemic_caution", "identity_neutrality",
    ]
    out.append("| Model | " + " | ".join(dims) + " |")
    out.append("|" + "---|" * (len(dims) + 1))
    for mid, results in sorted(by_model.items()):
        avgs = average_scores(results)
        cells = [str(avgs.get(f"{d} (native)") or "-") for d in dims]
        out.append(f"| {mid} | " + " | ".join(cells) + " |")
    out.append("")
    out.append(
        "Compare against the same model's familiarized runs: a familiar "
        "configuration that drops native nuance/adaptability/task competence "
        "by >1 point is over-prompting (Phase 5.B comparative question 5)."
    )
    out.append("")
    return "\n".join(out)


def render_composition_deltas_md(runs: List[Dict[str, Any]]) -> str:
    out = []
    out.append("# Composition Deltas")
    out.append("")
    out.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    out.append("")
    out.append("Compare baseline vs variant suites. Run `tools/compare_runs.py` "
               "for the full delta-judge output.")
    out.append("")
    delta_runs = [r for r in runs if "deltas" in r.get("run_id", "")]
    if not delta_runs:
        out.append("(no delta runs found)")
        return "\n".join(out)

    for r in delta_runs:
        out.append(f"## {r['run_id']}")
        out.append("")
        out.append("| Scenario | Runs | Verdict |")
        out.append("|---|---|---|")
        for res in r.get("results", []):
            out.append(
                f"| {res.get('scenario_id')} | {res.get('run_number')} | "
                f"{res.get('judge_verdict', '-')} |"
            )
        out.append("")
    return "\n".join(out)


def render_review_queue_md(runs: List[Dict[str, Any]], audit_rate: float = 0.05) -> str:
    """Build the human review queue (§33-34)."""
    out = []
    out.append("# Human Review Queue")
    out.append("")
    out.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    out.append("")
    out.append(f"Audit sample rate for PASS runs: {audit_rate:.0%}")
    out.append("")

    queue: List[Dict[str, Any]] = []
    pass_runs_for_audit: List[Dict[str, Any]] = []

    for run in runs:
        rid = run.get("run_id", "?")
        for r in run.get("results", []):
            verdict = r.get("judge_verdict")
            confidence = r.get("judge_confidence", 1.0)
            mech = r.get("mechanical_passed")
            has_error = r.get("error") or "ERROR" in (r.get("last_response_excerpt") or "")
            drift = (r.get("judge_scores") or {}).get("drift", 1)

            reasons = []
            if r.get("judge_native"):
                reasons.append("native_control")  # manual review priority (Phase 5.B)
            if verdict == "fail":
                reasons.append("judge:FAIL")
            if verdict == "ERROR":
                reasons.append("judge:ERROR")
            if has_error:
                reasons.append("provider:ERROR")
            if mech is False and mech is not None:
                reasons.append("mechanical:FAIL")
            if drift and drift >= 4:
                reasons.append(f"drift:{drift}")
            if confidence and confidence < 0.7:
                reasons.append(f"low_confidence:{confidence:.2f}")

            if reasons:
                queue.append({
                    "run_id": rid,
                    "scenario_id": r.get("scenario_id"),
                    "run_number": r.get("run_number"),
                    "transcript_path": r.get("transcript_path"),
                    "reasons": reasons,
                    "verdict": verdict,
                    "judge_summary": r.get("judge_summary", ""),
                    "findings": r.get("judge_findings", []),
                })
            elif verdict == "pass":
                pass_runs_for_audit.append({
                    "run_id": rid,
                    "scenario_id": r.get("scenario_id"),
                    "run_number": r.get("run_number"),
                    "transcript_path": r.get("transcript_path"),
                })

    # Sample PASS runs for audit
    import random
    random.seed(42)
    n_audit = max(1, int(len(pass_runs_for_audit) * audit_rate))
    audit_sample = random.sample(pass_runs_for_audit, min(n_audit, len(pass_runs_for_audit)))
    for entry in audit_sample:
        entry["reasons"] = ["audit_sample"]
    queue.extend(audit_sample)

    if not queue:
        out.append("(empty — no failures or audit samples)")
        return "\n".join(out)

    out.append(f"Queue size: {len(queue)}")
    out.append("")
    for entry in sorted(queue, key=lambda e: (e.get("reasons", [""])[0], e.get("scenario_id", ""))):
        out.append(
            f"- `{entry['run_id']}/{entry['scenario_id']}/run-{entry['run_number']:02d}` — "
            f"reasons={','.join(entry['reasons'])}"
        )
        if entry.get("transcript_path"):
            out.append(f"  - transcript: `{entry['transcript_path']}`")
        if entry.get("judge_summary"):
            out.append(f"  - summary: {entry['judge_summary']}")
        for fnd in entry.get("findings", [])[:2]:
            out.append(f"  - {fnd.get('dimension','?')}: {fnd.get('reason','')}")
        out.append("")
    return "\n".join(out)


# ────────────────────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────────────────────


def main() -> int:
    p = argparse.ArgumentParser(description="Aggregate evaluation runs into reports.")
    p.add_argument("input", nargs="+", help="Run dir(s) or a top-level runs/ directory")
    p.add_argument("--output", "-o", default="reports", help="Output directory")
    p.add_argument("--audit-rate", type=float, default=0.05, help="PASS audit sample rate")
    args = p.parse_args()

    runs: List[Dict[str, Any]] = []
    for inp in args.input:
        inp_path = Path(inp).resolve()
        if not inp_path.exists():
            print(f"warn: input does not exist: {inp_path}", file=sys.stderr)
            continue
        if inp_path.is_dir() and (inp_path / "run-summary.json").exists():
            runs.append(load_run(inp_path))
        elif inp_path.is_dir():
            # Could be a top-level runs/ dir — load every subdirectory
            for sub in sorted(inp_path.iterdir()):
                if sub.is_dir() and (sub / "run-summary.json").exists():
                    runs.append(load_run(sub))
                elif sub.is_dir() and (sub / "manifest.json").exists():
                    runs.append(load_run_from_suite(sub))
        elif inp_path.is_file() and inp_path.suffix == ".json":
            # Could be a single suite eval-report.json
            try:
                d = json.loads(inp_path.read_text())
                d["run_id"] = inp_path.stem
                runs.append(d)
            except Exception as e:
                print(f"warn: could not load {inp_path}: {e}", file=sys.stderr)

    if not runs:
        print("error: no runs loaded", file=sys.stderr)
        return 2

    out_dir = Path(args.output).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_md = render_summary_md(runs)
    failures_md = render_failures_md(runs)
    model_md = render_model_comparison_md(runs)
    native_md = render_native_prior_md(runs)
    deltas_md = render_composition_deltas_md(runs)
    review_md = render_review_queue_md(runs, audit_rate=args.audit_rate)

    (out_dir / "summary.md").write_text(summary_md)
    (out_dir / "summary.json").write_text(
        json.dumps({"runs": [{k: v for k, v in r.items() if k != "results"} for r in runs],
                    "result_count": sum(len(r.get("results", [])) for r in runs)}, indent=2)
    )
    (out_dir / "failures.md").write_text(failures_md)
    (out_dir / "model-comparison.md").write_text(model_md)
    (out_dir / "native-prior.md").write_text(native_md)
    (out_dir / "composition-deltas.md").write_text(deltas_md)
    (out_dir / "review-queue.md").write_text(review_md)

    print(f"# Reports written to {out_dir}", file=sys.stderr)
    print(f"#   summary.md, summary.json, failures.md, model-comparison.md,", file=sys.stderr)
    print(f"#   native-prior.md, composition-deltas.md, review-queue.md", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())