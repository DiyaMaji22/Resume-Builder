"""Runs the analytics pipelines inside the application process (no subprocess)."""

from __future__ import annotations

from typing import Any

from django.db import connections

from accounts.models import User
from analytics import pipelines
from resumes.models import Resume


def _collection(model: type[Any]) -> Any:
    return connections[model.objects.db].get_collection(model._meta.db_table)


def collect_analytics() -> dict[str, Any]:
    resumes = _collection(Resume)
    users = _collection(User)

    return {
        "templateUsage": list(resumes.aggregate(pipelines.template_usage())),
        "topSkills": list(resumes.aggregate(pipelines.top_skills())),
        "resumesPerUser": list(resumes.aggregate(pipelines.resumes_per_user(users.name))),
        "completenessScores": list(resumes.aggregate(pipelines.completeness_scores())),
        "monthlyVelocity": list(resumes.aggregate(pipelines.monthly_velocity())),
        "summary": {
            "totalUsers": users.count_documents({}),
            "totalResumes": resumes.count_documents({}),
            "publicResumes": resumes.count_documents({"isPublic": True}),
        },
        "engine": "MongoDB aggregation pipeline",
    }
