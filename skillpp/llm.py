"""Minimal OpenAI-compatible chat client (works with GLM, Ollama, OpenAI, ...).

httpx imports lazily so the offline test suite needs zero dependencies.
"""

from __future__ import annotations

import os


class LLMClient:
    """Chat completion against any OpenAI-compatible endpoint."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.base_url = (base_url or os.environ.get("SKILLPP_BASE_URL", "")).rstrip("/")
        self.api_key = api_key or os.environ.get("SKILLPP_API_KEY", "none")
        self.model = model or os.environ.get("SKILLPP_MODEL", "")
        if not self.base_url or not self.model:
            raise ValueError(
                "Set SKILLPP_BASE_URL and SKILLPP_MODEL (e.g. an Ollama endpoint "
                "http://localhost:11434/v1 with any local model, or any "
                "OpenAI-compatible provider)."
            )

    def complete(self, prompt: str) -> str:
        import httpx  # lazy: offline test runs never need it

        resp = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
