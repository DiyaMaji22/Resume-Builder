"""
Error handling. Every error response uses the same envelope as success responses.

Domain code raises ``ServiceError`` subclasses; DRF and Django errors are mapped
here so that clients always receive ``{"message": ...}`` and never an HTML page
or a stack trace.
"""

from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from rest_framework import exceptions as drf_exceptions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


class ServiceError(Exception):
    """An expected failure that should be reported to the client as-is."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        errors: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors


class ConflictError(ServiceError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=status.HTTP_409_CONFLICT)


class NotFoundError(ServiceError):
    def __init__(self, message: str = "Not found") -> None:
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class AuthenticationError(ServiceError):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class UnprocessableError(ServiceError):
    def __init__(self, message: str, *, errors: Any = None) -> None:
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, errors=errors)


class ExternalServiceError(ServiceError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=status.HTTP_502_BAD_GATEWAY)


class ServiceUnavailableError(ServiceError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


def _error_response(message: str, status_code: int, errors: Any = None) -> Response:
    body: dict[str, Any] = {"message": message}
    if errors is not None:
        body["errors"] = errors
    return Response(body, status=status_code)


def api_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    if isinstance(exc, ServiceError):
        return _error_response(exc.message, exc.status_code, exc.errors)

    response = drf_exception_handler(exc, context)

    if response is None:
        # Unexpected failure: log the full traceback, but never leak internals
        # to the client unless we are running in debug mode.
        logger.exception("Unhandled exception while serving %s", context.get("request"))
        message = str(exc) if settings.DEBUG else "Internal server error"
        return _error_response(message, status.HTTP_500_INTERNAL_SERVER_ERROR)

    if isinstance(exc, drf_exceptions.ValidationError):
        errors = response.data if isinstance(response.data, dict) else {"non_field_errors": response.data}
        return _error_response("Validation failed", response.status_code, errors)

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return _error_response("Unauthorized", response.status_code)

    if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        return _error_response("Too many requests. Please try again later.", response.status_code)

    detail = response.data.get("detail") if isinstance(response.data, dict) else None
    message = str(detail) if detail else "Request failed"
    return _error_response(message, response.status_code)
