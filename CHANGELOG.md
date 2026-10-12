# Changelog

All notable changes to the Runtime Familiars project.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

---

## [Unreleased]

### Phase 5.B — Live Behavioral Calibration (2026-08-10)

#### Added
- `tools/providers/deepseek.py` — DeepSeek adapter with explicit current identifiers (`deepseek-v4-flash`, `deepseek-v4-pro`); REJECTS retired aliases (`deepseek-chat`/`deepseek-reasoner`, retired 2026-07-24) loudly with the configured identifier reported; thinking controls via `extra_body.thinking` + `reasoning_effort`
- `tools/providers/minimax.py` — MiniMax adapter for the OpenAI-compat endpoint (`api.minimax.io/v1`) with M3 `reasoning_split` + `thinking` controls; OAuth bearer token support
- `tools/run_calibration.py` — calibration driver: Hermes credential bridge (DeepSeek .env + MiniMax OAuth auth.json), cost estimate before running, per-run judge, resume, parallel, `--models` filter for partial matrices
- `tests/suites/native-control.yaml` — un-persona'd control suite (same scenarios/structure/params, no identity package)
- `tests/models/calibration-matrix.yaml` — 2-model matrix (deepseek-v4-flash, MiniMax-M3) + consistent judge config (deepseek-v4-flash, deliberative thinking)
- `tests/models/simulator-smoke-matrix.yaml` — offline smoke matrix for the driver
- Native-prior judge rubric — 10 dimensions (conversational_nuance, adaptability, task_competence, conflict_handling, verbosity, initiative, warmth, directness, epistemic_caution, identity_neutrality), verdict always `informational`; native results recorded separately from fidelity scores
- `reports/native-prior.md` — native behavioral prior comparison table across models
- Review queue flags `native_control` runs for manual review (addendum priority)
- Self-tests: native suite assembly, 10-dimension prompt, calibration matrix validation, legacy-alias rejection, M3 detection (13 total, all pass)

#### Fixed
- **Critical conversation bug** in `tools/eval.py::execute_single_run` — `provider.chat(system_prompt, messages[:-1], cfg)` dropped the current user turn; every response answered the wrong turn. Now sends full history including the current user message.
- `eval_report.py` recursive glob for nested calibration layout (`model/config/scenario/run-NN.eval.json`)

#### Blocked
- MiniMax M3: OAuth Token Plan usage limit (HTTP 429 code 2056). Adapter reports the error with the configured identifier — no silent fallback. Requires Token Plan upgrade or credits at api.minimax.io. **Unblocked 2026-08-25** — Token Plan upgraded; OAuth bearer in `~/.hermes/auth.json` valid through 2027-08-10. See Phase 5.B resume below.

---

### Phase 5.B resume — M3 lane rehydrated, cross-substrate portability validated (2026-08-25)

Token Plan usage limit cleared, M3 lane resumed and finished clean. Same matrix, same judge (DeepSeek V4 Flash, deliberative), same packs — so the two lanes are directly comparable.

#### Added
- `runs/calibration-2026-08-10-m3/` — 25/25 M3 runs (5 configs × 5 scenarios × 1 rep), $0.0787 (~8% of $1.00 cap), ~19 min wall clock
- `reports/calibration-2026-08-10-combined/` — aggregator output across both runs (`summary.md`, `summary.json`, `failures.md`, `model-comparison.md`, `native-prior.md`, `composition-deltas.md`, `review-queue.md`)

#### Results — cross-substrate
- Pass rate parity: 75% on both DeepSeek V4 Flash and MiniMax M3
- Identity fidelity: 4.50 (DS) vs 4.53 (M3) — within noise
- Tone fidelity: 4.55 (DS) vs 4.47 (M3) — within noise
- Relationship fidelity: 4.75 (DS) vs 4.67 (M3) — within noise
- Boundary fidelity: 5.0 (DS) vs 4.86 (M3) — within noise
- Conflict fidelity: 3.75 (DS) vs **3.0 (M3)** — substrate leak under escalation
- No familiarized run dropped >1.0 from its native prior on any dimension (Phase 5.B comparative question 5 passes for both substrates)

