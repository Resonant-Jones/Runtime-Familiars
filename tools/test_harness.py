#!/usr/bin/env python3
"""
Runtime Familiars — Harness Self-Tests

Verifies the harness plumbing works end-to-end without API keys:
  - Assembles a pack
  - Runs scenarios through the SimulatorProvider
  - Applies mechanical assertions
  - Writes transcripts and manifest
  - Aggregates a report

Run via:
    python3 tools/test_harness.py

These tests are NOT unit tests of business logic — they are smoke
tests that the whole pipeline can complete. Use them after any
change to tools/eval.py, tools/extract_contract.py, or
tools/providers/.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import yaml

from tools.assemble import assemble  # noqa: E402
from tools.eval import (  # noqa: E402
    run_scenario_for_suite, assemble_for_suite, render_transcript_markdown,
    run_mechanical_assertions, write_manifest,
)
from tools.extract_contract import contract_from_assembly  # noqa: E402
from tools.providers.simulator import SimulatorProvider  # noqa: E402
from tools.providers import ProviderConfig  # noqa: E402


def test_assembly_succeeds() -> bool:
    """Verify all six matrix configurations assemble without error."""
    print("[test_assembly_succeeds]", end=" ")
    suites = ["moss", "moss-gentle", "moss-hollow", "roko-base", "roko-recursive", "vic-strategic"]
    try:
        for s in suites:
            suite_path = PROJECT_ROOT / "tests" / "suites" / f"{s}.yaml"
            with open(suite_path) as f:
                suite = yaml.safe_load(f)
            result = assemble_for_suite(suite)
            assert result.assembled_prompt, f"{s} produced empty prompt"
            assert "##" in result.assembled_prompt or "#" in result.assembled_prompt, f"{s} missing headers"
        print("PASS")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_contract_extraction_succeeds() -> bool:
    """Verify contracts extract for all six configurations."""
    print("[test_contract_extraction_succeeds]", end=" ")
    suites = ["moss", "moss-gentle", "moss-hollow", "roko-base", "roko-recursive", "vic-strategic"]
    try:
        for s in suites:
            suite_path = PROJECT_ROOT / "tests" / "suites" / f"{s}.yaml"
            contract = contract_from_assembly(str(suite_path), contract_version="v1")
            assert "identity" in contract, f"{s} contract missing identity"
            assert "behavior" in contract, f"{s} contract missing behavior"
            assert "judge_dimensions" in contract, f"{s} contract missing judge_dimensions"
        print("PASS")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_scenario_files_valid() -> bool:
    """Every scenario YAML parses and has the required fields."""
    print("[test_scenario_files_valid]", end=" ")
    try:
        scenarios_dir = PROJECT_ROOT / "tests" / "scenarios"
        files = sorted(scenarios_dir.glob("*.yaml"))
        assert len(files) >= 11, f"Expected ≥ 11 scenarios, found {len(files)}"
        for f in files:
            with open(f) as fp:
                s = yaml.safe_load(fp)
            assert "id" in s, f"{f.name} missing id"
            assert "turns" in s, f"{f.name} missing turns"
            assert len(s["turns"]) >= 1, f"{f.name} has no turns"
            for t in s["turns"]:
                assert "role" in t, f"{f.name} turn missing role"
                assert "content" in t, f"{f.name} turn missing content"
                assert t["role"] == "user", f"{f.name} has non-user turn (user-scripted scenarios only)"
        print(f"PASS ({len(files)} scenarios)")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_suite_files_valid() -> bool:
    """Every suite YAML has the required composition structure."""
    print("[test_suite_files_valid]", end=" ")
    try:
        suites_dir = PROJECT_ROOT / "tests" / "suites"
        files = sorted(suites_dir.glob("*.yaml")) + sorted((suites_dir / "deltas").glob("*.yaml"))
        for f in files:
            with open(f) as fp:
                s = yaml.safe_load(fp)
            assert "id" in s, f"{f.name} missing id"
            # Native-control suites carry no character by design.
            if s.get("native"):
                assert "character" not in s, f"{f.name} native suite must not have a character"
                assert s.get("scenarios"), f"{f.name} native suite missing scenarios"
                continue
            # Aggregator suite (e.g. all.yaml) and delta suites use
            # include_suites / baseline / variant structure instead of
            # an immediate character + scenarios. Accept those too.
            if "include_suites" in s or "baseline" in s:
                continue
            assert "character" in s, f"{f.name} missing character"
            assert "scenarios" in s or "baseline" in s, f"{f.name} missing scenarios or baseline"
            char = PROJECT_ROOT / s["character"]
            assert (char / "PACKAGE.json").exists() or list(char.glob("*.md")), f"{f.name} character path unresolvable: {s['character']}"
        print(f"PASS ({len(files)} suites)")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_simulator_provider_runs() -> bool:
    """The simulator provider returns a response when called."""
    print("[test_simulator_provider_runs]", end=" ")
    try:
        provider = SimulatorProvider()
        cfg = ProviderConfig(model="test-model", temperature=0.5, seed=None, max_tokens=200)
        resp = provider.chat(
            "You are a test character.",
            [{"role": "user", "content": "hello"}],
            cfg,
        )
        assert resp.ok, f"Simulator returned error: {resp.error}"
        assert resp.text, "Simulator returned empty text"
        assert resp.provider == "simulator"
        assert resp.input_tokens and resp.input_tokens > 0
        print("PASS")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_mechanical_assertions_run() -> bool:
    """Mechanical assertions produce findings for a known scenario."""
    print("[test_mechanical_assertions_run]", end=" ")
    try:
        scenario = {
            "id": "test",
            "mechanical_assertions": [
                "response is not empty",
                'response does not contain: "I am an AI"',
                "response length is reasonable (≤ 600 chars for one user turn)",
                'response does not open with "Hello! How can I"',
            ],
        }
        transcript = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello there, friend."},
        ]
        passed, findings = run_mechanical_assertions(scenario, transcript)
        assert isinstance(passed, bool)
        assert len(findings) == 4
        # All four should pass for this clean response
        assert all(f["passed"] for f in findings), f"Some assertions failed: {findings}"
        print("PASS")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_end_to_end_dry_run(tmp: Path) -> bool:
    """Run a single scenario through the simulator and verify outputs."""
    print("[test_end_to_end_dry_run]", end=" ")
    try:
        # Load moss-gentle suite
        suite_path = PROJECT_ROOT / "tests" / "suites" / "moss-gentle.yaml"
        with open(suite_path) as f:
            suite = yaml.safe_load(f)

        provider = SimulatorProvider()
        model_def = {"provider": "simulator", "id": "sim-1", "model": "sim-1", "temperature": 0.0}

        contract_path = PROJECT_ROOT / "tests" / "contracts" / "generated" / "moss-gentle-v1.json"

        # Run the low-context scenario (smallest)
        suite_dir = tmp / "moss-gentle"
        suite_dir.mkdir(parents=True, exist_ok=True)
        write_manifest(
            suite_dir / "manifest.json",
            "moss-gentle", str(suite_path), suite["character"],
            suite.get("composition", {}), model_def, contract_path,
            "2026-08-09T00:00:00Z", 1,
        )

        result = run_scenario_for_suite(
            suite, "moss-gentle", "low-context", model_def, provider,
            run_number=1, runs_per_scenario=1,
            output_dir=suite_dir,
            scenarios_dir=PROJECT_ROOT / "tests" / "scenarios",
            seed=None,
        )

        # Verify
        assert "transcript_path" in result, f"result missing transcript_path: {result}"
        transcript_path = Path(result["transcript_path"])
        assert transcript_path.exists(), f"transcript not written: {transcript_path}"
        content = transcript_path.read_text()
        assert "Suite: moss-gentle" in content
        assert "Scenario: low-context" in content
        assert "SIMULATOR RESPONSE" in content  # simulator marker

        eval_path = suite_dir / "low-context" / "run-01.eval.json"
        assert eval_path.exists(), f"eval.json not written: {eval_path}"
        eval_data = json.loads(eval_path.read_text())
        assert "mechanical_assertions" in eval_data
        assert "mechanical_passed" in eval_data
        # Mechanical assertions on simulator output — let's see what happens
        # (the simulator marker contains "AI" which is forbidden by the
        # identity-disclosure assertion, but low-context doesn't have
        # mechanical assertions)

        # Manifest
        manifest_path = suite_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        assert manifest["suite"] == "moss-gentle"
        assert manifest["model"]["provider"] == "simulator"
        assert manifest["contract_path"]

        print("PASS")
        return True
    except Exception as e:
        import traceback
        print(f"FAIL: {e}")
        traceback.print_exc()
        return False


def test_judge_parser_handles_fences() -> bool:
    """The judge JSON parser tolerates markdown code fences."""
    print("[test_judge_parser_handles_fences]", end=" ")
    try:
        from tools.evaluate_transcript import parse_judge_output
        sample = """
