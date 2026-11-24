"""
Windowed rate limiting built on DRF's throttle machinery.

DRF's built-in rates only accept per-second/minute/hour/day units with a count of
1 (e.g. "10/min"). The API needs windows such as "10 per 15 minutes", so this
module accepts "<requests>/<window>" with an optional multiplier, e.g. "200/15m".
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from django.http import HttpRequest
from rest_framework.request import Request
from rest_framework.throttling import SimpleRateThrottle

if TYPE_CHECKING:
    from rest_framework.views import APIView

_RATE_PATTERN = re.compile(r"^(?P<requests>\d+)/(?P<multiplier>\d+)?(?P<unit>[smhd])$")
_UNIT_SECONDS = {"s": 1, "m": 60, "h": 3600, "d": 86400}


class WindowedRateThrottle(SimpleRateThrottle):
    """Base class. Subclasses set ``scope`` and ``rate`` and implement ``get_ident``."""

    rate: str = "60/1m"

    def parse_rate(self, rate: str | None) -> tuple[int, int]:  # type: ignore[override]
        if rate is None:
            return (0, 0)
        match = _RATE_PATTERN.match(rate)
        if match is None:
            raise ValueError(f"Invalid throttle rate: {rate!r}")
        requests = int(match.group("requests"))
        multiplier = int(match.group("multiplier") or 1)
        return requests, multiplier * _UNIT_SECONDS[match.group("unit")]


class IPWindowedThrottle(WindowedRateThrottle):
    """Limits by client IP address (anonymous endpoints)."""

    def get_cache_key(self, request: Request | HttpRequest, view: APIView) -> str | None:
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}


class UserWindowedThrottle(WindowedRateThrottle):
    """Limits by authenticated user, falling back to IP for anonymous requests."""

    def get_cache_key(self, request: Request | HttpRequest, view: APIView) -> str | None:
        user = getattr(request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False):
            ident = f"user:{user.pk}"
        else:
            ident = f"ip:{self.get_ident(request)}"
        return self.cache_format % {"scope": self.scope, "ident": ident}


class GlobalIPThrottle(IPWindowedThrottle):
    """Default ceiling for every API request from one IP."""

    scope = "global"
    rate = "200/15m"


class RegisterThrottle(IPWindowedThrottle):
    scope = "auth-register"
    rate = "5/1h"


class RefreshThrottle(IPWindowedThrottle):
    scope = "auth-refresh"
    rate = "30/15m"


class AISuggestThrottle(UserWindowedThrottle):
    scope = "ai-suggest"
    rate = "20/1m"
