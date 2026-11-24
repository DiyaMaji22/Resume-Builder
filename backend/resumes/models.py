"""
Resume documents.

Each resume is one MongoDB document. Nested sections (experience, education, ...)
are embedded in that document rather than stored in separate collections, because
they are always read and written together. ``db_column`` keeps the camelCase keys
used by the original Mongoose schema, so existing documents load without migration.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django_mongodb_backend.fields import ArrayField, EmbeddedModelArrayField, EmbeddedModelField
from django_mongodb_backend.models import EmbeddedModel

from resumes.constants import DEFAULT_ACCENT_COLOR, DEFAULT_TEMPLATE, MAX_SKILL, MAX_URL, TemplateId


class PersonalInfo(EmbeddedModel):
    full_name = models.CharField(max_length=120, blank=True, default="", db_column="fullName")
    email = models.CharField(max_length=254, blank=True, default="")
    phone = models.CharField(max_length=30, blank=True, default="")
    location = models.CharField(max_length=100, blank=True, default="")
    linkedin = models.CharField(max_length=MAX_URL, blank=True, default="")
    website = models.CharField(max_length=MAX_URL, blank=True, default="")
    github = models.CharField(max_length=MAX_URL, blank=True, default="")
    image = models.CharField(max_length=MAX_URL, blank=True, default="")

    class Meta:
        # Embedded documents live inside their parent resume; they have no collection of their own.
        managed = False


class ExperienceEntry(EmbeddedModel):
    id = models.CharField(max_length=64, primary_key=True)
    company = models.CharField(max_length=120, blank=True, default="")
    position = models.CharField(max_length=120, blank=True, default="")
    start_date = models.CharField(max_length=32, blank=True, default="", db_column="startDate")
    end_date = models.CharField(max_length=32, blank=True, default="", db_column="endDate")
    is_current = models.BooleanField(default=False, db_column="isCurrent")
    description = models.CharField(max_length=2000, blank=True, default="")

    class Meta:
        # Embedded documents live inside their parent resume; they have no collection of their own.
        managed = False


class EducationEntry(EmbeddedModel):
    id = models.CharField(max_length=64, primary_key=True)
    institution = models.CharField(max_length=120, blank=True, default="")
    degree = models.CharField(max_length=120, blank=True, default="")
    field_of_study = models.CharField(max_length=120, blank=True, default="", db_column="field")
    graduation_date = models.CharField(max_length=32, blank=True, default="", db_column="graduationDate")
    gpa = models.CharField(max_length=10, blank=True, default="")

    class Meta:
        # Embedded documents live inside their parent resume; they have no collection of their own.
        managed = False


class ProjectEntry(EmbeddedModel):
    id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=120, blank=True, default="")
    type = models.CharField(max_length=60, blank=True, default="")
    description = models.CharField(max_length=1000, blank=True, default="")
    url = models.CharField(max_length=MAX_URL, blank=True, default="")
    technologies = ArrayField(models.CharField(max_length=50), default=list, blank=True)

    class Meta:
        # Embedded documents live inside their parent resume; they have no collection of their own.
        managed = False


class CertificationEntry(EmbeddedModel):
    id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=120, blank=True, default="")
    issuer = models.CharField(max_length=120, blank=True, default="")
    date = models.CharField(max_length=32, blank=True, default="")
    url = models.CharField(max_length=MAX_URL, blank=True, default="")

    class Meta:
        # Embedded documents live inside their parent resume; they have no collection of their own.
        managed = False


class ResumeSnapshot(EmbeddedModel):
    """A saved version. ``content`` holds the section data as JSON, as the original service did."""

    snapshot_id = models.CharField(max_length=24, db_column="snapshotId")
    saved_at = models.CharField(max_length=40, db_column="savedAt")
    title = models.CharField(max_length=100)
    content = models.TextField()

    class Meta:
        # Embedded documents live inside their parent resume; they have no collection of their own.
        managed = False


class Resume(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resumes",
        db_column="userId",
    )
    title = models.CharField(max_length=100, default="Untitled Resume")
    is_public = models.BooleanField(default=False, db_column="isPublic")
    template = models.CharField(max_length=32, choices=TemplateId.choices, default=DEFAULT_TEMPLATE)
    accent_color = models.CharField(max_length=7, default=DEFAULT_ACCENT_COLOR, db_column="accentColor")
    professional_summary = models.CharField(
        max_length=2000, blank=True, default="", db_column="professionalSummary"
    )
    personal_info = EmbeddedModelField(PersonalInfo, default=PersonalInfo, db_column="personalInfo")
    experience = EmbeddedModelArrayField(ExperienceEntry, default=list, blank=True, db_column="experience")
    education = EmbeddedModelArrayField(EducationEntry, default=list, blank=True, db_column="education")
    projects = EmbeddedModelArrayField(ProjectEntry, default=list, blank=True, db_column="projects")
    certifications = EmbeddedModelArrayField(
        CertificationEntry, default=list, blank=True, db_column="certifications"
    )
    skills = ArrayField(models.CharField(max_length=MAX_SKILL), default=list, blank=True, db_column="skills")
    versions = EmbeddedModelArrayField(ResumeSnapshot, default=list, blank=True, db_column="versions")
    created_at = models.DateTimeField(auto_now_add=True, db_column="createdAt")
    updated_at = models.DateTimeField(auto_now=True, db_column="updatedAt")

    class Meta:
        db_table = "resumes"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "-updated_at"], name="resumes_user_updated_idx"),
        ]

    def __str__(self) -> str:
        return self.title
