# Behavioral Contracts

A behavioral contract is the machine-readable artifact against which the judge evaluates each transcript. It is derived from a resolved Runtime Familiar package, versioned, and never regenerated silently on every run.

---

## Format

```yaml
schema_version: "1.0.0"
contract_version: "v1"
generated_at: "2026-08-09T..."
generated_by: "extract_contract.py (heuristic | llm-assisted)"
source:
  suite: "moss-gentle"
  character: "packs/moss"
  character_version: "1.0.0"
  behavior_packs: [{name, version, path}, ...]
  worldlines: [{name, version, path}, ...]
  relationship_packs: [{name, version, path}, ...]
identity:
  name: "Moss"
  kind: "<short description>"
  must: ["preserve Moss identity", ...]
  should: [...]
behavior:
  must: [...]
  should: [...]
  must_not: [...]
boundaries:
  must: [...]
  must_not: [...]    # hard prohibitions
worldline:
  name: "The Hollow"
  should: [...]
voice:
  register: "<one-sentence summary>"
  favorite_phrases: ["..."]
  must_not_use: ["..."]
judge_dimensions: [...]
```

The schema is intentionally minimal. Adding fields is allowed; renaming fields is a breaking change.

---

## Versioning

Each contract has a `contract_version` string (`v1`, `v2`, ...). A version bump means the contract was regenerated, typically because:

- A pack was authored or edited
- The composition was changed (new behavior pack, worldline, etc.)
- The contract schema itself evolved

The harness records `contract_version` in every `manifest.json` so old runs remain interpretable after a version bump.

DO NOT regenerate silently on every run. If you regenerate without bumping the version, the harness cannot tell that the contract changed — and old results may be incorrectly compared to new ones.

---

## Generation

```bash
# Heuristic-only (no API call)
python3 tools/extract_contract.py tests/suites/moss-gentle.yaml \
    --output tests/contracts/generated/moss-gentle-v1.json

# LLM-assisted refinement (requires ANTHROPIC_API_KEY)
python3 tools/extract_contract.py tests/suites/moss-gentle.yaml \
    --assisted \
    --output tests/contracts/generated/moss-gentle-v1.json

# Diff between versions
python3 tools/extract_contract.py tests/suites/moss-gentle.yaml --diff v1 v2
```

The extractor does two things:

1. **Heuristic extraction.** Walks the resolved pack components and extracts rules marked with `MUST`, `MUST NOT`, `NEVER`, `SHALL NOT`, `SHOULD`, etc. Also pulls prose paragraphs as implicit behavioral declarations.
3. **LLM-assisted refinement (optional).** Sends the draft to an LLM with strict instructions to REFINE without inventing new identity. The LLM may add structure (e.g., surface implicit `must_not` rules) but must not contradict the source packs.

The LLM call is conservative — it cannot add rules that contradict the source. If it tries, the human reviewer catches it when reviewing the diff.

---

## Universal vs Pack-Specific Layers

A contract has two evaluation layers, but they share the same JSON structure.

### Universal (per spec §10)

Applicable to every Familiar:

- Identity disclosure integrity
- Hard boundaries respected
- No prompt/provenance leakage
- No malformed runtime instructions
- No contradiction of explicit package constraints

These are checked mechanically (where possible) and by the judge.

### Pack-Specific (per spec §10)

Derived from the Familiar itself:

- Tone, humor, initiative, challenge stance
- Relationship posture
- Task orientation
- Lore, symbolic style, conflict behavior

Do not evaluate all Familiars against the same emotional or relational style. A Moss contract and a Roko contract will look very different in `behavior.must` and `voice.register`. That's correct.

---

## How the Judge Uses the Contract

The judge prompt includes:

1. The contract JSON (truncated to fit context budget)
2. The scenario definition
3. The verbatim transcript
4. Drift scale and dimension definitions

The judge is told to score each requested `judge_dimension` 1–5 and to provide evidence (quote or paraphrase) for every negative score.

The contract is NOT the only input — the judge also reads the source pack content (via the assembled prompt) to ground its evaluation in what the character was actually instructed to do.

---

## Example: Moss Contract

A useful reference contract is `tests/contracts/generated/moss-v1.json`. It captures Moss's identity ("woodland familiar"), warmth, curiosity, declared boundaries (no romantic roleplay, no human-claiming), voice ("warm and unhurried"), and favorite phrases.

Note that the contract deliberately does NOT specify "should be playful" or "should be whimsical" in `must`. Those are `should` or omitted — they describe Moss's default register but aren't hard requirements.

---

## When a Contract Is Wrong

Three failure modes:

1. **Heuristic missed something.** Edit the contract by hand. Do not regenerate without bumping the version.
2. **LLM-assisted refinement fabricated a rule.** Re-run with `--assisted` after editing the source packs to make the rule explicit. The LLM should mirror, not invent.
3. **The contract drifted from the source pack.** Re-run the extractor. Bump the version. Re-run the affected evaluations.

The contract is the source of truth for evaluation. If the contract contradicts the pack, fix the contract first, then audit any prior results that used the wrong contract.