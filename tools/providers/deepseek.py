"""
Runtime Familiars — DeepSeek provider adapter.

OpenAI-compatible chat completions against the DeepSeek API.

CREDENTIALS
-----------
- DEEPSEEK_API_KEY  (required)
- DEEPSEEK_BASE_URL (optional, default https://api.deepseek.com/v1)

MODEL IDENTIFIERS
-----------------
Current DeepSeek V4 family identifiers:
    deepseek-v4-flash
    deepseek-v4-pro

The legacy aliases ``deepseek-chat`` / ``deepseek-reasoner`` were retired
on 2026-07-24. This adapter MUST NOT silently substitute them. If a
legacy alias is configured, the call fails loudly and reports the
configured identifier. If the API rejects an identifier, the error
reports the exact identifier sent.

THINKING MODE
-------------
DeepSeek V4 defaults to thinking-mode ON when ``extra_body.thinking`` is
unset; the API then returns ``reasoning_content`` and enforces that
subsequent turns echo it back (the "reasoning_content must be passed
back" 400 trap). The harness therefore explicitly sets thinking per
call:

    extra: {thinking: false}            → extra_body.thinking = disabled
    extra: {thinking: true}             → extra_body.thinking = enabled
    extra: {reasoning_effort: high}     → top-level reasoning_effort

For Familiar generation the harness uses thinking disabled (normal
mode). The judge may use thinking enabled (deliberative mode) where the
API supports it. Capabilities are configured per call, never assumed in
the core abstraction.
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

# Retired aliases — rejected loudly, never remapped.
RETIRED_ALIASES = ("deepseek-chat", "deepseek-reasoner")

# Current V4 family identifiers (for helpful diagnostics only; unknown
# identifiers are passed through to the API which is the authority).
CURRENT_IDENTIFIERS = ("deepseek-v4-flash", "deepseek-v4-pro")


class DeepSeekProvider(ModelProvider):
    """DeepSeek OpenAI-compatible chat completions."""

    name = "deepseek"

    def __init__(self):
        self.base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").rstrip("/")
        self.endpoint = f"{self.base_url}/chat/completions"

    def available(self) -> bool:
        return bool(os.environ.get("DEEPSEEK_API_KEY"))

    def chat(
        self,
        system: str,
        messages: List[Dict[str, str]],
        config: ProviderConfig,
    ) -> ModelResponse:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            return ModelResponse(
                text="",
                model=config.model,
                provider=self.name,
                latency_ms=0.0,
                error="DEEPSEEK_API_KEY not set",
            )

        model = config.model.strip()
        normalized = model.lower()

        # Reject retired legacy aliases loudly — never silently substitute.
        if normalized in RETIRED_ALIASES or normalized.startswith("deepseek-chat") or normalized.startswith("deepseek-reasoner"):
            return ModelResponse(
                text="",
                model=model,
                provider=self.name,
                latency_ms=0.0,
                error=(
                    f"Model identifier '{model}' is a retired DeepSeek alias "
                    f"(retired 2026-07-24). Use an explicit current identifier: "
                    f"{', '.join(CURRENT_IDENTIFIERS)}. The harness does not "
                    f"silently substitute legacy identifiers."
                ),
            )

        msgs = [{"role": "system", "content": system}] + messages
        body: Dict[str, Any] = {
            "model": model,
            "messages": msgs,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        }
        if config.seed is not None:
            body["seed"] = config.seed

        # Thinking mode controls (V4 family).
        extra = config.extra or {}
        thinking = extra.get("thinking")
        effort = (extra.get("reasoning_effort") or "").strip().lower()

        if thinking is not None:
            if isinstance(thinking, str):
                thinking = thinking.strip().lower() in ("1", "true", "yes", "enabled", "on")
            body["extra_body"] = body.get("extra_body", {})
            body["extra_body"]["thinking"] = {"type": "enabled" if thinking else "disabled"}

        if effort:
            if effort in {"low", "medium", "high", "max"}:
                body["reasoning_effort"] = effort
            else:
                # Unknown effort values are surfaced, not silently dropped.
                return ModelResponse(
                    text="",
                    model=model,
                    provider=self.name,
                    latency_ms=0.0,
                    error=(
                        f"Unsupported reasoning_effort '{effort}' in provider config. "
                        f"Supported: low, medium, high, max."
                    ),
                )

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
    """Register the DeepSeek provider with the provider registry."""
    from tools.providers import PROVIDERS

    PROVIDERS["deepseek"] = DeepSeekProvider()