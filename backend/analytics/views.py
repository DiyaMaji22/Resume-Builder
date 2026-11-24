"""
Analytics endpoints. Analytics spans every user's data, so access is restricted to staff.

The original API let any signed-in user read these figures, which included other users' names.
"""

from __future__ import annotations

from io import StringIO
from typing import ClassVar

from django.conf import settings
from django.core.management import call_command
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.services import collect_analytics
from core.exceptions import NotFoundError
from core.responses import envelope


class AnalyticsView(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request: Request) -> Response:
        return envelope("Analytics retrieved successfully", collect_analytics())


class _AdminOperationView(APIView):
    """Schema setup and demo seeding are operator tasks. They are off unless explicitly enabled."""

    permission_classes = (IsAdminUser,)
    command_name: str = ""
    command_options: ClassVar[dict[str, object]] = {}
    message: str = ""

    def post(self, request: Request) -> Response:
        if not settings.ENABLE_DB_ADMIN_ENDPOINTS:
            raise NotFoundError("Not found")
        output = StringIO()
        call_command(self.command_name, stdout=output, **self.command_options)
        return envelope(self.message, {"log": output.getvalue()})


class SetupView(_AdminOperationView):
    command_name = "setup_mongodb"
    message = "Database validators applied successfully"


class SeedView(_AdminOperationView):
    command_name = "seed_demo_data"
    command_options: ClassVar[dict[str, object]] = {"flush": True, "force": True}
    message = "Demo data seeded successfully"
