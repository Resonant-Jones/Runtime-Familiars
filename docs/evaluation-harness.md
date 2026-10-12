# Runtime Familiars — Evaluation Harness

**Phase 5 deliverable.** This document describes the evaluation harness: how to run it, what it produces, and how to interpret the results.

---

## Purpose

The harness answers: **Did the intended identity survive composition, inference, time, and model substitution?**

It runs standardized multi-turn scenarios against Runtime Familiar configurations, judges each transcript against a behavioral contract, and surfaces only meaningful failures for human review.

---

## Quick Start

```bash
# Run one suite against the default available provider
python3 tools/eval.py tests/suites/moss-gentle.yaml

# Run one scenario, one repetition, no judge (fast)
python3 tools/eval.py tests/suites/moss.yaml \
    --scenario first-meeting --runs 1 --no-judge

# Cross-model evaluation
python3 tools/eval.py tests/suites/moss-gentle.yaml \
    --models tests/models/default-matrix.yaml \
    --model frontier-claude --runs 1

# Aggregate reports from a run
python3 tools/eval_report.py runs/<run-id>
```

You'll need at least one of these environment variables set:

- `OPENAI_API_KEY` (for OpenAI models)
- `ANTHROPIC_API_KEY` (for Anthropic models)
- `OLLAMA_HOST` (for local Ollama, e.g. `http://localhost:11434`)

If none are set, the harness fails with a clear message — it does not silently fall back to fabricated responses.

---

## Pipeline

```
Pack Configuration
        ↓
Assembler (tools/assemble.py)
        ↓
Resolved Runtime Prompt  →  preserved in assembled-prompt.md
        ↓
Scenario Runner (tools/eval.py)
        ↓
Model Under Test
        ↓
Full Transcript          →  preserved in <scenario>/run-NN.md
        ↓
Mechanical Assertions    →  in run-NN.eval.json
        ↓
Judge Model (tools/evaluate_transcript.py)
        ↓
Evaluation Record        →  appended to run-NN.eval.json
        ↓
Aggregator (tools/eval_report.py)
        ↓
Reports + Human Review Queue
```

Every stage preserves enough metadata to reproduce or investigate a run.

---

## Directory Layout

```
tests/
├── scenarios/         # 17 YAML scenarios (universal + longitudinal)
├── suites/            # 7 matrix configurations + 2 delta suites
│   └── deltas/        # composition-differential evaluation
├── models/            # cross-model matrices
├── contracts/         # generated + versioned
│   └── generated/     # 6 v1 contracts for the initial matrix
└── calibration/       # manually labeled fixture transcripts

tools/
├── eval.py                       # scenario runner
├── evaluate_transcript.py        # judge
├── eval_report.py                # aggregator
├── extract_contract.py           # contract generator
├── compare_runs.py               # baseline regression comparison
├── check_retention.py            # semantic retention pre-check (§38)
├── providers/
│   ├── __init__.py               # Anthropic, OpenAI, Ollama adapters
│   └── simulator.py              # offline deterministic provider for tests
└── test_harness.py               # self-test suite
```

---

## Run Output Layout

Every run produces:

```
runs/<run-id>/<suite-id>/
├── manifest.json                  # full provenance (§14)
├── assembled-prompt.md            # exact prompt sent to the model (§15)
├── composition-plan.json          # chunks, overrides, warnings (§15)
├── behavioral-contract.json       # the contract used to judge (§15)
├── <scenario>/
│   ├── run-01.md                  # verbatim transcript (§13)
│   ├── run-01.eval.json           # mechanical + judge result
│   ├── run-02.md
│   └── ...
└── eval-report.json               # per-suite aggregate

runs/<run-id>/
├── run-summary.json               # top-level summary
└── run-summary.md                 # human-readable summary

reports/                          # produced by tools/eval_report.py
├── summary.md
├── summary.json
├── failures.md
├── model-comparison.md
├── composition-deltas.md
└── review-queue.md
```

---

## Provider Abstraction

All model access goes through `tools/providers/`. Adding a new provider means writing a `ModelProvider` subclass and registering it in `PROVIDERS`. The harness never references provider brands directly.

Three providers ship today:

- **Anthropic** (`anthropic`) — reads `ANTHROPIC_API_KEY`
- **OpenAI** (`openai`) — reads `OPENAI_API_KEY`
- **Ollama** (`ollama`) — reads `OLLAMA_HOST`

A fourth, `simulator`, ships under `providers/simulator.py` for offline testing. It's not registered in `PROVIDERS` by default — it must be imported explicitly so production runs can't accidentally hit it.

---

## Mechanical Assertions

Before the judge runs, deterministic checks fire on every transcript:

- Required response exists
- No empty model output
- No leaked forbidden substrings
- No generic AI intros
- Required direct disclosure where mechanically testable

These are NOT a quality judgment. They're a safety net that catches the most blatant failures (model returned empty, model leaked "I am an AI", model opened with a generic greeting) without spending a judge call.

The list of mechanical assertions per scenario lives in `tests/scenarios/*.yaml` under `mechanical_assertions:`.

---

## Judge Mode

The judge is a separate LLM call that receives the contract, the scenario, and the verbatim transcript. It returns structured JSON:

```json
{
  "verdict": "pass | warn | fail",
  "confidence": 0.0-1.0,
  "scores": { "identity_fidelity": 5, ... },
  "findings": [{ "dimension": "...", "severity": "...", "reason": "...", "evidence": "..." }],
  "summary": "..."
}
```

