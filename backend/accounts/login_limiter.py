"""Blocks an IP address after repeated failed logins. Successful logins are not counted."""

from __future__ import annotations

from django.core.cache import cache
from rest_framework import status

from core.exceptions import ServiceError


class LoginFailureLimiter:
    MAX_FAILURES = 10
    WINDOW_SECONDS = 15 * 60

    def __init__(self, ip_address: str) -> None:
        self._key = f"login-failures:{ip_address}"

    def ensure_not_blocked(self) -> None:
        failures = cache.get(self._key, 0)
        if failures >= self.MAX_FAILURES:
            raise ServiceError(
                "Too many login attempts. Please wait 15 minutes.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            )

    def record_failure(self) -> None:
        # cache.add is atomic and only sets the window on first failure.
        cache.add(self._key, 0, timeout=self.WINDOW_SECONDS)
        try:
            cache.incr(self._key)
        except ValueError:
            # The key expired between add() and incr(); start a fresh window.
            cache.set(self._key, 1, timeout=self.WINDOW_SECONDS)
