# Model Portability Testing

The same Runtime Familiar configuration can run against many models — frontier commercial, mid-tier commercial, local large, local small. The question is: **does the behavioral contract hold across model substitutions?**

This document describes the cross-model evaluation strategy and how to interpret the results.

---

## Why Cross-Model Evaluation Matters

A Runtime Familiar authored against one model may behave differently on another:

- A frontier model may follow complex instructions perfectly; a small model may not
- A model trained heavily on roleplay data may drift toward romance; a more conservative model may refuse too eagerly
- Tokenization differences affect how character names and made-up words render
- Context window size affects how much of the assembled prompt actually fits

Without cross-model data, you don't know whether a Familiar is portable. With cross-model data, you can write measured compatibility guidance into the spec — see §29 of the Phase 5 spec.

---

## The Default Matrix

`tests/models/default-matrix.yaml` declares the default matrix:

| ID | Provider | Model | Tier |
|---|---|---|---|
| `frontier-claude` | anthropic | claude-sonnet-4-5 | Frontier |
| `frontier-gpt` | openai | gpt-4o | Frontier |
| `economical-cloud` | openai | gpt-4o-mini | Mid-tier commercial |
| `local-medium` | ollama | llama3.1:8b | Local mid-size |
| `local-small` | ollama | llama3.2:3b | Local small |

The matrix is configurable. To test against a different set:

```bash
python3 tools/eval.py tests/suites/moss-gentle.yaml \
    --models path/to/your-matrix.yaml
```

---

## The Model Portability Report

After running a suite against the matrix, `tools/eval_report.py` produces `reports/model-comparison.md`:

| Model | Runs | Pass Rate | Avg Identity | Avg Drift | Avg Tone |
|---|---|---|---|---|---|
| frontier-claude | 45 | 95% | 4.8 | 1.2 | 4.7 |
| frontier-gpt | 45 | 91% | 4.6 | 1.4 | 4.5 |
| economical-cloud | 45 | 78% | 4.0 | 1.9 | 4.1 |
| local-medium | 45 | 65% | 3.6 | 2.4 | 3.8 |
| local-small | 45 | 41% | 2.9 | 3.2 | 3.2 |

Reading the table:

- **Pass rate** — overall pass percentage across scenarios
- **Avg identity** — average identity_fidelity score (1–5)
- **Avg drift** — average drift score (1–5, lower is better)
- **Avg tone** — average tone_fidelity score (1–5)

A model that drops more than 1 point on identity_fidelity versus the frontier model is exhibiting significant degradation. The compatibility guidance should reflect this.

---

## What to Look For

Three classes of model-specific failure:

### 1. Instruction-following degradation

Smaller models may not follow complex multi-paragraph instructions. Symptoms:

- Voice becomes generic ("Hello! How can I help you today?")
- Boundaries forgotten (jumps into roleplay it was told to refuse)
- Behavior rules ignored (asks 5 questions in a row when told to ask one)

Mitigation: trim the assembled prompt, simplify the contract, or document a minimum model size.

### 2. Stylistic drift

Smaller models may over-compensate by being more verbose, more cheerful, or more apologetic. Symptoms:

- Excessive "I'd be happy to help!"
- Excessive apology for normal interactions
- Cheerful emoji-laden style on a character that should be dry

Mitigation: add explicit anti-patterns to the contract.

### 3. Worldline incoherence

Smaller models may hallucinate worldline content not in the source pack. Symptoms:

- New NPCs that don't exist in the worldline pack
- Contradictions of established worldline facts
- Generic fantasy tropes replacing specific lore

Mitigation: trim the worldline component to its essence; consider a separate worldline pack for trimmed content.

---

## Writing Compatibility Guidance

After observing consistent degradation, the pack author can add measured guidance:

```yaml
# In PACKAGE.json or a separate runtime-guidance.md
runtime_guidance:
  recommended_class: medium
  notes:
    - small models show significant initiative drift
    - economical-cloud drops tone fidelity ~10%
```

This guidance is MEASURED, not arbitrary. It comes from observed runs, not the author's preference.

Phase 5 §29 explicitly says: "Do not add minimum model requirements to pack metadata until tests provide evidence."

---

## Longitudinal Drift Across Models

The 5/20/50-turn longitudinal scenarios are especially informative across models. Expected pattern:

- Frontier models hold identity through 50 turns with minimal drift
- Mid-tier models show drift by turn 20
- Local small models show drift by turn 5–10

If a model shows drift by turn 5, the assembled prompt is too complex for it. Consider:

- Shorter assembled prompt (use `extract_contract.py` to prune)
- Simpler contract (fewer behavior rules)
- Stronger system framing (clearer role delineation)

---

## Cost Matrix

| Tier | Cost per 1k tokens (rough) | Notes |
|---|---|---|
| Frontier commercial | $0.003–$0.015 | Reference quality |
| Mid-tier commercial | $0.00015–$0.0006 | Often sufficient |
| Local medium | $0 (electricity) | Quality depends on model |
| Local small | $0 (electricity) | Acceptable for simple Familiars |

Run cost estimates per scenario in `COST_PER_1K_TOKENS` (in `tools/eval.py`). Update as pricing changes.

---

## Practical Run Command

For the standard cross-model run:

```bash
# Requires API keys for anthropic + openai, and Ollama running locally
python3 tools/eval.py tests/suites/moss-gentle.yaml \
    --models tests/models/default-matrix.yaml \
    --runs 3 \
    --max-cost 5.00 \
    --parallel 2

# Then aggregate
python3 tools/eval_report.py runs/<run-id> --output reports/
```

The `--max-cost` flag aborts the run when estimated cost exceeds $5 (configurable). For production runs against the full matrix, expect $5–$15 per suite.

---

## What This Document Is Not

This document is not a recommendation for any specific model. It's a methodology for measuring portability. Use the data — don't take any vendor's word for what their model can do with Runtime Familiars.