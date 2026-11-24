"""Health check and JSON error pages for non-DRF failures (unknown URLs, crashes)."""

from __future__ import annotations

import logging

from django.conf import settings
from django.db import connection
from django.http import HttpRequest, JsonResponse

logger = logging.getLogger(__name__)


def health(request: HttpRequest) -> JsonResponse:
    """Liveness plus a cheap database ping, so load balancers can detect a dead DB."""
    try:
        connection.ensure_connection()
    except Exception:
        logger.exception("Health check could not reach the database")
        return JsonResponse({"status": "unavailable", "env": settings.ENVIRONMENT}, status=503)
    return JsonResponse({"status": "ok", "env": settings.ENVIRONMENT})


def not_found(request: HttpRequest, exception: Exception | None = None) -> JsonResponse:
    return JsonResponse({"message": "Not found"}, status=404)


def server_error(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"message": "Internal server error"}, status=500)


def bad_request(request: HttpRequest, exception: Exception | None = None) -> JsonResponse:
    """Covers DisallowedHost (unknown Host header) and other malformed requests outside DRF."""
    return JsonResponse({"message": "Bad request"}, status=400)