```json
{
  "verdict": "warn",
  "confidence": 0.6,
  "scores": {"identity_fidelity": 3, "drift": 2},
  "findings": [],
  "summary": "Some concern."
}
```
"""
        parsed = parse_judge_output(sample)
        assert parsed["verdict"] == "warn"
        assert parsed["confidence"] == 0.6
        print("PASS")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_native_suite_assembles_without_character() -> bool:
    """Native-control suites skip assembly and get a neutral prompt."""
    print("[test_native_suite_assembles_without_character]", end=" ")
    try:
        suite_path = PROJECT_ROOT / "tests" / "suites" / "native-control.yaml"
        with open(suite_path) as f:
            suite = yaml.safe_load(f)
        assert suite.get("native"), "native-control.yaml must declare native: true"
        assert "character" not in suite, "native-control.yaml must not have a character"
        from tools.eval import assemble_for_suite
        assembly = assemble_for_suite(suite)
        assert assembly.assembled_prompt, "native suite produced empty prompt"
        assert "Moss" not in assembly.assembled_prompt, "native prompt leaked character content"
        assert "helpful" in assembly.assembled_prompt.lower(), "native prompt should be neutral helper"
        print("PASS")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_native_judge_prompt_has_10_dimensions() -> bool:
    """Native judge prompt requests the 10 Phase 5.B dimensions."""
    print("[test_native_judge_prompt_has_10_dimensions]", end=" ")
    try:
        from tools.evaluate_transcript import (
            build_native_judge_prompt, NATIVE_DIMENSIONS,
        )
        assert len(NATIVE_DIMENSIONS) == 10
        prompt = build_native_judge_prompt(
            {"id": "test", "turns": [{"role": "user", "content": "hi"}]},
            "# transcript",
            NATIVE_DIMENSIONS,
        )
        for d in NATIVE_DIMENSIONS:
            assert d in prompt, f"native dimension missing from prompt: {d}"
        assert "informational" in prompt, "native verdict must be informational"
        assert "behavioral contract" not in prompt.lower(), "native prompt must not reference a contract"
        print("PASS")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_calibration_matrix_declares_explicit_ids() -> bool:
    """Calibration matrix uses explicit current identifiers, no legacy aliases."""
    print("[test_calibration_matrix_declares_explicit_ids]", end=" ")
    try:
        matrix_path = PROJECT_ROOT / "tests" / "models" / "calibration-matrix.yaml"
        with open(matrix_path) as f:
            matrix = yaml.safe_load(f)
        models = matrix.get("models", [])
        assert len(models) == 2, f"expected 2 models, got {len(models)}"
        ids = {m.get("model") for m in models}
        # No retired DeepSeek aliases used as model identifiers
        # (the matrix description may mention them as documentation).
        assert "deepseek-chat" not in ids
        assert "deepseek-reasoner" not in ids
        # Explicit current identifiers present.
        assert "deepseek-v4-flash" in ids, f"missing deepseek-v4-flash: {ids}"
        assert any("m3" in str(m.get("model", "")).lower() for m in models), f"missing M3: {ids}"
        # Both subject providers declared.
        providers = {m.get("provider") for m in models}
        assert "deepseek" in providers and "minimax" in providers, f"providers: {providers}"
        # Judge is a single consistent model.
        judge = matrix.get("judge", {})
        assert judge.get("provider"), "matrix judge must declare a provider"
        assert judge.get("model"), "matrix judge must declare a model"
        print(f"PASS ({ids})")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_deepseek_provider_rejects_legacy_aliases() -> bool:
    """DeepSeek adapter rejects retired aliases loudly (no silent remap)."""
    print("[test_deepseek_provider_rejects_legacy_aliases]", end=" ")
    import os
    try:
        os.environ["DEEPSEEK_API_KEY"] = "dummy-for-test"
        from tools.providers.deepseek import DeepSeekProvider
        provider = DeepSeekProvider()
        assert provider.available()
        resp = provider.chat(
            "system",
            [{"role": "user", "content": "hi"}],
            ProviderConfig(model="deepseek-chat"),
        )
        assert not resp.ok, "retired alias must not succeed"
        assert "retired" in resp.error.lower(), f"error should mention retirement: {resp.error}"
        assert "deepseek-chat" in resp.error, "error must report the configured identifier"
        resp2 = provider.chat(
            "system",
            [{"role": "user", "content": "hi"}],
            ProviderConfig(model="deepseek-reasoner"),
        )
        assert not resp2.ok, "deepseek-reasoner must also be rejected"
        print("PASS")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_minimax_provider_m3_detection() -> bool:
    """MiniMax adapter recognizes M3 identifiers (case-insensitive)."""
    print("[test_minimax_provider_m3_detection]", end=" ")
    try:
        from tools.providers.minimax import is_m3
        assert is_m3("MiniMax-M3")
        assert is_m3("minimax-m3")
        assert is_m3("minimax/minimax-m3")
        assert is_m3("some-other-m3")
        assert not is_m3("MiniMax-M2.7")
        assert not is_m3("deepseek-v4-flash")
        print("PASS")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def main() -> int:
    tests = [
        test_assembly_succeeds,
        test_scenario_files_valid,
        test_suite_files_valid,
        test_contract_extraction_succeeds,
        test_simulator_provider_runs,
        test_mechanical_assertions_run,
        test_judge_parser_handles_fences,
        test_native_suite_assembles_without_character,
        test_native_judge_prompt_has_10_dimensions,
        test_calibration_matrix_declares_explicit_ids,
        test_deepseek_provider_rejects_legacy_aliases,
        test_minimax_provider_m3_detection,
    ]
    tmp = Path(tempfile.mkdtemp(prefix="rf-harness-test-"))
    try:
        tests.append(lambda: test_end_to_end_dry_run(tmp))

        results = []
        for t in tests:
            results.append(t())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    passed = sum(1 for r in results if r)
    failed = len(results) - passed
    print(f"\n# {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())