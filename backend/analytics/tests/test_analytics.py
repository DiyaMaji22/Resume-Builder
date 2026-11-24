from __future__ import annotations

from io import StringIO

from django.core.cache import cache
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from accounts.models import User
from core.demo_data import seed_demo_data
from core.testing import authenticate, make_user
from resumes.models import Resume


class AnalyticsTestCase(TestCase):
    def setUp(self) -> None:
        cache.clear()
        seed_demo_data(flush=True)
        self.staff = User.objects.create_superuser(
            email="staff@example.com", name="Staff", password="a-long-staff-password"
        )


class AnalyticsAccessTests(AnalyticsTestCase):
    def test_anonymous_is_unauthorized(self) -> None:
        self.assertEqual(APIClient().get("/api/analytics").status_code, 401)

    def test_ordinary_user_is_forbidden(self) -> None:
        # The original API let any signed-in user read figures that included other users' names.
        response = authenticate(APIClient(), make_user(email="plain@example.com")).get("/api/analytics")
        self.assertEqual(response.status_code, 403)

    def test_staff_user_gets_the_dashboard(self) -> None:
        response = authenticate(APIClient(), self.staff).get("/api/analytics")
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        # Four demo users plus the staff account created in setUp.
        self.assertEqual(data["summary"], {"totalUsers": 5, "totalResumes": 9, "publicResumes": 5})
        self.assertEqual(data["resumesPerUser"][0], {"userName": "Diya Maji", "resumeCount": 3})

    def test_template_usage_covers_every_seeded_template(self) -> None:
        data = authenticate(APIClient(), self.staff).get("/api/analytics").json()["data"]
        counts = {row["_id"]: row["totalResumes"] for row in data["templateUsage"]}
        self.assertEqual(sum(counts.values()), 9)
        self.assertEqual(
            set(counts), {"classic", "modern", "minimal", "executive", "home_college", "general_template"}
        )

    def test_top_skills_are_lowercased_and_ranked(self) -> None:
        data = authenticate(APIClient(), self.staff).get("/api/analytics").json()["data"]
        self.assertLessEqual(len(data["topSkills"]), 5)
        frequencies = [row["frequency"] for row in data["topSkills"]]
        self.assertEqual(frequencies, sorted(frequencies, reverse=True))
        self.assertTrue(all(row["_id"] == row["_id"].lower() for row in data["topSkills"]))

    def test_monthly_velocity_reflects_seeded_dates(self) -> None:
        data = authenticate(APIClient(), self.staff).get("/api/analytics").json()["data"]
        months = [row["_id"] for row in data["monthlyVelocity"]]
        self.assertEqual(months, sorted(months))
        self.assertIn("2026-08", months)
        self.assertIn("2026-11", months)


@override_settings(ENABLE_DB_ADMIN_ENDPOINTS=False)
class AdminOperationsDisabledTests(AnalyticsTestCase):
    def test_setup_and_seed_are_hidden_when_disabled(self) -> None:
        client = authenticate(APIClient(), self.staff)
        self.assertEqual(client.post("/api/analytics/setup").status_code, 404)
        self.assertEqual(client.post("/api/analytics/seed").status_code, 404)

    def test_ordinary_user_cannot_run_admin_operations_even_when_enabled(self) -> None:
        with self.settings(ENABLE_DB_ADMIN_ENDPOINTS=True):
            plain = authenticate(APIClient(), make_user(email="plain2@example.com"))
            self.assertEqual(plain.post("/api/analytics/setup").status_code, 403)


class AdminOperationsEnabledTests(AnalyticsTestCase):
    def test_setup_applies_validators(self) -> None:
        with self.settings(ENABLE_DB_ADMIN_ENDPOINTS=True):
            response = authenticate(APIClient(), self.staff).post("/api/analytics/setup")
        self.assertEqual(response.status_code, 200)
        self.assertIn("validator on 'resumes'", response.json()["data"]["log"])

    def test_seed_replaces_contents(self) -> None:
        Resume.objects.create(user=self.staff, title="Temporary")
        with self.settings(ENABLE_DB_ADMIN_ENDPOINTS=True):
            response = authenticate(APIClient(), self.staff).post("/api/analytics/seed")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Resume.objects.count(), 9)
        self.assertFalse(Resume.objects.filter(title="Temporary").exists())


class SeedCommandTests(TestCase):
    def test_refuses_to_run_over_existing_data_without_flush(self) -> None:
        make_user(email="existing@example.com")
        with self.assertRaisesMessage(CommandError, "--flush"):
            call_command("seed_demo_data", force=True, stdout=StringIO())

    def test_refuses_outside_debug_without_force(self) -> None:
        with self.assertRaisesMessage(CommandError, "--force"):
            call_command("seed_demo_data", stdout=StringIO())

    def test_seeds_into_an_empty_database(self) -> None:
        out = StringIO()
        call_command("seed_demo_data", force=True, stdout=out)
        self.assertIn("Seeded 4 users and 9 resumes", out.getvalue())
        self.assertEqual(User.objects.count(), 4)

    def test_seeded_resumes_keep_their_intended_visibility_and_colour(self) -> None:
        # The original seed silently ignored these two fields. Regression guard.
        seed_demo_data(flush=True)
        minimal = Resume.objects.get(title="Frontend UI/UX Specialist")
        self.assertTrue(minimal.is_public)
        self.assertEqual(minimal.accent_color, "#0EA5E9")
