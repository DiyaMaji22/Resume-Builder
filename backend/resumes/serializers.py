"""
Request validation and response shapes for resumes.

Field names are camelCase on the wire, matching the client. ``source=`` maps them to
the snake_case attributes of the models. Validated input keys are the model attribute
names, so services can apply them directly.
"""

from __future__ import annotations

import re
from typing import Any, ClassVar

from rest_framework import serializers

from core.serializer_fields import IsoDateTimeField
from resumes import constants as c
from resumes.constants import TemplateId

_URL_PATTERN = re.compile(r"^https?://\S+$")
_HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


class OptionalUrlField(serializers.CharField):
    """A URL that may be empty. Non-empty values must start with http:// or https://."""

    default_error_messages: ClassVar[dict[str, str]] = {"invalid": "Must be a valid URL or empty."}

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("allow_blank", True)
        kwargs.setdefault("max_length", c.MAX_URL)
        kwargs.setdefault("required", False)
        super().__init__(**kwargs)

    def run_validation(self, data: Any = serializers.empty) -> str:
        value: str = super().run_validation(data)
        if value and not _URL_PATTERN.match(value):
            self.fail("invalid")
        return value


class PersonalInfoSerializer(serializers.Serializer):
    fullName = serializers.CharField(
        source="full_name", max_length=c.MAX_NAME, allow_blank=True, required=False
    )
    email = serializers.EmailField(max_length=254, allow_blank=True, required=False)
    phone = serializers.CharField(max_length=30, allow_blank=True, required=False)
    location = serializers.CharField(max_length=100, allow_blank=True, required=False)
    linkedin = OptionalUrlField()
    website = OptionalUrlField()
    github = OptionalUrlField()
    image = serializers.CharField(max_length=c.MAX_URL, allow_blank=True, required=False)


class ExperienceSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=64)
    company = serializers.CharField(max_length=120, allow_blank=True, required=False)
    position = serializers.CharField(max_length=120, allow_blank=True, required=False)
    startDate = serializers.CharField(source="start_date", max_length=32, allow_blank=True, required=False)
    endDate = serializers.CharField(source="end_date", max_length=32, allow_blank=True, required=False)
    isCurrent = serializers.BooleanField(source="is_current", required=False)
    description = serializers.CharField(max_length=c.MAX_DESCRIPTION, allow_blank=True, required=False)


class EducationSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=64)
    institution = serializers.CharField(max_length=120, allow_blank=True, required=False)
    degree = serializers.CharField(max_length=120, allow_blank=True, required=False)
    field = serializers.CharField(source="field_of_study", max_length=120, allow_blank=True, required=False)
    graduationDate = serializers.CharField(
        source="graduation_date", max_length=32, allow_blank=True, required=False
    )
    gpa = serializers.CharField(max_length=10, allow_blank=True, required=False)


class ProjectSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=64)
    name = serializers.CharField(max_length=c.MAX_NAME, allow_blank=True, required=False)
    type = serializers.CharField(max_length=60, allow_blank=True, required=False)
    description = serializers.CharField(max_length=1000, allow_blank=True, required=False)
    url = OptionalUrlField()
    technologies = serializers.ListField(
        child=serializers.CharField(max_length=50),
        max_length=c.MAX_PROJECT_TECHNOLOGIES,
        required=False,
    )


class CertificationSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=64)
    name = serializers.CharField(max_length=c.MAX_NAME, allow_blank=True, required=False)
    issuer = serializers.CharField(max_length=c.MAX_NAME, allow_blank=True, required=False)
    date = serializers.CharField(max_length=32, allow_blank=True, required=False)
    url = OptionalUrlField()


class ResumeWriteSerializer(serializers.Serializer):
    """Fields accepted on update. Every field is optional (PATCH-style semantics)."""

    title = serializers.CharField(max_length=c.MAX_TITLE, required=False)
    isPublic = serializers.BooleanField(source="is_public", required=False)
    template = serializers.ChoiceField(choices=TemplateId.choices, required=False)
    accentColor = serializers.RegexField(
        _HEX_COLOR_PATTERN, source="accent_color", max_length=7, required=False
    )
    professionalSummary = serializers.CharField(
        source="professional_summary", max_length=c.MAX_SUMMARY, allow_blank=True, required=False
    )
    personalInfo = PersonalInfoSerializer(source="personal_info", required=False)
    experience = ExperienceSerializer(many=True, required=False, max_length=c.MAX_EXPERIENCE)
    education = EducationSerializer(many=True, required=False, max_length=c.MAX_EDUCATION)
    projects = ProjectSerializer(many=True, required=False, max_length=c.MAX_PROJECTS)
    certifications = CertificationSerializer(many=True, required=False, max_length=c.MAX_CERTIFICATIONS)
    skills = serializers.ListField(
        child=serializers.CharField(max_length=c.MAX_SKILL, min_length=1),
        max_length=c.MAX_SKILLS,
        required=False,
    )


class ResumeCreateSerializer(ResumeWriteSerializer):
    title = serializers.CharField(max_length=c.MAX_TITLE)


class ResumeSnapshotSerializer(serializers.Serializer):
    snapshotId = serializers.CharField(source="snapshot_id", read_only=True)
    savedAt = serializers.CharField(source="saved_at", read_only=True)
    title = serializers.CharField(read_only=True)
    content = serializers.CharField(read_only=True)


class ResumeListItemSerializer(serializers.Serializer):
    """A resume without its version history. Used for lists and public pages."""

    _id = serializers.CharField(source="pk", read_only=True)
    userId = serializers.CharField(source="user_id", read_only=True)
    title = serializers.CharField(read_only=True)
    isPublic = serializers.BooleanField(source="is_public", read_only=True)
    template = serializers.CharField(read_only=True)
    accentColor = serializers.CharField(source="accent_color", read_only=True)
    professionalSummary = serializers.CharField(source="professional_summary", read_only=True)
    personalInfo = PersonalInfoSerializer(source="personal_info", read_only=True)
    experience = ExperienceSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    skills = serializers.ListField(child=serializers.CharField(), read_only=True)
    createdAt = IsoDateTimeField(source="created_at")
    updatedAt = IsoDateTimeField(source="updated_at")


class ResumeSerializer(ResumeListItemSerializer):
    """The full resume, including version history."""

    versions = ResumeSnapshotSerializer(many=True, read_only=True)


class ATSAnalyzeSerializer(serializers.Serializer):
    jobDescription = serializers.CharField(min_length=10, max_length=20_000)


class PdfUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
