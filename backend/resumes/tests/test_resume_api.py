from __future__ import annotations

from typing import Any

from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from core.testing import authenticate, build_pdf, make_user
from resumes.models import Resume
from resumes.services import save_version


def valid_create_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "title": "Backend Engineer",
        "template": "modern",
        "accentColor": "#4F46E5",
        "professionalSummary": "Engineer who ships reliable services.",
        "personalInfo": {
            "fullName": "Jane Doe",
            "email": "jane@example.com",
            "phone": "+1 555 0100",
            "linkedin": "https://linkedin.com/in/jane",
        },
        "experience": [
            {
                "id": "e1",
                "company": "Acme",
                "position": "Engineer",
                "startDate": "2020",
                "endDate": "2022",
                "isCurrent": False,
                "description": "• Reduced latency by 35%",
            },
        ],
        "skills": ["Python", "Django"],
    }
    body.update(overrides)
    return body


class ResumeTestCase(TestCase):
    def setUp(self) -> None:
        cache.clear()
        self.owner = make_user(email="owner@example.com")
        self.other = make_user(email="other@example.com")
        self.client = authenticate(APIClient(), self.owner)

    def create(self, body: dict[str, Any] | None = None) -> dict[str, Any]:
        response = self.client.post("/api/resumes", body or valid_create_body(), format="json")
        self.assertEqual(response.status_code, 201, response.content)
        return response.json()["data"]


