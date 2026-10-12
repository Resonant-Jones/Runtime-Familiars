#!/usr/bin/env python3
"""
Runtime Familiars — Run Comparison

Compares two evaluation runs and produces a regression report.

USAGE
-----
    # Compare a current run against a baseline
    python3 tools/compare_runs.py runs/baseline/2026-08-01-001 runs/current/2026-08-09-001
    python3 tools/compare_runs.py runs/baseline/ runs/current/ --output reports/baseline-vs-current.md

WHAT IT DOES
------------
- Loads both run directories (must contain run-summary.json or eval.json files)
- For each (suite, scenario, model), compares aggregate metrics
- Reports regressions: scenarios whose pass rate dropped or whose
  identity/drift scores regressed beyond a configurable threshold
- Reports improvements: the reverse
- Marks a run as "baseline" so future runs can be compared against it

This is NOT exact-text matching (per §51 non-goals). It compares
behavioral evaluations and declared deltas only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.eval_report import load_run, load_run_from_suite, aggregate_by_scenario, average_scores  # noqa: E402


def load(path: Path) -> List[Dict[str, Any]]:
    """Load one or more runs from a path."""
    if path.is_dir() and (path / "run-summary.json").exists():
        return [load_run(path)]
    if path.is_dir():
        runs = []
        for sub in sorted(path.iterdir()):
            if sub.is_dir():
                if (sub / "run-summary.json").exists():
                    runs.append(load_run(sub))
                elif (sub / "manifest.json").exists():
                    runs.append(load_run_from_suite(sub))
        return runs
    return []


def compare_runs(
    baseline_runs: List[Dict[str, Any]],
    current_runs: List[Dict[str, Any]],
    pass_rate_drop_threshold: float = 0.10,
    score_drop_threshold: float = 0.5,
) -> Dict[str, Any]:
    """Return a structured regression report."""

    # Index by (suite, scenario, model)
    def index(runs):
        idx: Dict[str, Dict[str, Any]] = {}
        for r in runs:
            mid = (r.get("manifest") or {}).get("model", {}).get("id") or "default"
            suite = r.get("suite") or (r.get("manifest") or {}).get("suite") or "?"
            agg = aggregate_by_scenario(r.get("results", []))
            avgs = average_scores(r.get("results", []))
            for scenario, info in agg.items():
                key = f"{suite}|{mid}|{scenario}"
                idx[key] = {
                    "scenario": scenario,
                    "suite": suite,
                    "model": mid,
                    "pass_rate": info["verdicts"].get("pass", 0) / max(1, info["runs"]),
                    "n_runs": info["runs"],
                    "n_mech_pass": info["mech_pass"],
                    "n_errored": info["errored"],
                    "avg_scores": avgs,
                }
        return idx

    base_idx = index(baseline_runs)
    curr_idx = index(current_runs)

    all_keys = set(base_idx) | set(curr_idx)
    regressions: List[Dict[str, Any]] = []
    improvements: List[Dict[str, Any]] = []
    new_only: List[Dict[str, Any]] = []
    dropped: List[Dict[str, Any]] = []

    for k in sorted(all_keys):
        b = base_idx.get(k)
        c = curr_idx.get(k)
        if b and not c:
            dropped.append(b)
            continue
        if c and not b:
            new_only.append(c)
            continue

        # Pass-rate change
        pr_delta = c["pass_rate"] - b["pass_rate"]
        if pr_delta <= -pass_rate_drop_threshold:
            regressions.append({
                "key": k,
                "type": "pass_rate_drop",
                "baseline": b["pass_rate"],
                "current": c["pass_rate"],
                "delta": pr_delta,
            })
        elif pr_delta >= pass_rate_drop_threshold:
            improvements.append({
                "key": k,
                "type": "pass_rate_gain",
                "baseline": b["pass_rate"],
                "current": c["pass_rate"],
                "delta": pr_delta,
            })

        # Score changes
        for dim in set(b["avg_scores"]) | set(c["avg_scores"]):
            bv = b["avg_scores"].get(dim)
            cv = c["avg_scores"].get(dim)
            if bv is None or cv is None:
                continue
            d = cv - bv
            if d <= -score_drop_threshold:
                regressions.append({
                    "key": k,
                    "type": f"score_drop:{dim}",
                    "baseline": bv,
                    "current": cv,
                    "delta": d,
                })
            elif d >= score_drop_threshold:
                improvements.append({
                    "key": k,
                    "type": f"score_gain:{dim}",
                    "baseline": bv,
                    "current": cv,
                    "delta": d,
                })

    return {
        "regressions": regressions,
        "improvements": improvements,
        "new_only": new_only,
        "dropped": dropped,
    }


def render_comparison_md(report: Dict[str, Any]) -> str:
    out = ["# Run Comparison Report", ""]
    out.append(f"Regressions: {len(report['regressions'])}")
    out.append(f"Improvements: {len(report['improvements'])}")
    out.append(f"New-only: {len(report['new_only'])}")
    out.append(f"Dropped (baseline-only): {len(report['dropped'])}")
    out.append("")

    if report["regressions"]:
        out.append("## Regressions")
        out.append("")
        out.append("| Where | Type | Baseline | Current | Delta |")
        out.append("|---|---|---|---|---|")
        for r in report["regressions"]:
            out.append(
                f"| {r['key']} | {r['type']} | "
                f"{r['baseline']:.2f} | {r['current']:.2f} | {r['delta']:+.2f} |"
            )
        out.append("")

    if report["improvements"]:
        out.append("## Improvements")
        out.append("")
        out.append("| Where | Type | Baseline | Current | Delta |")
        out.append("|---|---|---|---|---|")
        for r in report["improvements"]:
            out.append(
                f"| {r['key']} | {r['type']} | "
                f"{r['baseline']:.2f} | {r['current']:.2f} | {r['delta']:+.2f} |"
            )
        out.append("")

    if report["new_only"]:
        out.append("## New (no baseline)")
        out.append("")
        for r in report["new_only"]:
            out.append(f"- {r['key']}")
        out.append("")

    if report["dropped"]:
        out.append("## Dropped (baseline only)")
        out.append("")
        for r in report["dropped"]:
            out.append(f"- {r['key']}")
        out.append("")

    return "\n".join(out)


def main() -> int:
    p = argparse.ArgumentParser(description="Compare two evaluation runs.")
    p.add_argument("baseline", help="Baseline run directory")
    p.add_argument("current", help="Current run directory")
    p.add_argument("--output", "-o", help="Output markdown path")
    p.add_argument("--pass-rate-threshold", type=float, default=0.10)
    p.add_argument("--score-threshold", type=float, default=0.5)
    p.add_argument("--mark-baseline", action="store_true",
                   help="Tag the baseline run as the new reference baseline")
    args = p.parse_args()

    base_runs = load(Path(args.baseline).resolve())
    curr_runs = load(Path(args.current).resolve())

    if not base_runs:
        print(f"error: no runs loaded from baseline: {args.baseline}", file=sys.stderr)
        return 2
    if not curr_runs:
        print(f"error: no runs loaded from current: {args.current}", file=sys.stderr)
        return 2

    report = compare_runs(
        base_runs, curr_runs,
        pass_rate_drop_threshold=args.pass_rate_threshold,
        score_drop_threshold=args.score_threshold,
    )

    md = render_comparison_md(report)
    if args.output:
        Path(args.output).write_text(md)
        print(f"# Wrote {args.output}", file=sys.stderr)
    else:
        print(md)

    if args.mark_baseline:
        # Tag baseline by writing a marker file in the run dir
        marker_path = Path(args.baseline).resolve() / "BASELINE"
        if not marker_path.exists():
            marker_path.write_text(
                f"Marked baseline at {__import__('datetime').datetime.utcnow().isoformat()}Z\n"
            )
            print(f"# Marked {args.baseline} as baseline", file=sys.stderr)

    # Exit non-zero if regressions exist
    return 1 if report["regressions"] else 0


if __name__ == "__main__":
    sys.exit(main())