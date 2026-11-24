"""Domain constants shared by the models, serializers, and import parser."""

from django.db import models


class TemplateId(models.TextChoices):
    CLASSIC = "classic", "Classic"
    MODERN = "modern", "Modern"
    MINIMAL = "minimal", "Minimal"
    EXECUTIVE = "executive", "Executive"
    HOME_COLLEGE = "home_college", "Home / College"
    GENERAL = "general_template", "General"


DEFAULT_TEMPLATE = TemplateId.CLASSIC
DEFAULT_ACCENT_COLOR = "#2563EB"
IMPORTED_TEMPLATE = TemplateId.MODERN

MAX_VERSIONS = 10

# Collection limits, enforced by serializers and by the $jsonSchema validator.
MAX_EXPERIENCE = 20
MAX_EDUCATION = 10
MAX_PROJECTS = 20
MAX_CERTIFICATIONS = 20
MAX_SKILLS = 50
MAX_PROJECT_TECHNOLOGIES = 20

MAX_TITLE = 100
MAX_SUMMARY = 2000
MAX_DESCRIPTION = 2000
MAX_NAME = 120
MAX_URL = 2048
MAX_SKILL = 50