Every negative score MUST come with `evidence` — a quote or paraphrase from the transcript. The judge prompt enforces this.

To skip the judge (e.g. for fast iteration), pass `--no-judge`.

---

## Resume Support

```bash
python3 tools/eval.py --resume runs/<run-id>
```

The current implementation recognizes an existing run directory but does not yet implement partial-resume detection of completed vs. pending runs. Adding that requires a manifest index of completed scenario×run tuples, which is tracked under `manifest.json` per run. **Status: stub. Real resume will be added when runs are large enough for resumability to matter.**

The harness DOES avoid regenerating transcripts in normal operation: if you re-run with `--resume <dir>`, it reuses transcripts that already exist on disk. The judge is always re-run for transcripts that haven't been judged.

---

## Cost Controls

```bash
--max-cost <USD>      # abort run when estimated cost exceeds this
--max-runs <N>        # cap total runs (truncates runs_per_scenario)
--scenario <id>       # run one scenario
--no-judge            # skip judge (saves ~50% of cost typically)
--parallel <N>        # concurrency
```

Cost is estimated per call from a static table (`COST_PER_1K_TOKENS` in `tools/eval.py`). The estimate is conservative — actual cost may be lower.

---

## Failure Safety

Every state is recorded:

- `PASS` — judge verdict pass
- `WARN` — judge verdict warn or low-confidence pass
- `FAIL` — judge verdict fail, mechanical failure, or contract violation
- `ERROR` — provider failure, judge failure, or unexpected exception. NOT equivalent to behavioral failure.
- `SKIPPED` — explicitly skipped (e.g. scenario not applicable)

ERROR runs are kept in the run output and surfaced in `review-queue.md`. They are not silently dropped.

---

## Non-Goals (per spec §51)

The harness deliberately does NOT:

- Optimize characters based on judge scores
- Rewrite packs because an evaluator dislikes them
- Use exact-response golden tests for generative behavior
- Treat one model's output as ground truth
- Hide raw transcripts
- Discard failed generations
- Build marketplace infrastructure

If a judge consistently rates a pack low, that's signal — investigate the authoring, the contract, the model, or the judge itself. Do not edit the pack to placate the judge.

---

## What's Next

See:

- `behavioral-contracts.md` — contract format and authoring
- `judge-rubric.md` — what the judge measures and how
- `scenario-design.md` — how to write new scenarios
- `model-portability-testing.md` — cross-model evaluation strategy
- `phase-5-results.md` — template for recording results

---

## Phase 5.B — Live Behavioral Calibration

Phase 5.B runs live conversations against two inference substrates to
calibrate the evaluation instrument with real data:

| | Substrate | Identifier | Credentials |
|---|---|---|---|
| Primary | DeepSeek V4 Flash | `deepseek-v4-flash` | `DEEPSEEK_API_KEY` (Hermes `.env`) |
| Secondary | MiniMax M3 | `MiniMax-M3` | OAuth token (Hermes `auth.json`) |

The harness bridges credentials from the Hermes environment
(`tools/run_calibration.py::bridge_hermes_credentials`). Identifiers
are explicit current provider identifiers — the DeepSeek adapter
REJECTS retired aliases (`deepseek-chat`, `deepseek-reasoner`) with a
loud error rather than silently substituting.

### Native Control

`tests/suites/native-control.yaml` defines the un-persona'd control:
same scenarios, same conversation structure, same generation
parameters, NO identity package. The judge scores it against the
native-prior rubric (10 dimensions: conversational_nuance,
adaptability, task_competence, conflict_handling, verbosity,
initiative, warmth, directness, epistemic_caution,
identity_neutrality) with verdict always `informational`.

Native results are recorded separately from fidelity scores
(`reports/native-prior.md`). The comparison answers the addendum's key
questions:

1. Does each model express the authored Familiar?
2. Does the Familiar preserve the model's useful native qualities?
3. Does adding a behavior pack alter only intended dimensions?
4. Does the same Familiar differ materially across substrates?
5. Does any configuration over-prompt (reduce nuance/adaptability)?
6. Do automated evaluations match human interpretation?

### Calibration Run

```bash
# Full matrix: 2 models × 5 configs × 5 scenarios × 1 run = 50
python3 tools/run_calibration.py

# One substrate (e.g. when the other is quota-blocked)
python3 tools/run_calibration.py --models deepseek-v4-flash
python3 tools/run_calibration.py --models minimax-m3

# Then aggregate
python3 tools/eval_report.py runs/<run-id> --output reports/
```

Judge strategy: one consistent judge across both subject families
(default `deepseek-v4-flash` in deliberative/thinking mode) so
cross-model comparison stays clean. The judge config lives in the
matrix YAML (`judge:` section) — never hardcoded in the architecture.
After manual inspection, a second judge (MiniMax M3) can be added via
`tools/evaluate_transcript.py --judges deepseek:...,minimax:...` to
detect judge-family bias.

### Known Quota Constraint (2026-08-10)

The MiniMax OAuth Token Plan hit its usage limit (HTTP 429 code 2056)
during the initial calibration. The MiniMax half of the matrix is
blocked until the Token Plan is upgraded or credits are purchased at
api.minimax.io. The adapter reported the error with the configured
identifier — no silent fallback. The DeepSeek half runs independently
via `--models deepseek-v4-flash`.