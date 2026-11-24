from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from django.conf import settings
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from accounts.models import User
from accounts.tokens import ACCESS_TYPE, issue_access_token
from core.testing import LEGACY_BCRYPT_HASH, TEST_PASSWORD, authenticate, make_user
from resumes.models import Resume


class AuthTestCase(TestCase):
    def setUp(self) -> None:
        cache.clear()
        self.client = APIClient()

    def register(self, **overrides: Any) -> dict[str, Any]:
        body = {"name": "Ada Lovelace", "email": "Ada@Example.com", "password": TEST_PASSWORD}
        body.update(overrides)
        return self.client.post("/api/auth/register", body, format="json").json()


class RegisterTests(AuthTestCase):
    def test_register_returns_session_and_normalises_email(self) -> None:
        response = self.client.post(
            "/api/auth/register",
            {"name": "Ada Lovelace", "email": "Ada@Example.com", "password": TEST_PASSWORD},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["message"], "Account created")
        self.assertEqual(body["data"]["user"]["email"], "ada@example.com")
        self.assertTrue(body["data"]["token"])
        self.assertTrue(body["data"]["refreshToken"])
        self.assertRegex(body["data"]["user"]["createdAt"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")
        self.assertIn("_id", body["data"]["user"])

    def test_duplicate_email_is_conflict(self) -> None:
        self.register()
        response = self.client.post(
            "/api/auth/register",
            {"name": "Someone", "email": "ada@example.com", "password": TEST_PASSWORD},
            format="json",
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["message"], "Email already in use")

    def test_weak_password_returns_field_errors(self) -> None:
        response = self.client.post(
            "/api/auth/register",
            {"name": "Ada", "email": "ada@example.com", "password": "short"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertEqual(body["message"], "Validation failed")
        self.assertIn("password", body["errors"])

    def test_registration_is_rate_limited_per_ip(self) -> None:
        for index in range(5):
            self.register(email=f"user{index}@example.com")
        response = self.register(email="sixth@example.com")
        self.assertEqual(response.get("message"), "Too many requests. Please try again later.")


class LoginTests(AuthTestCase):
    def setUp(self) -> None:
        super().setUp()
        make_user(email="grace@example.com")

    def test_login_succeeds_with_correct_password(self) -> None:
        response = self.client.post(
            "/api/auth/login", {"email": "grace@example.com", "password": TEST_PASSWORD}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Login successful")

    def test_wrong_password_and_unknown_email_look_identical(self) -> None:
        wrong = self.client.post(
            "/api/auth/login", {"email": "grace@example.com", "password": "wrong-password-xx"}, format="json"
        )
        unknown = self.client.post(
            "/api/auth/login", {"email": "nobody@example.com", "password": "wrong-password-xx"}, format="json"
        )
        self.assertEqual(wrong.status_code, 401)
        self.assertEqual(unknown.status_code, 401)
        self.assertEqual(wrong.json(), unknown.json())

    def test_repeated_failures_block_the_address(self) -> None:
        for _ in range(10):
            self.client.post(
                "/api/auth/login", {"email": "grace@example.com", "password": "nope-nope-nope"}, format="json"
            )
        response = self.client.post(
            "/api/auth/login", {"email": "grace@example.com", "password": TEST_PASSWORD}, format="json"
        )
        self.assertEqual(response.status_code, 429)

    def test_legacy_bcrypt_account_can_sign_in_and_is_upgraded(self) -> None:
        User.objects.create(name="Legacy", email="legacy@example.com", password=LEGACY_BCRYPT_HASH)
        response = self.client.post(
            "/api/auth/login", {"email": "legacy@example.com", "password": "password123"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        stored = User.objects.get(email="legacy@example.com").password
        self.assertFalse(stored.startswith("$2"), "password should be re-hashed with Django's hasher")

    def test_legacy_account_rejects_wrong_password(self) -> None:
        User.objects.create(name="Legacy", email="legacy@example.com", password=LEGACY_BCRYPT_HASH)
        response = self.client.post(
            "/api/auth/login", {"email": "legacy@example.com", "password": "not-the-password"}, format="json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertTrue(User.objects.get(email="legacy@example.com").password.startswith("$2"))


class TokenTests(AuthTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = make_user(email="token@example.com")

    def _session(self, remember_me: bool = False) -> dict[str, Any]:
        response = self.client.post(
            "/api/auth/login",
            {"email": "token@example.com", "password": TEST_PASSWORD, "rememberMe": remember_me},
            format="json",
        )
        return response.json()["data"]

    def test_refresh_issues_new_access_token(self) -> None:
        session = self._session()
        response = self.client.post(
            "/api/auth/refresh", {"refreshToken": session["refreshToken"]}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["data"]["token"])

    def test_refresh_token_cannot_be_used_as_access_token(self) -> None:
        session = self._session()
        response = authenticate(APIClient(), self.user)
        response.credentials(HTTP_AUTHORIZATION=f"Bearer {session['refreshToken']}")
        self.assertEqual(response.get("/api/auth/me").status_code, 401)

    def test_expired_access_token_is_rejected(self) -> None:
        past = datetime.now(tz=UTC) - timedelta(hours=1)
        token = jwt.encode(
            {"sub": str(self.user.pk), "type": ACCESS_TYPE, "iat": past - timedelta(minutes=15), "exp": past},
            settings.JWT_KEY,
            algorithm="HS256",
        )
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = client.get("/api/auth/me")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"message": "Unauthorized"})

    def test_token_for_deleted_user_is_rejected(self) -> None:
        token = issue_access_token(str(self.user.pk))
        self.user.delete()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(client.get("/api/auth/me").status_code, 401)

    def test_logout_revokes_only_that_session(self) -> None:
        first = self._session()
        second = self._session()
        authed = authenticate(APIClient(), self.user)
        authed.post("/api/auth/logout", {"refreshToken": first["refreshToken"]}, format="json")

        revoked = self.client.post(
            "/api/auth/refresh", {"refreshToken": first["refreshToken"]}, format="json"
        )
        still_valid = self.client.post(
            "/api/auth/refresh", {"refreshToken": second["refreshToken"]}, format="json"
        )
        self.assertEqual(revoked.status_code, 401)
        self.assertEqual(still_valid.status_code, 200)

    def test_session_limit_keeps_the_five_most_recent(self) -> None:
        sessions = [self._session() for _ in range(6)]
        first = sessions[0]
        response = self.client.post(
            "/api/auth/refresh", {"refreshToken": first["refreshToken"]}, format="json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(len(User.objects.get(pk=self.user.pk).refresh_token_ids), 5)

    def test_me_returns_profile(self) -> None:
        response = authenticate(APIClient(), self.user).get("/api/auth/me")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["email"], "token@example.com")

    def test_anonymous_me_is_unauthorized(self) -> None:
        response = self.client.get("/api/auth/me")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"message": "Unauthorized"})


class AccountManagementTests(AuthTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = make_user(email="manage@example.com", name="Manage Me")

    def test_update_profile_changes_name_and_email(self) -> None:
        response = authenticate(APIClient(), self.user).put(
            "/api/users/me", {"name": "New Name", "email": "NEW@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "New Name")
        self.assertEqual(self.user.email, "new@example.com")

    def test_update_profile_rejects_taken_email(self) -> None:
        make_user(email="taken@example.com")
        response = authenticate(APIClient(), self.user).put(
            "/api/users/me", {"email": "taken@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, 409)

    def test_update_profile_with_no_fields_is_rejected(self) -> None:
        response = authenticate(APIClient(), self.user).put("/api/users/me", {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_wrong_current_password_is_400_not_401(self) -> None:
        # A 401 would make the client treat this as an expired session and log the user out.
        response = authenticate(APIClient(), self.user).put(
            "/api/users/me/password",
            {"currentPassword": "not-my-password", "newPassword": "another-good-password"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_password_change_revokes_all_sessions(self) -> None:
        login = self.client.post(
            "/api/auth/login", {"email": "manage@example.com", "password": TEST_PASSWORD}, format="json"
        ).json()["data"]
        authenticate(APIClient(), self.user).put(
            "/api/users/me/password",
            {"currentPassword": TEST_PASSWORD, "newPassword": "a-brand-new-password-1"},
            format="json",
        )
        response = self.client.post(
            "/api/auth/refresh", {"refreshToken": login["refreshToken"]}, format="json"
        )
        self.assertEqual(response.status_code, 401)

        relogin = self.client.post(
            "/api/auth/login",
            {"email": "manage@example.com", "password": "a-brand-new-password-1"},
            format="json",
        )
        self.assertEqual(relogin.status_code, 200)

    def test_delete_account_requires_correct_password(self) -> None:
        response = authenticate(APIClient(), self.user).delete(
            "/api/users/me", {"password": "wrong-password-here"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())

    def test_delete_account_removes_resumes(self) -> None:
        Resume.objects.create(user=self.user, title="Doomed")
        response = authenticate(APIClient(), self.user).delete(
            "/api/users/me", {"password": TEST_PASSWORD}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
        self.assertFalse(Resume.objects.filter(user_id=self.user.pk).exists())


@override_settings(CORS_ALLOWED_ORIGINS=["https://app.example.com"])
class CorsTests(AuthTestCase):
    def test_cors_allows_configured_origin_only(self) -> None:
        allowed = self.client.options(
            "/api/auth/login",
            HTTP_ORIGIN="https://app.example.com",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )
        denied = self.client.options(
            "/api/auth/login",
            HTTP_ORIGIN="https://evil.example.com",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )
        self.assertEqual(allowed["Access-Control-Allow-Origin"], "https://app.example.com")
        self.assertNotIn("Access-Control-Allow-Origin", denied)
