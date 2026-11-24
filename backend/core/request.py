"""Request helpers shared across apps."""

from __future__ import annotations

from rest_framework.request import Request
from rest_framework.throttling import BaseThrottle


def client_ip(request: Request) -> str:
    """Client address, honouring X-Forwarded-For only for the number of proxies configured."""
    return str(BaseThrottle().get_ident(request))
