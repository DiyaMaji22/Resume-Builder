"""Reusable serializer fields that match the API's wire format."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from rest_framework import serializers


class IsoDateTimeField(serializers.Field):
    """Renders datetimes as UTC ISO-8601 with millisecond precision, e.g. 2026-11-24T08:00:00.000Z."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("read_only", True)
        super().__init__(**kwargs)

    def to_representation(self, value: datetime | None) -> str:
        if value is None:
            return ""
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
