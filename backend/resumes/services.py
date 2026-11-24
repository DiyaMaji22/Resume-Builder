"""
Resume use cases: creation, editing, duplication, version history and PDF import.

Ownership checks happen in the views (queries are always scoped to the requesting
user). The services assume the resume they receive is already authorised.
"""

from __future__ import annotations

import copy
import json
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from bson import ObjectId

from accounts.models import User
from core.exceptions import NotFoundError, UnprocessableError
from resumes.constants import (
    DEFAULT_ACCENT_COLOR,
    IMPORTED_TEMPLATE,
    MAX_VERSIONS,
)
from resumes.models import (
    CertificationEntry,
    EducationEntry,
    ExperienceEntry,
    ProjectEntry,
    Resume,
    ResumeSnapshot,
)
from resumes.pdf_import import extract_text, parse_resume_text
from resumes.serializers import (
    ResumeCreateSerializer,
    ResumeSerializer,
    ResumeWriteSerializer,
)

# Scalar API keys -> model attribute names.
_SCALAR_FIELDS = {
    "title": "title",
    "is_public": "is_public",
    "template": "template",
    "accent_color": "accent_color",
    "professional_summary": "professional_summary",
}

# Section API keys -> the embedded model used for each item.
_SECTION_MODELS: dict[str, type] = {
    "experience": ExperienceEntry,
    "education": EducationEntry,
    "projects": ProjectEntry,
    "certifications": CertificationEntry,
}

# What a version snapshot captures. Matches the keys the original service stored.
_SNAPSHOT_KEYS = (
    "template",
    "accentColor",
    "professionalSummary",
    "personalInfo",
    "experience",
    "education",
    "projects",
    "certifications",
    "skills",
)

_PDF_IMPORT_UNREADABLE = (
    "Unable to extract readable text from this PDF. Please ensure it is not an image scan."
)


def apply_changes(resume: Resume, data: Mapping[str, Any]) -> None:
    """Apply validated input to a resume in memory. Callers decide when to save."""
    for key, attr in _SCALAR_FIELDS.items():
        if key in data:
            setattr(resume, attr, data[key])

    # Personal info is merged field by field, so a partial update does not wipe the rest.
    if "personal_info" in data:
        for attr, value in data["personal_info"].items():
            setattr(resume.personal_info, attr, value)

    for key, model in _SECTION_MODELS.items():
        if key in data:
            setattr(resume, key, [model(**item) for item in data[key]])

    if "skills" in data:
        resume.skills = list(data["skills"])


def create_resume(user: User, data: Mapping[str, Any]) -> Resume:
    resume = Resume(user=user)
    apply_changes(resume, data)
    resume.save()
    return resume


def update_resume(resume: Resume, data: Mapping[str, Any]) -> Resume:
    apply_changes(resume, data)
    resume.save()
    return resume


def delete_resume(resume: Resume) -> None:
    resume.delete()


def duplicate_resume(source: Resume) -> Resume:
    copy_ = Resume(
        user=source.user,
        title=f"{source.title} (copy)",
        is_public=source.is_public,
        template=source.template,
        accent_color=source.accent_color,
        professional_summary=source.professional_summary,
        personal_info=copy.deepcopy(source.personal_info),
        experience=copy.deepcopy(source.experience),
        education=copy.deepcopy(source.education),
        projects=copy.deepcopy(source.projects),
        certifications=copy.deepcopy(source.certifications),
        skills=list(source.skills),
    )
    copy_.save()
    return copy_


def _snapshot_content(resume: Resume) -> str:
    serialized = ResumeSerializer(resume).data
    payload = {key: serialized[key] for key in _SNAPSHOT_KEYS}
    return json.dumps(payload, default=str)


def save_version(resume: Resume) -> Resume:
    """Record the current content as a new version, keeping only the most recent MAX_VERSIONS."""
    snapshot = ResumeSnapshot(
        snapshot_id=str(ObjectId()),
        saved_at=datetime.now(tz=UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        title=resume.title,
        content=_snapshot_content(resume),
    )
    kept = list(resume.versions)[-(MAX_VERSIONS - 1) :]
    resume.versions = [*kept, snapshot]
    resume.save(update_fields=["versions", "updated_at"])
    return resume


def restore_version(resume: Resume, snapshot_id: str) -> Resume:
    snapshot = next((v for v in resume.versions if v.snapshot_id == snapshot_id), None)
    if snapshot is None:
        raise NotFoundError("Version not found")

    try:
        content: dict[str, Any] = json.loads(snapshot.content)
    except ValueError as exc:
        raise UnprocessableError("This saved version is corrupted and cannot be restored.") from exc
    content["title"] = snapshot.title

    # Restoring goes through the same validation as an edit. The original code wrote the
    # stored JSON straight into the document, which would also have accepted unknown fields.
    serializer = ResumeWriteSerializer(data=content, partial=True)
    if not serializer.is_valid():
        raise UnprocessableError("This saved version is no longer valid.", errors=serializer.errors)
    return update_resume(resume, serializer.validated_data)


def import_resume_from_pdf(user: User, pdf_bytes: bytes, original_filename: str) -> Resume:
    text = extract_text(pdf_bytes)
    if not text.strip():
        raise UnprocessableError(_PDF_IMPORT_UNREADABLE)

    parsed = parse_resume_text(text, original_filename)
    parsed["template"] = IMPORTED_TEMPLATE.value
    parsed["accentColor"] = DEFAULT_ACCENT_COLOR

    serializer = ResumeCreateSerializer(data=parsed)
    if not serializer.is_valid():
        raise UnprocessableError("The parsed resume data could not be saved.", errors=serializer.errors)
    return create_resume(user, serializer.validated_data)


def public_resume_queryset_filter(resume_id: str) -> dict[str, Any]:
    return {"pk": resume_id, "is_public": True}
