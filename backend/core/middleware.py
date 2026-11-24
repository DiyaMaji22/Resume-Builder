"""Small middleware for headers Django's SecurityMiddleware does not set."""

from __future__ import annotations

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse


class PermissionsPolicyMiddleware:
    """Disables browser features the API never needs."""

    HEADER_VALUE = "camera=(), microphone=(), geolocation=()"

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        response.setdefault("Permissions-Policy", self.HEADER_VALUE)
        return response
