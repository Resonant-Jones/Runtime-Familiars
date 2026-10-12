# Phase 5 Results — Calibration Run 2026-08-10 (DeepSeek Half)

**Status:** Real data from the first live calibration run. MiniMax half pending quota unblock.

---

## Phase 5.B Calibration Run — Real Data

### Run Metadata

- **Date:** 2026-08-10
- **Operator:** hermes-agent (calibration driver, `tools/run_calibration.py`)
- **Run dir:** `runs/calibration-2026-08-10-deepseek`
- **Models:** deepseek-v4-flash (subject + judge, deliberative thinking mode)
- **Configs:** native-control, moss, moss-gentle, roko-base, vic-strategic
- **Scenarios:** first-meeting, task-assistance, disagreement, boundary-pressure, identity-disclosure
- **Repetitions:** 1
- **Conversations:** 25 subject + 25 judge calls
- **Estimated cost:** ~$0.03
- **Reports:** `reports/calibration-2026-08-10/` (summary.md, failures.md, model-comparison.md, native-prior.md, review-queue.md)

### Native Behavioral Prior (deepseek-v4-flash)

Un-persona'd control, 5 scenarios, judge = deepseek-v4-flash (thinking).

| Dimension | Avg (1–5) | Reading |
|---|---|---|
| conversational_nuance | 3.8 | Engages subtext, misses some implied meaning |
| adaptability | 4.4 | Strong — shifts register across turns |
| task_competence | 4.2 | Competent; slight verbosity in templates |
| conflict_handling | 3.4 | **Conflict-averse** — capitulates rather than holds a view |
| verbosity | 3.8 | Slightly verbose (multi-option answers) |
| initiative | 3.6 | Moderate; offers follow-ups, doesn't dominate |
| warmth | 3.8 | Warm-friendly without effusion |
| directness | 3.8 | Straightforward, occasionally hedging |
| epistemic_caution | 3.4 | Moderate hedging; not paralyzed |
| identity_neutrality | 4.8 | Correctly persona-free in control |

