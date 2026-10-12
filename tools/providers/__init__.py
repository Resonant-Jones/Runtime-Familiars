"""
Runtime Familiars — Provider Abstraction

Defines the ModelProvider interface used by the evaluation harness.
Adding a new provider means writing a subclass of ModelProvider and
registering it in PROVIDERS below.

INTERFACE
---------
A provider takes a fully-formed prompt (system + history + new user
turn) and returns a ModelResponse. Providers MUST:

  - read credentials from environment variables only (never accept keys
    via CLI args or YAML)
  - fail loudly with a clear error if credentials are missing
  - support temperature and seed where the underlying API supports them
  - return a structured response with text, latency, and metadata
  - never silently retry on error — let the harness decide

NEVER HARDCODE PROVIDER BRANDS INTO THE EVALUATION ARCHITECTURE.
"""

from __future__ import annotations

import os
import time
import urllib.error
import urllib.request
import json
import socket
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ModelResponse:
    """Structured response from a model provider."""

    text: str
    model: str
    provider: str
    latency_ms: float
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass
class ProviderConfig:
    """Configuration for a specific provider call."""

    model: str
    temperature: float = 0.7
    seed: Optional[int] = None
    max_tokens: int = 1024
    extra: Dict[str, Any] = field(default_factory=dict)


class ModelProvider(ABC):
    """Abstract base class for all model providers."""

    name: str = "abstract"

    @abstractmethod
    def chat(
        self,
        system: str,
        messages: List[Dict[str, str]],
        config: ProviderConfig,
    ) -> ModelResponse:
        """Send a chat completion request.

        Args:
            system: The system prompt (assembled Runtime Familiar).
            messages: Ordered list of {"role": ..., "content": ...}.
            config: Model-specific configuration.

        Returns:
            ModelResponse. If the call fails, return a ModelResponse
            with error set and text="" — do not raise.
        """

    def available(self) -> bool:
        """Return True if the provider's credentials are configured."""
        return True


# ────────────────────────────────────────────────────────────────────────────
# Anthropic
# ────────────────────────────────────────────────────────────────────────────


class AnthropicProvider(ModelProvider):
    """Anthropic Messages API. Reads ANTHROPIC_API_KEY from env."""

    name = "anthropic"
    endpoint = "https://api.anthropic.com/v1/messages"
    api_version = "2023-06-01"

    def available(self) -> bool:
        return bool(os.environ.get("ANTHROPIC_API_KEY"))

    def chat(
        self,
        system: str,
        messages: List[Dict[str, str]],
        config: ProviderConfig,
    ) -> ModelResponse:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return ModelResponse(
                text="",
                model=config.model,
                provider=self.name,
                latency_ms=0.0,
                error="ANTHROPIC_API_KEY not set",
            )
        # Strip system message from messages; Anthropic takes it as a field.
        msgs = [m for m in messages if m.get("role") != "system"]
        body: Dict[str, Any] = {
            "model": config.model,
            "max_tokens": config.max_tokens,
            "system": system,
            "messages": msgs,
            "temperature": config.temperature,
        }
        if config.seed is not None:
            # Anthropic does not currently support seed on Messages API;
            # leave it absent — the harness records null in the manifest.
            pass
        start = time.time()
        try:
            req = urllib.request.Request(
                self.endpoint,
                data=json.dumps(body).encode(),
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": self.api_version,
                    "content-type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=300) as resp:
                payload = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body_text = e.read().decode(errors="replace")[:500]
            return ModelResponse(
                text="",
                model=config.model,
                provider=self.name,
                latency_ms=(time.time() - start) * 1000,
                error=f"HTTP {e.code}: {body_text}",
            )
        except (urllib.error.URLError, socket.timeout) as e:
            return ModelResponse(
                text="",
                model=config.model,
                provider=self.name,
                latency_ms=(time.time() - start) * 1000,
                error=str(e),
            )

        latency = (time.time() - start) * 1000
        # Extract content
        content_blocks = payload.get("content", [])
        text = "".join(b.get("text", "") for b in content_blocks if b.get("type") == "text")
        usage = payload.get("usage", {})
        return ModelResponse(
            text=text,
            model=config.model,
            provider=self.name,
            latency_ms=latency,
            input_tokens=usage.get("input_tokens"),
            output_tokens=usage.get("output_tokens"),
            metadata={"stop_reason": payload.get("stop_reason")},
        )


# ────────────────────────────────────────────────────────────────────────────
# OpenAI
# ────────────────────────────────────────────────────────────────────────────


class OpenAIProvider(ModelProvider):
    """OpenAI Chat Completions API. Reads OPENAI_API_KEY from env."""

    name = "openai"
    endpoint = "https://api.openai.com/v1/chat/completions"

    def available(self) -> bool:
        return bool(os.environ.get("OPENAI_API_KEY"))

    def chat(
        self,
        system: str,
        messages: List[Dict[str, str]],
        config: ProviderConfig,
    ) -> ModelResponse:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return ModelResponse(
                text="",
                model=config.model,
                provider=self.name,
                latency_ms=0.0,
                error="OPENAI_API_KEY not set",
            )
        # Prepend system as a system message
        msgs = [{"role": "system", "content": system}] + messages
        body: Dict[str, Any] = {
            "model": config.model,
            "messages": msgs,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        }
        if config.seed is not None:
            body["seed"] = config.seed
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
                model=config.model,
                provider=self.name,
                latency_ms=(time.time() - start) * 1000,
                error=f"HTTP {e.code}: {body_text}",
            )
        except (urllib.error.URLError, socket.timeout) as e:
            return ModelResponse(
                text="",
                model=config.model,
                provider=self.name,
                latency_ms=(time.time() - start) * 1000,
                error=str(e),
            )

        latency = (time.time() - start) * 1000
        try:
            text = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            text = ""
        usage = payload.get("usage", {})
        return ModelResponse(
            text=text,
            model=config.model,
            provider=self.name,
            latency_ms=latency,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            metadata={"finish_reason": payload.get("choices", [{}])[0].get("finish_reason")},
        )


