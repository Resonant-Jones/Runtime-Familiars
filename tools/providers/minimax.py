"""
Runtime Familiars — MiniMax provider adapter.

OpenAI-compatible chat completions against the MiniMax API.

CREDENTIALS
-----------
- MINIMAX_API_KEY   (required — direct API key OR OAuth bearer token)
- MINIMAX_BASE_URL  (optional, default https://api.minimax.io/v1)

For OAuth setups the calibration driver bridges the token from Hermes
auth.json into MINIMAX_API_KEY; the adapter itself only reads env vars.

MODEL IDENTIFIERS
-----------------
Current MiniMax identifiers (M3 family):
    MiniMax-M3
    minimax-m3
    minimax/minimax-m3

MiniMax-M3 on the OpenAI-compatible endpoint keeps thinking inline
unless ``reasoning_split`` is sent, so this adapter always sends
``reasoning_split: true`` for M3 identifiers. ``extra.thinking`` maps
to the ``thinking`` control:

    extra: {thinking: false}  → {"type": "disabled"}   (generation)
    extra: {thinking: true}   → {"type": "adaptive"}   (judging)

Provider-specific naming is NOT part of the evaluation architecture;
the identifier comes from the model matrix / suite config.
"""

from __future__ import annotations

import json
import os
import socket
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from tools.providers import ModelProvider, ModelResponse, ProviderConfig


def is_m3(model: Optional[str]) -> bool:
    """True if the model identifier is a MiniMax M3 variant."""
    m = (model or "").strip().lower()
    return m in {"minimax-m3", "minimax/minimax-m3"} or m.endswith("-m3")


class MiniMaxProvider(ModelProvider):
    """MiniMax OpenAI-compatible chat completions (global endpoint)."""

    name = "minimax"

    def __init__(self):
        self.base_url = os.environ.get("MINIMAX_BASE_URL", "https://api.minimax.io/v1").rstrip("/")
        self.endpoint = f"{self.base_url}/chat/completions"

    def available(self) -> bool:
        return bool(os.environ.get("MINIMAX_API_KEY"))

    def chat(
        self,
        system: str,
        messages: List[Dict[str, str]],
        config: ProviderConfig,
    ) -> ModelResponse:
        api_key = os.environ.get("MINIMAX_API_KEY")
        if not api_key:
            return ModelResponse(
                text="",
                model=config.model,
                provider=self.name,
                latency_ms=0.0,
                error="MINIMAX_API_KEY not set",
            )

        model = config.model.strip()
        msgs = [{"role": "system", "content": system}] + messages
        body: Dict[str, Any] = {
            "model": model,
            "messages": msgs,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        }
        if config.seed is not None:
            body["seed"] = config.seed

        # M3 reasoning controls.
        if is_m3(model):
            body["reasoning_split"] = True
            extra = config.extra or {}
            thinking = extra.get("thinking")
            if thinking is not None:
                if isinstance(thinking, str):
                    thinking = thinking.strip().lower() in ("1", "true", "yes", "enabled", "on")
                body["thinking"] = {"type": "adaptive" if thinking else "disabled"}

        start = time.time()
        try:
            req = urllib.request.Request(
                self.endpoint,
                data=json.dumps(body).encode(),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "content-type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=300) as resp:
                payload = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body_text = e.read().decode(errors="replace")[:500]
            return ModelResponse(
                text="",
                model=model,
                provider=self.name,
                latency_ms=(time.time() - start) * 1000,
                error=(
                    f"HTTP {e.code} for model '{model}' via {self.endpoint}: {body_text}"
                ),
            )
        except (urllib.error.URLError, socket.timeout) as e:
            return ModelResponse(
                text="",
                model=model,
                provider=self.name,
                latency_ms=(time.time() - start) * 1000,
                error=str(e),
            )

        latency = (time.time() - start) * 1000
        try:
            message = payload["choices"][0]["message"]
            text = message.get("content") or ""
            reasoning = message.get("reasoning_content") or ""
        except (KeyError, IndexError):
            text = ""
            reasoning = ""
        usage = payload.get("usage", {})
        return ModelResponse(
            text=text,
            model=model,
            provider=self.name,
            latency_ms=latency,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            metadata={
                "finish_reason": payload.get("choices", [{}])[0].get("finish_reason"),
                "reasoning_content": reasoning[:2000] if reasoning else "",
            },
        )


def register() -> None:
    """Register the MiniMax provider with the provider registry."""
    from tools.providers import PROVIDERS

    PROVIDERS["minimax"] = MiniMaxProvider()