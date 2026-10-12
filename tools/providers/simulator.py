"""
Offline Simulator provider — deterministic canned responses.

Used for harness self-tests and CI smoke runs that don't have
network access or API credentials. NEVER registered in the default
PROVIDERS dict — must be imported explicitly.

USAGE
-----
    from tools.providers.simulator import SimulatorProvider
    provider = SimulatorProvider()
    response = provider.chat(system, messages, config)
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Any, Dict, List

from tools.providers import ModelProvider, ModelResponse, ProviderConfig


class SimulatorProvider(ModelProvider):
    """Deterministic provider that returns canned responses.

    The response is derived from a hash of (system + messages + config)
    so the same input always produces the same output. Useful for:
      - Harness self-tests
      - Local development without API keys
      - Smoke-testing the evaluation pipeline end-to-end
    """

    name = "simulator"

    def available(self) -> bool:
        # Always available — that's the point.
        return True

    def chat(
        self,
        system: str,
        messages: List[Dict[str, str]],
        config: ProviderConfig,
    ) -> ModelResponse:
        # Build a stable hash
        h = hashlib.sha256()
        h.update(system.encode())
        for m in messages:
            h.update(m["role"].encode())
            h.update(b"\x00")
            h.update(m["content"].encode())
            h.update(b"\x00")
        h.update(config.model.encode())
        digest = h.hexdigest()

        # Derive a canned response that reflects the input. The intent
        # is that the response looks like the character, but it is
        # deterministic. This is NOT meant to pass any judge — it's
        # only for exercising the harness.
        last_user = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user = m.get("content", "")
                break

        # Use the first ~80 chars of the system prompt as a marker
        sys_marker = system.split("\n", 1)[0][:60]
        text = (
            f"[SIMULATOR RESPONSE — model={config.model}]\n\n"
            f"System marker: {sys_marker!r}\n"
            f"Last user turn: {last_user[:200]!r}\n"
            f"Turn count: {len([m for m in messages if m['role'] == 'user'])}\n\n"
            f"This is a deterministic canned response for harness testing. "
            f"Hash prefix: {digest[:16]}.\n"
        )

        # Judge-mode: if the system prompt marks this as an independent
        # evaluator call, return valid judge JSON so the full judge
        # parsing pipeline can be exercised offline.
        if "independent evaluator" in system.lower():
            # Native-prior vs contract rubric is signaled in the prompt
            # (user message), not the system line.
            prompt_lower = last_user.lower()
            is_native = (
                "un-persona" in prompt_lower
                or "native behavioral prior" in prompt_lower
                or "identity_neutrality" in prompt_lower
            )
            if is_native:
                text = json.dumps({
                    "verdict": "informational",
                    "confidence": 0.8,
                    "scores": {
                        "conversational_nuance": 3,
                        "adaptability": 3,
                        "task_competence": 3,
                        "conflict_handling": 3,
                        "verbosity": 3,
                        "initiative": 3,
                        "warmth": 3,
                        "directness": 3,
                        "epistemic_caution": 3,
                        "identity_neutrality": 5,
                    },
                    "findings": [],
                    "summary": "Simulated native-prior assessment (offline smoke test).",
                })
            else:
                text = json.dumps({
                    "verdict": "pass",
                    "confidence": 0.85,
                    "scores": {
                        "identity_fidelity": 4,
                        "behavior_fidelity": 4,
                        "boundary_fidelity": 4,
                        "tone_fidelity": 4,
                        "drift": 1,
                    },
                    "findings": [],
                    "summary": "Simulated contract-based assessment (offline smoke test).",
                })

        return ModelResponse(
            text=text,
            model=config.model,
            provider=self.name,
            latency_ms=1.0,
            input_tokens=len(system.split()) + sum(len(m["content"].split()) for m in messages),
            output_tokens=len(text.split()),
            metadata={"simulated": True, "hash_prefix": digest[:16]},
        )


def register() -> None:
    """Register the simulator provider (EXPLICIT import only).

    Never auto-registered — production runs must not be able to hit it
    accidentally. Calibration smoke tests call this directly.
    """
    from tools.providers import PROVIDERS

    PROVIDERS["simulator"] = SimulatorProvider()