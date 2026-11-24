"""
Backfills resume fields missing from documents written by the original Node service.

Mongoose applied defaults when it wrote documents, but a document imported or edited by
other tools may omit fields. Django would read those as None and fail on list fields, so
each missing field gets the default a new resume would have.
"""

from django.db import migrations

DEFAULTS = {
    "title": "Untitled Resume",
    "isPublic": False,
    "template": "classic",
    "accentColor": "#2563EB",
    "professionalSummary": "",
    "personalInfo": {
        "fullName": "",
        "email": "",
        "phone": "",
        "location": "",
        "linkedin": "",
        "website": "",
        "github": "",
        "image": "",
    },
    "experience": [],
    "education": [],
    "projects": [],
    "certifications": [],
    "skills": [],
    "versions": [],
}


def backfill_resume_fields(apps, schema_editor):
    resumes = schema_editor.connection.get_collection("resumes")
    for field, value in DEFAULTS.items():
        resumes.update_many({field: None}, {"$set": {field: value}})


class Migration(migrations.Migration):
    dependencies = [("resumes", "0001_initial"), ("accounts", "0003_backfill_account_fields")]

    operations = [
        migrations.RunPython(backfill_resume_fields, migrations.RunPython.noop),
    ]
