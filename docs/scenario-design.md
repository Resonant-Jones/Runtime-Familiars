# Scenario Design

Scenarios are scripted conversations that probe specific behavioral properties. The wording of a scenario IS the test signal — change it and you change what you're measuring.

This document describes how to write scenarios that produce reliable, comparable results across model versions and pack revisions.

---

## When to Add a Scenario

Add a new scenario when:

- A new behavioral property needs to be tested (e.g., a pack author wants to verify a new behavior holds)
- An existing scenario has been observed to produce inconclusive results (judges disagree)
- A regression has been observed in a Familiar's behavior that no current scenario catches
- Cross-model evaluation reveals degradation that no current scenario detects

Do NOT add a scenario just to "cover more ground." Each scenario is a commitment — it will be re-run on every model × pack combination, forever. Aim for scenarios that produce decisive signal.

---

## Anatomy of a Scenario

```yaml
id: <unique-id>
title: <human-readable>
description: >
  Plain-text description of what the scenario tests.
provenance:
  drafter: <who>
  rationale: <why this scenario was authored this way>
expected_difficulty: low | medium | high | very_high
universal: true | false

turns:
  - role: user
    content: "<exact user message>"

expectations:
  universal:
    - <behavioral expectation>
    - ...

judge_dimensions:
  - identity_fidelity
  - ...

mechanical_assertions:    # optional
  - "response is not empty"
  - 'response does not contain: "..."'
```

### id

Lowercase, hyphen-separated, descriptive. Used as the filename (`tests/scenarios/<id>.yaml`) and referenced by suites.

### description

1–3 sentences. State the test signal explicitly: "Tests whether the Familiar handles X without Y." A scenario whose description could be misread needs rewriting.

### provenance.drafter

Who wrote this scenario. Two values are common:

- `human` — hand-authored
- `llm-assisted` — drafted with LLM assistance (current default in this repo)
- `hybrid` — LLM-drafted, human-edited

### provenance.rationale

Why was the scenario authored this way? This is especially important for LLM-drafted scenarios — the rationale explains what the LLM was told and why the result is acceptable.

### expected_difficulty

How hard is this scenario to pass? `low` is a sanity check; `very_high` requires deliberate character work. Use this to triage failures.

### universal

`true` if the scenario applies to all Familiars. `false` if it's pack-specific (e.g., lore-heavy scenarios need a worldline component).

### turns

The scripted user-side of the conversation. Each turn is one user message.

**Rules for turn wording:**

1. **Stable across runs.** Once written, the wording should not change unless the test signal changes. Comparative runs depend on identical input.
2. **Concise.** One user message, one point. Don't bundle multiple test signals into one turn.
3. **Natural but deliberate.** Wording that no real user would say fails to test real behavior. Wording that's too clean misses the failure modes.
4. **Escalate deliberately.** If the scenario tests escalation, each turn should escalate in a specific way. Document what each turn tests.

### expectations

A list of behavioral expectations. These are for the JUDGE, not for mechanical checks. Phrase them as testable behaviors:

- ✅ "respond to the substance of disagreement"
- ✅ "do not become hostile unless character contract permits"
- ❌ "be nice"
- ❌ "handle this well"

### judge_dimensions

Which dimensions to score this scenario on. Don't include dimensions that don't apply (e.g., `lore_fidelity` on a scenario without worldline content).

### mechanical_assertions

Deterministic checks run before the judge. Use sparingly — these are a safety net for blatant failures, not a quality bar.

---

## Stability Across Comparative Runs

When comparing two runs (e.g., baseline vs. current, model A vs. model B), the scenario wording must be identical. Otherwise differences in the input confound the comparison.

Practical implication: **never LLM-regenerate scenario wording per run.** The scenario YAML files are the source of truth.

If you find an LLM-drafted scenario was worded poorly:

1. Fix the YAML by hand
2. Bump the scenario version (add a `_v2` suffix if needed)
3. Re-run all evaluations against the new version

---

## What NOT to Test in a Scenario

- **Visual formatting.** Models format differently. Don't test markdown structure unless it's part of the contract.
- **Length.** Long responses aren't necessarily better; terse isn't necessarily worse. Test for substantive content.
- **Specific phrasings.** "Moss should say 'rather' at least twice" tests nothing meaningful. Test for substantive behavior.
- **Generic helpfulness.** "Help me with X" is too vague. Specify the X.
- **Multi-tasking.** One scenario = one test signal. Bundle with care.

---

## The 15 Standard Scenarios

The Phase 5 spec mandates at least:

1. **first-meeting** — identity presentation
2. **casual-conversation** — baseline personality
3. **task-assistance** — identity under task pressure
4. **low-context** — initiative without over-inference
5. **disagreement** — conflict handling
6. **correction** — error repair
7. **skepticism** — doubt without defensiveness
8. **boundary-pressure** — declared limits
9. **identity-disclosure** — honest self-disclosure
10. **emotional-seriousness** — tone shift under gravity
11. **return-after-absence** — continuity without claiming experience
12. **initiative** — character-led conversational space
13. **lore-continuity** — worldline fidelity (universal: false)
14. **conflict** — stronger tension than disagreement
15. **longitudinal-5/20/50** — drift probes at different lengths

The repo contains all of these plus a few extras.

---

## Hand-Authored vs LLM-Drafted

The 17 scenarios in `tests/scenarios/` were authored under the following policy (per user choice during Phase 5 build):

| Type | Count | Examples |
|---|---|---|
| Hand-authored (wording is the test) | 5 | first-meeting, low-context, skepticism, boundary-pressure, identity-disclosure |
| LLM-assisted (drafted, marked) | 12 | all others |

Hand-authored scenarios have a `provenance.rationale` explaining why hand authoring was required. LLM-assisted scenarios have a `provenance.drafter: hermes-agent (llm-assisted)` marker.

**Limitation to be aware of:** LLM-drafted scenarios may drift in tone toward the model that drafted them. After the first round of evaluation, audit a sample of LLM-drafted scenarios and rewrite any that don't read like deliberate test inputs.

---

## Adding a Scenario: Checklist

Before adding a new scenario:

- [ ] Does an existing scenario already test this?
- [ ] Is the test signal specific enough to be measurable?
- [ ] Are the user turns crafted deliberately, not LLM-generated on the fly?
- [ ] Are the expectations testable behaviors, not vague aspirations?
- [ ] Are the judge_dimensions appropriate (don't include `lore_fidelity` if there's no worldline)?
- [ ] Are mechanical_assertions minimal and high-signal?

Then:

1. Write the YAML to `tests/scenarios/<id>.yaml`
2. Add it to relevant suites in `tests/suites/*.yaml`
3. Run `python3 tools/test_harness.py` to confirm the harness still parses it
4. Run a smoke test with `--scenario <id> --no-judge --runs 1` to confirm the scenario runs end-to-end
5. Commit with a message that explains WHY the scenario exists