class CrudTests(ResumeTestCase):
    def test_create_returns_full_resume_in_api_shape(self) -> None:
        data = self.create()
        self.assertEqual(data["title"], "Backend Engineer")
        self.assertEqual(data["userId"], str(self.owner.pk))
        self.assertEqual(data["personalInfo"]["fullName"], "Jane Doe")
        self.assertEqual(data["experience"][0]["startDate"], "2020")
        self.assertFalse(data["experience"][0]["isCurrent"])
        self.assertEqual(data["skills"], ["Python", "Django"])
        self.assertEqual(data["versions"], [])
        self.assertIn("createdAt", data)

    def test_list_omits_version_history_and_is_newest_first(self) -> None:
        self.create(valid_create_body(title="First"))
        second = self.create(valid_create_body(title="Second"))
        response = self.client.get("/api/resumes")
        self.assertEqual(response.status_code, 200)
        items = response.json()["data"]
        self.assertEqual([item["title"] for item in items], ["Second", "First"])
        self.assertNotIn("versions", items[0])
        self.assertEqual(second["title"], "Second")

    def test_partial_update_merges_personal_info(self) -> None:
        data = self.create()
        response = self.client.put(
            f"/api/resumes/{data['_id']}",
            {"personalInfo": {"phone": "+1 555 9999"}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        personal = response.json()["data"]["personalInfo"]
        self.assertEqual(personal["phone"], "+1 555 9999")
        self.assertEqual(personal["fullName"], "Jane Doe", "untouched fields must survive a partial update")

    def test_update_replaces_sections_and_template(self) -> None:
        data = self.create()
        response = self.client.put(
            f"/api/resumes/{data['_id']}",
            {"template": "home_college", "experience": []},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["template"], "home_college")
        self.assertEqual(response.json()["data"]["experience"], [])

    def test_delete_removes_resume(self) -> None:
        data = self.create()
        response = self.client.delete(f"/api/resumes/{data['_id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get(f"/api/resumes/{data['_id']}").status_code, 404)

    def test_unknown_template_is_a_validation_error(self) -> None:
        response = self.client.post("/api/resumes", valid_create_body(template="fancy"), format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("template", response.json()["errors"])

    def test_invalid_url_and_colour_are_rejected(self) -> None:
        body = valid_create_body(accentColor="blue")
        body["personalInfo"]["linkedin"] = "linkedin.com/in/jane"
        response = self.client.post("/api/resumes", body, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("accentColor", response.json()["errors"])
        self.assertIn("linkedin", str(response.json()["errors"]))

    def test_title_is_required_on_create(self) -> None:
        body = valid_create_body()
        del body["title"]
        response = self.client.post("/api/resumes", body, format="json")
        self.assertEqual(response.status_code, 400)

    def test_duplicate_copies_content_with_new_title(self) -> None:
        data = self.create()
        response = self.client.post(f"/api/resumes/{data['_id']}/duplicate")
        self.assertEqual(response.status_code, 201)
        copy = response.json()["data"]
        self.assertNotEqual(copy["_id"], data["_id"])
        self.assertEqual(copy["title"], "Backend Engineer (copy)")
        self.assertEqual(copy["experience"], data["experience"])
        self.assertEqual(copy["skills"], data["skills"])


class OwnershipTests(ResumeTestCase):
    def test_other_users_resume_is_invisible(self) -> None:
        data = self.create()
        intruder = authenticate(APIClient(), self.other)
        resume_path = f"/api/resumes/{data['_id']}"
        self.assertEqual(intruder.get(resume_path).status_code, 404)
        self.assertEqual(intruder.put(resume_path, {"title": "Hacked"}, format="json").status_code, 404)
        self.assertEqual(intruder.delete(resume_path).status_code, 404)
        self.assertEqual(intruder.post(f"{resume_path}/duplicate").status_code, 404)
        self.assertEqual(intruder.get("/api/resumes").json()["data"], [])
        self.assertEqual(Resume.objects.get(pk=data["_id"]).title, "Backend Engineer")

    def test_anonymous_requests_are_rejected(self) -> None:
        response = APIClient().get("/api/resumes")
        self.assertEqual(response.status_code, 401)


class VersionTests(ResumeTestCase):
    def test_save_and_restore_a_version(self) -> None:
        data = self.create()
        saved = self.client.post(f"/api/resumes/{data['_id']}/versions").json()["data"]
        self.assertEqual(len(saved["versions"]), 1)
        snapshot_id = saved["versions"][0]["snapshotId"]

        self.client.put(
            f"/api/resumes/{data['_id']}", {"professionalSummary": "Changed my mind."}, format="json"
        )
        restored = self.client.post(f"/api/resumes/{data['_id']}/versions/{snapshot_id}/restore")
        self.assertEqual(restored.status_code, 200)
        self.assertEqual(
            restored.json()["data"]["professionalSummary"], "Engineer who ships reliable services."
        )

    def test_only_the_ten_most_recent_versions_are_kept(self) -> None:
        resume = Resume.objects.create(user=self.owner, title="Versioned")
        for index in range(12):
            resume.title = f"Draft {index}"
            resume.save()
            save_version(resume)
        resume.refresh_from_db()
        self.assertEqual(len(resume.versions), 10)
        self.assertEqual(resume.versions[-1].title, "Draft 11")

    def test_restoring_unknown_version_is_not_found(self) -> None:
        data = self.create()
        response = self.client.post(f"/api/resumes/{data['_id']}/versions/{'a' * 24}/restore")
        self.assertEqual(response.status_code, 404)

    def test_corrupted_snapshot_cannot_be_restored(self) -> None:
        resume = Resume.objects.create(user=self.owner, title="Broken")
        from resumes.models import ResumeSnapshot

        bad = ResumeSnapshot(
            snapshot_id="b" * 24, saved_at="2026-01-01T00:00:00.000Z", title="x", content="{not json"
        )
        resume.versions = [bad]
        resume.save()
        response = self.client.post(f"/api/resumes/{resume.pk}/versions/{'b' * 24}/restore")
        self.assertEqual(response.status_code, 422)

    def test_restore_ignores_unknown_fields_in_stored_content(self) -> None:
        import json

        resume = Resume.objects.create(user=self.owner, title="Injected")
        from resumes.models import ResumeSnapshot

        content = json.dumps(
            {"professionalSummary": "Safe", "userId": "000000000000000000000000", "isAdmin": True}
        )
        resume.versions = [
            ResumeSnapshot(
                snapshot_id="c" * 24, saved_at="2026-01-01T00:00:00.000Z", title="t", content=content
            )
        ]
        resume.save()
        response = self.client.post(f"/api/resumes/{resume.pk}/versions/{'c' * 24}/restore")
        self.assertEqual(response.status_code, 200)
        resume.refresh_from_db()
        self.assertEqual(resume.user_id, self.owner.pk)
        self.assertEqual(resume.professional_summary, "Safe")


class PublicAndStarterTests(ResumeTestCase):
    def test_private_resume_is_not_publicly_visible(self) -> None:
        data = self.create()
        response = APIClient().get(f"/api/resumes/public/{data['_id']}")
        self.assertEqual(response.status_code, 404)

    def test_public_resume_is_visible_without_versions(self) -> None:
        data = self.create({**valid_create_body(), "isPublic": True})
        save_version(Resume.objects.get(pk=data["_id"]))
        response = APIClient().get(f"/api/resumes/public/{data['_id']}")
        self.assertEqual(response.status_code, 200)
        body = response.json()["data"]
        self.assertEqual(body["title"], "Backend Engineer")
        self.assertNotIn("versions", body)

    def test_starters_are_public_and_complete(self) -> None:
        response = APIClient().get("/api/resumes/starters")
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(len(data["starters"]), 6)
        self.assertEqual(len(data["benchmarkJobs"]), 6)


class AtsEndpointTests(ResumeTestCase):
    def test_ats_endpoint_scores_the_callers_resume(self) -> None:
        data = self.create()
        response = self.client.post(
            f"/api/resumes/{data['_id']}/ats-analyze",
            {"jobDescription": "We need Python and Django engineers who know Kubernetes."},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()["data"]
        self.assertIn("Python", result["matchedKeywords"])
        self.assertIn("Kubernetes", result["missingKeywords"])

    def test_short_job_description_is_rejected(self) -> None:
        data = self.create()
        response = self.client.post(
            f"/api/resumes/{data['_id']}/ats-analyze", {"jobDescription": "short"}, format="json"
        )
        self.assertEqual(response.status_code, 400)


@override_settings(RESUME_UPLOAD_MAX_BYTES=2048)
class PdfUploadTests(ResumeTestCase):
    def upload(self, content: bytes, name: str = "cv.pdf") -> Any:
        from django.core.files.uploadedfile import SimpleUploadedFile

        return self.client.post(
            "/api/resumes/upload", {"file": SimpleUploadedFile(name, content, "application/pdf")}
        )

    def test_text_pdf_is_imported_as_a_resume(self) -> None:
        pdf = build_pdf(
            [
                "Jane Doe",
                "jane.doe@example.com | +1 415 555 0134",
                "Experience",
                "Senior Engineer | Acme Corp | 2021 - Present",
                "- Architected a platform on AWS",
                "Skills",
                "Python, Django, PostgreSQL",
            ]
        )
        response = self.upload(pdf)
        self.assertEqual(response.status_code, 201, response.content)
        data = response.json()["data"]
        self.assertEqual(data["title"], "Jane Doe's Resume")
        self.assertEqual(data["template"], "modern")
        self.assertEqual(data["personalInfo"]["email"], "jane.doe@example.com")
        self.assertIn("Python", data["skills"])

    def test_missing_file_is_rejected(self) -> None:
        response = self.client.post("/api/resumes/upload", {}, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "No PDF file uploaded")

    def test_non_pdf_content_is_rejected(self) -> None:
        response = self.upload(b"just some text, not a pdf")
        self.assertEqual(response.status_code, 400)

    def test_oversized_upload_is_rejected(self) -> None:
        response = self.upload(build_pdf(["x" * 3000]))
        self.assertEqual(response.status_code, 413)

    def test_scanned_or_blank_pdf_is_unprocessable(self) -> None:
        response = self.upload(build_pdf([]))
        self.assertEqual(response.status_code, 422)
        self.assertIn("image scan", response.json()["message"])