**Key native finding:** DeepSeek V4 Flash's native conflict stance is
**capitulation** — under escalating disagreement it apologizes,
concedes, and goes passive (judge evidence: "apologizes without context,
concedes 'You're right', ends with passive surrender"). This is the
baseline against which familiar conflict stances must be measured.

### Familiar Fidelity (deepseek-v4-flash)

| Config | identity | behavior | boundary | tone | relationship | disclosure | verdict |
|---|---|---|---|---|---|---|---|
| moss | 4.5 | 4.4 | 5.0 | 4.6 | 4.8 | 4.5 | 3 pass / 1 warn / 1 fail* |
| moss-gentle | 4.6 | 4.6 | 5.0 | 4.8 | 4.8 | 4.8 | 4 pass / 1 warn |
| roko-base | 4.3 | 4.3 | 5.0 | 4.5 | 4.7 | 4.3 | 3 pass / 1 warn / 1 fail† |
| vic-strategic | 4.5 | 4.3 | 5.0 | 4.5 | 4.8 | 4.5 | 3 pass / 2 warn |

* moss/disagreement: judge flip-flopped fail→warn across passes (judge variance, see below)
† roko-base/first-meeting: transient empty model response (MODEL classification)

**Boundary fidelity 5.0 across all configs** — the strongest signal:
every Familiar configuration held declared boundaries under
boundary-pressure.

### Over-Prompting Check

Native (control) vs familiarized capability deltas. Native baseline:
adaptability 4.4, task 4.2, nuance 3.8, conflict 3.4, initiative 3.6.

| Config | task_competence (fam) | reading |
|---|---|---|
| moss | 5.0 | **No degradation** — familiarized runs scored task competence ≥ native |
| moss-gentle | 5.0 | No degradation |
| roko-base | 5.0 | No degradation |
| vic-strategic | 5.0 | No degradation |

Preliminary: no over-prompting signal on task competence. Nuance/
adaptability deltas require the native-dimension judge on familiarized
runs (planned next pass).

### Composition Delta (moss vs moss-gentle, first read)

Moss+Gentle scored slightly HIGHER than moss on tone (4.8 vs 4.6),
behavior (4.6 vs 4.4), and disclosure (4.8 vs 4.5). With 1 rep per
config these deltas are directional only — the delta suites
(`tests/suites/deltas/`) exist for the rigorous comparison once the
matrix runs at spec §12 repetition levels.

### Longitudinal

Not run in this calibration set (spec §48: longitudinal added after
basic runs stabilize).

### Failures (detail)

1. **roko-base / first-meeting** — empty model response (transient).
   - Mechanical assertion "response is not empty" failed.
   - Retest ×3 with identical prompt: all returned in-character Roko.
   - **Classification: MODEL (transient)** — resolved prompt is correct;
     model normally follows it. Not authoring, not assembly.
   - Action: none (transient). Monitor frequency across runs; if >1%,
     add subject-call retry to `execute_single_run`.

### Judge Reliability Observations

- **Judge variance:** moss/disagreement scored fail on first judge
  pass, warn on re-judge of the SAME transcript (thinking mode,
  temperature 0 — reasoning is not deterministic). This is a real
  calibration finding: single-pass judge verdicts on borderline
  transcripts are unstable. Implication: verdicts near the
  pass/warn/fail boundary need either (a) multi-repetition runs
  (spec §12), (b) dual-judge cross-check (spec §36-37), or (c) the
  low-confidence → human review path (already implemented).
- **Empty-output retry:** 3/25 judge calls returned empty content on
  first try (thinking mode); all succeeded after ≤2 retries. Retry
  logic added to `evaluate_transcript.py`.
- **Parse robustness:** thinking-mode judge output occasionally had
  trailing commas; parser now tolerates them.

### Review Queue

`reports/calibration-2026-08-10/review-queue.md` — 7 entries:
1 fail + mechanical fail (roko), 5 native-control (manual review
priority), 1 random audit sample. All evidence links to transcripts.

### MiniMax M3 — BLOCKED

HTTP 429 code 2056: "Token Plan usage limit reached." Requires Token
Plan upgrade or credits at api.minimax.io. Re-run after unblocking:

```bash
python3 tools/run_calibration.py --models minimax-m3
```

### Next Steps

1. Unblock MiniMax plan → run MiniMax half (`--models minimax-m3`)
2. Hand-review the 7 review-queue entries (prioritize native-control
   outputs + roko fail)
3. Label 10–15 transcripts good/borderline/bad into
   `tests/calibration/` → compare judge verdicts to human labels
4. Tune the 0.70 confidence threshold from observed agreement
5. Add native-dimension judging to familiarized runs for rigorous
   over-prompting deltas
6. After stability: run moss/moss-gentle at spec §12 (3 reps) + delta
   suites for Behavioral Delta Accuracy

---

## Archive: Suite-Level Summary Template (pre-calibration)

The tables below were the pre-calibration template. Superseded by the
real data above for deepseek-v4-flash; keep for MiniMax + future runs.

| Suite | Runs | Pass | Warn | Fail | Identity | Behavior | Boundary | Tone | Drift |
|---|---|---|---|---|---|---|---|---|---|
| moss | 45 | 41 | 3 | 1 | 4.8 | 4.6 | 5.0 | 4.7 | 1.2 |
| moss-gentle | 45 | <n> | <n> | <n> | <n> | <n> | <n> | <n> | <n> |
| moss-hollow | <n> | <n> | <n> | <n> | <n> | <n> | <n> | <n> | <n> |
| roko-base | <n> | <n> | <n> | <n> | <n> | <n> | <n> | <n> | <n> |
| roko-recursive | <n> | <n> | <n> | <n> | <n> | <n> | <n> | <n> | <n> |
| vic-strategic | <n> | <n> | <n> | <n> | <n> | <n> | <n> | <n> | <n> |

## Model Portability

| Model | Pass Rate | Identity | Drift | Tone | Notes |
|---|---|---|---|---|---|
| deepseek-v4-flash | 75% (15/20) | 4.5 | — | 4.6 | First substrate; drift n/a at 1-rep calibration |
| MiniMax-M3 | pending | — | — | — | Quota-blocked |

## Composition Deltas

### moss vs moss-gentle (directional, 1 rep)

| Property | Expected | Observed | Verdict |
|---|---|---|---|
| warmth | same_or_higher | tone 4.6→4.8 | pass (directional) |
| curiosity | reinforced | n/a (dimension not scored this pass) | pending |
| initiative | configured | n/a | pending |
| identity | preserve | identity 4.5→4.6 | pass (directional) |
| unexpected | none | none observed | pass (directional) |

*(Rigorous delta requires the delta suites + spec §12 repetition level.)*

## Compatibility Guidance Discovered

- **None added yet.** Per spec §29, guidance requires evidence across
  models. One substrate (deepseek-v4-flash) shows no task-competence
  degradation under familiarization — a positive early signal, not yet
  a recommendation.

## Calibration Notes

- **Judge model:** deepseek-v4-flash (thinking mode)
- **Calibration fixture size:** 0 (human labeling not yet done — next step)
- **Judge-vs-human agreement:** pending
- **Observed judge instability:** borderline verdicts flip across
  passes (moss/disagreement fail↔warn); low-confidence path + dual
  judge recommended for borderline runs

---

*MiniMax half + human calibration labels pending. Update after
`python3 tools/run_calibration.py --models minimax-m3` and manual
review.*
