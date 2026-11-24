from __future__ import annotations

from datetime import UTC, datetime
from unittest import mock

import pymongo
from django.db import connection
from django.test import SimpleTestCase, TestCase, override_settings
from django.test.client import RequestFactory
from rest_framework.request import Request
from rest_framework.test import APIClient

from core.exceptions import api_exception_handler
from core.mongodb import RESUMES_VALIDATOR, install_validator
from core.request import client_ip
from core.responses import envelope
from core.serializer_fields import IsoDateTimeField
from core.testing import authenticate, make_user
from core.throttling import WindowedRateThrottle


class HealthAndErrorEnvelopeTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_health_reports_ok_when_database_reachable(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_unknown_route_returns_json_envelope(self) -> None:
        response = self.client.get("/api/does-not-exist")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"message": "Not found"})

    def test_malformed_object_id_in_path_is_not_found(self) -> None:
        user = make_user()
        response = authenticate(APIClient(), user).get("/api/resumes/not-a-real-id")
        self.assertEqual(response.status_code, 404)

    def test_unhandled_exception_is_hidden_outside_debug(self) -> None:
        with mock.patch("core.exceptions.settings") as settings_mock:
            settings_mock.DEBUG = False
            response = api_exception_handler(RuntimeError("secret internals"), {"request": None})
        self.assertIsNotNone(response)
        assert response is not None
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data, {"message": "Internal server error"})

    def test_envelope_omits_data_key_when_absent(self) -> None:
        response = envelope("Resume deleted")
        self.assertEqual(response.data, {"message": "Resume deleted"})

    def test_requests_for_unknown_hosts_are_rejected(self) -> None:
        response = self.client.get("/health", HTTP_HOST="attacker.example")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message": "Bad request"})

    def test_permissions_policy_header_is_set(self) -> None:
        response = self.client.get("/health")
        self.assertIn("camera=()", response["Permissions-Policy"])


class SchemaGuardrailTests(TestCase):
    """The database itself must refuse documents that violate the schema."""

    def setUp(self) -> None:
        self.db = connection.get_database()
        install_validator(self.db, "resumes", RESUMES_VALIDATOR)

    def test_invalid_template_is_rejected_by_mongodb(self) -> None:
        from bson import ObjectId

        with self.assertRaises(pymongo.errors.WriteError):
            self.db["resumes"].insert_one(
                {
                    "userId": ObjectId(),
                    "title": "x",
                    "isPublic": False,
                    "template": "not-a-template",
                    "accentColor": "#000000",
                }
            )


class ThrottleAndRequestTests(SimpleTestCase):
    def test_window_rate_strings_parse(self) -> None:
        throttle = WindowedRateThrottle.__new__(WindowedRateThrottle)
        self.assertEqual(throttle.parse_rate("200/15m"), (200, 900))
        self.assertEqual(throttle.parse_rate("5/1h"), (5, 3600))
        self.assertEqual(throttle.parse_rate("20/1m"), (20, 60))

    def test_invalid_rate_is_rejected(self) -> None:
        throttle = WindowedRateThrottle.__new__(WindowedRateThrottle)
        with self.assertRaises(ValueError):
            throttle.parse_rate("many per minute")

    @override_settings(REST_FRAMEWORK={"NUM_PROXIES": 0})
    def test_forwarded_for_is_ignored_without_trusted_proxy(self) -> None:
        request = Request(
            RequestFactory().get("/", REMOTE_ADDR="10.0.0.5", HTTP_X_FORWARDED_FOR="203.0.113.9")
        )
        self.assertEqual(client_ip(request), "10.0.0.5")

    def test_iso_datetime_renders_milliseconds_and_z(self) -> None:
        field = IsoDateTimeField()
        value = datetime(2026, 11, 24, 8, 0, 0, 123456, tzinfo=UTC)
        self.assertEqual(field.to_representation(value), "2026-11-24T08:00:00.123Z")
