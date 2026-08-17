"""Optional AI helpers. Nothing is sent remotely unless the user configures a key."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from .errors import ConfigurationError


def _settings() -> tuple[str, str, str]:
    key = os.environ.get("BETON_AI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    base = (os.environ.get("BETON_AI_BASE_URL") or os.environ.get("OPENAI_API_BASE") or "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("BETON_AI_MODEL", "gpt-4o-mini")
    if not key:
        raise ConfigurationError("AI is disabled. Set BETON_AI_API_KEY and optionally BETON_AI_MODEL to enable it.")
    return key, base, model


def complete(prompt: str, system: str = "You are a concise helpful assistant.") -> str:
    key, base, model = _settings()
    payload = json.dumps({"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}], "temperature": 0.2}).encode()
    request = urllib.request.Request(
        f"{base}/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"AI request failed: {exc}") from exc
    try:
        return str(data["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        raise ConfigurationError("AI provider returned an unexpected response.") from exc
