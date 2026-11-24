from __future__ import annotations

import json
from typing import Any
from unittest import mock

import httpx
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from ai.client import ChatCompletionClient
from ai.prompts import build_prompt
from core.testing import authenticate, make_user

SUMMARY_REQUEST = {
    "field": "summary",
    "context": {
        "currentText": "Backend dev",
        "existingExperience": [{"position": "Engineer", "company": "Acme", "description": ""}],
        "skills": ["Python", "Django"],
    },
}


def client_with(handler: Any) -> ChatCompletionClient:
    return ChatCompletionClient(
        base_url="https://llm.example.test",
        api_key="secret-key",
        model="test-model",
        timeout_seconds=5,
        transport=httpx.MockTransport(handler),
    )


def completion(text: str) -> httpx.Response:
    return httpx.Response(200, json={"choices": [{"message": {"content": text}}]})


@override_settings(OPENAI_KEY="secret-key")
class AISuggestionTests(TestCase):
    def setUp(self) -> None:
        cache.clear()
        self.user = make_user()
        self.client = authenticate(APIClient(), self.user)

    def post(self, body: dict[str, Any]) -> Any:
        return self.client.post("/api/ai/suggest", body, format="json")

    def test_returns_trimmed_suggestion_and_sends_expected_request(self) -> None:
        captured: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            captured["auth"] = request.headers["authorization"]
            captured["body"] = json.loads(request.content)
            return completion("  I build reliable systems.  ")

        with mock.patch("ai.services.get_client", return_value=client_with(handler)):
            response = self.post(SUMMARY_REQUEST)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], {"suggestion": "I build reliable systems."})
        self.assertEqual(captured["url"], "https://llm.example.test/v1/chat/completions")
        self.assertEqual(captured["auth"], "Bearer secret-key")
        self.assertEqual(captured["body"]["model"], "test-model")
        user_prompt = captured["body"]["messages"][1]["content"]
        self.assertIn("- Engineer at Acme", user_prompt)
        self.assertIn("Skills: Python, Django", user_prompt)

    def test_provider_http_error_is_bad_gateway(self) -> None:
        with mock.patch("ai.services.get_client", return_value=client_with(lambda r: httpx.Response(500))):
            response = self.post(SUMMARY_REQUEST)
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["message"], "AI service returned an error. Please try again.")

    def test_unreachable_provider_is_bad_gateway(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("refused", request=request)

        with mock.patch("ai.services.get_client", return_value=client_with(handler)):
            response = self.post(SUMMARY_REQUEST)
        self.assertEqual(response.status_code, 502)

    def test_empty_completion_is_bad_gateway(self) -> None:
        with mock.patch("ai.services.get_client", return_value=client_with(lambda r: completion("   "))):
            response = self.post(SUMMARY_REQUEST)
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["message"], "AI returned an empty response.")

    def test_unexpected_response_shape_is_bad_gateway(self) -> None:
        with mock.patch(
            "ai.services.get_client", return_value=client_with(lambda r: httpx.Response(200, json={}))
        ):
            response = self.post(SUMMARY_REQUEST)
        self.assertEqual(response.status_code, 502)

    @override_settings(OPENAI_KEY="")
    def test_unconfigured_server_says_so(self) -> None:
        response = self.post(SUMMARY_REQUEST)
        self.assertEqual(response.status_code, 503)

    def test_unknown_field_is_rejected(self) -> None:
        response = self.post({"field": "education", "context": {}})
        self.assertEqual(response.status_code, 400)

    def test_anonymous_requests_are_rejected(self) -> None:
        response = APIClient().post("/api/ai/suggest", SUMMARY_REQUEST, format="json")
        self.assertEqual(response.status_code, 401)


class PromptTests(TestCase):
    def test_bullet_prompt_uses_unknown_placeholders_only_when_missing(self) -> None:
        prompt = build_prompt("experience_description", {"position": "", "company": "Acme"})
        self.assertIn("Position: \n", prompt)  # empty string stays empty, as the original did
        self.assertIn("Company: Acme", prompt)
        self.assertIn("starting with •", prompt)

    def test_summary_prompt_caps_experience_and_skills(self) -> None:
        context = {
            "existingExperience": [
                {"position": f"P{i}", "company": "C", "description": ""} for i in range(6)
            ],
            "skills": [f"S{i}" for i in range(12)],
        }
        prompt = build_prompt("summary", context)  # type: ignore[arg-type]
        self.assertIn("P2 at C", prompt)
        self.assertNotIn("P3 at C", prompt)
        self.assertIn("S7", prompt)
        self.assertNotIn("S8", prompt)
