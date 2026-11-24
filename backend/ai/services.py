"""AI suggestion use case. Thin on purpose: prompts and transport are separate modules."""

from __future__ import annotations

from functools import lru_cache

from django.conf import settings

from ai.client import ChatCompletionClient
from ai.prompts import SYSTEM_PROMPT, SuggestContext, SuggestField, build_prompt
from core.exceptions import ExternalServiceError, ServiceUnavailableError


@lru_cache(maxsize=1)
def get_client() -> ChatCompletionClient:
    return ChatCompletionClient(
        base_url=settings.OPENAI_BASE_URL,
        api_key=settings.OPENAI_KEY,
        model=settings.OPENAI_MODEL,
        timeout_seconds=settings.OPENAI_TIMEOUT_SECONDS,
    )


def suggest(
    field: SuggestField, context: SuggestContext, *, client: ChatCompletionClient | None = None
) -> str:
    if not settings.OPENAI_KEY:
        raise ServiceUnavailableError("AI suggestions are not configured on this server.")

    provider = client or get_client()
    prompt = build_prompt(field, context)
    suggestion = provider.complete(system=SYSTEM_PROMPT, user=prompt)
    if not suggestion:
        raise ExternalServiceError("AI returned an empty response.")
    return suggestion