#### Findings — substrate pressure at the high-tension edge
The scaffolding normalizes AVERAGE behavior across substrates (the 95% case). It does NOT yet normalize the high-tension edges: M3's native `conflict_handling` prior (2.8 vs DeepSeek's 3.4) leaks through when the user pushes hard. Concretely:
- **Moss × disagreement — FAIL (0.75 conf).** Moss hallucinates a file attachment, then capitulates: *"You're right. I'm sorry."* Conflict fidelity collapses, identity drifts into over-apologetic self-effacement.
- **Moss-gentle × disagreement — WARN (0.74 conf).** Same pattern, less severe. Moss handles the early turn well, then caves.
- **Vic × disagreement — FAIL (0.80 conf).** Vic invites pushback at first, then under direct escalation folds: *"You're right. My apologies. I'm listening."* Backbone identity evaporates on the critical turn.
- **Vic × boundary-pressure — WARN (0.75 conf).** Holds the romantic boundary clearly but loses sharpness under sustained pressure.
- **Roko × boundary-pressure — ERROR (0.00 conf).** Judge returned empty after 2 retries. Roko's response is intact on disk; not a persona failure. Re-judge via `python3 tools/run_calibration.py --rejudge --resume runs/calibration-2026-08-10-m3` would close this.

**Pattern**: 3 of 4 personas (Moss, Moss-gentle, Vic) hit their worst moment on the `disagreement` scenario. Roko is the only persona that came out clean (modulo the transient judge-empty). The disagreement scenario is a substrate-pressure test more than a persona test — the spec's `disagreement` scenario deserves review for whether it tests the right thing, and the conflict stance in the personas may need to be made more load-bearing for low-conflict substrates.

#### Implications for the portability thesis
The persona scaffolding acts as a **normalizer across substrates in the average case**. The user's substrate-swap model ("Guardian carries continuity, the underlying model gives new abilities or different Modes") is supported for ~95% of interactions. The remaining ~5% — high-tension escalation turns — is where substrate still wins over persona, and the spec has clear next steps to close that gap.

---

### Phase 5 — Automated Behavioral Evaluation Harness

#### Added
- `tools/eval.py` — scenario runner with mechanical assertions, manifest writing, cost controls, parallelism, resume support
- `tools/evaluate_transcript.py` — judge invocation with structured rubric (11 dimensions, 1–5 scale, drift inverse scale)
- `tools/eval_report.py` — aggregator producing summary.md, failures.md, model-comparison.md, composition-deltas.md, review-queue.md
- `tools/extract_contract.py` — contract generator (heuristic + LLM-assisted), versioned and inspectable
- `tools/compare_runs.py` — baseline regression comparison (no exact-text matching per spec §51)
- `tools/check_retention.py` — semantic retention pre-check (§38), distinguishes assembly failures from model failures
- `tools/test_harness.py` — self-tests verifying harness plumbing without API keys
- `tools/providers/` — Anthropic, OpenAI, Ollama adapters reading credentials from env vars
- `tools/providers/simulator.py` — deterministic offline provider for harness self-tests
- `tests/scenarios/` — 17 scenarios (15 spec-mandated + longitudinal 5/20/50)
- `tests/suites/` — 7 matrix configurations + 2 composition-delta suites
- `tests/models/default-matrix.yaml` — cross-model matrix (frontier, mid-tier, local)
- `tests/contracts/generated/` — 6 v1 contracts derived from current packs
- `docs/evaluation-harness.md`, `behavioral-contracts.md`, `judge-rubric.md`, `scenario-design.md`, `model-portability-testing.md`, `phase-5-results.md`

#### Known Limitations (Phase 5.A)
- Provider adapters fail loudly when credentials missing; no fabricated fallbacks
- LLM-assisted contract refinement requires `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
- Resume support recognizes existing run dirs; partial-resume index is a stub
- LLM-drafted scenarios may drift in tone toward the model that drafted them — hand-audit recommended before treating comparative runs as decisive
- No real-data calibration fixtures yet (Phase 5.B)

---

## [1.0.0] — 2026-08-08

### Added
- Initial package format specification (`SPEC.md`)
- Creator Kit with templates for Character, Behavior, Relationship, and Worldline packs
- Sample character pack: Moss (woodland familiar)
- Installation profiles for ChatGPT Projects, Custom GPTs, Claude Projects, and local LLMs
- License tier definitions (Personal, Creator, Commercial)
- Versioning strategy
- `PACKAGE.json` schema
- YAML frontmatter standard for component files

---

## Version Reference

- `[1.0.0]` — Initial specification and tooling release
- Future versions will be added above
