"""Minimal OpenAI-compatible chat client (works with GLM, Ollama, OpenAI, ...).

httpx imports lazily so the offline test suite needs zero dependencies.
"""

from __future__ import annotations

import os
import time


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

        # retry transient failures (transport, 408/429/5xx) so one hiccup
        # doesn't kill a benchmark run; auth/bad-request errors raise at once.
        # 429 waits longer (Retry-After when the endpoint sends it).
        last_err: Exception | None = None
        for attempt in range(4):
            try:
                resp = httpx.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,
                    },
                    timeout=90,
                )
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait = e.response.headers.get("Retry-After", "")
                    wait = int(wait) if wait.isdigit() else 5 * (attempt + 1)
                    last_err = e
                elif e.response.status_code == 408 or e.response.status_code >= 500:
                    wait = 2 * (attempt + 1)
                    last_err = e
                else:
                    raise
            except httpx.TransportError as e:
                wait = 2 * (attempt + 1)
                last_err = e
            if attempt < 3:  # no sleep after the final attempt
                time.sleep(min(wait, 60))
        raise last_err  # type: ignore[misc]
