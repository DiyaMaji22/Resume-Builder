"""A minimal client for OpenAI-compatible chat completion endpoints."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class ChatCompletionClient:
    """Wraps ``POST {base_url}/v1/chat/completions``. Errors are reported as ExternalServiceError."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout_seconds: float,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._model = model
        self._http = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout_seconds,
            transport=transport,
        )

    def complete(self, *, system: str, user: str, max_tokens: int = 400, temperature: float = 0.7) -> str:
        payload: dict[str, Any] = {
            "model": self._model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        try:
            response = self._http.post("/v1/chat/completions", json=payload)
        except httpx.HTTPError as exc:
            logger.warning("AI provider unreachable: %s", exc)
            raise ExternalServiceError("AI service is unreachable. Please try again.") from exc

        if response.is_error:
            logger.error("AI provider returned HTTP %s: %s", response.status_code, response.text[:500])
            raise ExternalServiceError("AI service returned an error. Please try again.")

        try:
            content = response.json()["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            logger.error("Unexpected AI provider response shape")
            raise ExternalServiceError("AI service returned an unexpected response.") from exc

        return str(content or "").strip()

    def close(self) -> None:
        self._http.close()
