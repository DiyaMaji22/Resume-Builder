"""
The JSON envelope used by every endpoint.

    success:  {"message": "...", "data": ...}
    failure:  {"message": "...", "errors": {field: [messages]}}   (errors optional)

The client relies on this shape; keep it stable.
"""

from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.response import Response


def envelope(
    message: str,
    data: Any = None,
    *,
    status_code: int = status.HTTP_200_OK,
) -> Response:
    body: dict[str, Any] = {"message": message}
    if data is not None:
        body["data"] = data
    return Response(body, status=status_code)