# ────────────────────────────────────────────────────────────────────────────
# Ollama (local)
# ────────────────────────────────────────────────────────────────────────────


class OllamaProvider(ModelProvider):
    """Ollama local API. Reads OLLAMA_HOST from env (default localhost:11434)."""

    name = "ollama"

    def __init__(self):
        self.host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

    def available(self) -> bool:
        try:
            with urllib.request.urlopen(self.host + "/api/tags", timeout=2) as r:
                return r.status == 200
        except Exception:
            return False

    def chat(
        self,
        system: str,
        messages: List[Dict[str, str]],
        config: ProviderConfig,
    ) -> ModelResponse:
        msgs = [{"role": "system", "content": system}] + messages
        body: Dict[str, Any] = {
            "model": config.model,
            "messages": msgs,
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens,
            },
        }
        if config.seed is not None:
            body["options"]["seed"] = config.seed
        start = time.time()
        try:
            req = urllib.request.Request(
                f"{self.host}/api/chat",
                data=json.dumps(body).encode(),
                headers={"content-type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=600) as resp:
                payload = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body_text = e.read().decode(errors="replace")[:500]
            return ModelResponse(
                text="",
                model=config.model,
                provider=self.name,
                latency_ms=(time.time() - start) * 1000,
                error=f"HTTP {e.code}: {body_text}",
            )
        except (urllib.error.URLError, socket.timeout) as e:
            return ModelResponse(
                text="",
                model=config.model,
                provider=self.name,
                latency_ms=(time.time() - start) * 1000,
                error=str(e),
            )
        latency = (time.time() - start) * 1000
        text = payload.get("message", {}).get("content", "")
        # Ollama returns counts in eval_count / prompt_eval_count
        return ModelResponse(
            text=text,
            model=config.model,
            provider=self.name,
            latency_ms=latency,
            input_tokens=payload.get("prompt_eval_count"),
            output_tokens=payload.get("eval_count"),
            metadata={"total_duration_ns": payload.get("total_duration")},
        )


# ────────────────────────────────────────────────────────────────────────────
# Registry
# ────────────────────────────────────────────────────────────────────────────


PROVIDERS: Dict[str, ModelProvider] = {
    "anthropic": AnthropicProvider(),
    "openai": OpenAIProvider(),
    "ollama": OllamaProvider(),
}

# Optional provider modules register themselves here. Importing them is
# safe: each module only defines its class and a register() function.
for _mod_name, _mod in (("deepseek", "deepseek"), ("minimax", "minimax")):
    try:
        _imported = __import__(f"tools.providers.{_mod_name}", fromlist=[_mod])
        if hasattr(_imported, "register"):
            _imported.register()
    except Exception:
        # A broken optional provider must not take down the registry.
        pass


def get_provider(name: str) -> ModelProvider:
    """Look up a provider by name. Raises KeyError if unknown."""
    if name not in PROVIDERS:
        raise KeyError(
            f"Unknown provider: {name}. Available: {list(PROVIDERS.keys())}"
        )
    return PROVIDERS[name]


def available_providers() -> List[str]:
    """Return names of providers whose credentials are configured."""
    return [n for n, p in PROVIDERS.items() if p.available()]