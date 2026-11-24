"""
MongoDB aggregation pipelines behind the analytics dashboard.

Stage-for-stage equivalents of the original PyMongo script. Field names are the stored
(camelCase) keys, so these run unchanged against existing data.
"""

from __future__ import annotations

from typing import Any

Pipeline = list[dict[str, Any]]


def template_usage() -> Pipeline:
    return [
        {
            "$group": {
                "_id": "$template",
                "totalResumes": {"$sum": 1},
                "publicResumes": {"$sum": {"$cond": ["$isPublic", 1, 0]}},
            }
        },
        {"$sort": {"totalResumes": -1, "_id": 1}},
    ]


def top_skills(limit: int = 5) -> Pipeline:
    return [
        {"$unwind": "$skills"},
        {"$group": {"_id": {"$toLower": "$skills"}, "frequency": {"$sum": 1}}},
        {"$sort": {"frequency": -1, "_id": 1}},
        {"$limit": limit},
    ]


def resumes_per_user(users_collection: str) -> Pipeline:
    return [
        {"$group": {"_id": "$userId", "resumeCount": {"$sum": 1}}},
        {
            "$lookup": {
                "from": users_collection,
                "localField": "_id",
                "foreignField": "_id",
                "as": "owner",
            }
        },
        {"$unwind": "$owner"},
        {"$project": {"_id": 0, "userName": "$owner.name", "resumeCount": 1}},
        {"$sort": {"resumeCount": -1, "userName": 1}},
    ]


def completeness_scores(limit: int = 5) -> Pipeline:
    """Scores each resume from 0 to 6: experience, projects, skills, and summary, each capped."""
    return [
        {
            "$project": {
                "_id": 0,
                "title": 1,
                "expCount": {"$size": "$experience"},
                "projCount": {"$size": "$projects"},
                "skillCount": {"$size": "$skills"},
                "hasSummary": {"$ne": ["$professionalSummary", ""]},
            }
        },
        {
            "$addFields": {
                "completenessScore": {
                    "$add": [
                        {"$min": ["$expCount", 3]},
                        {"$min": ["$projCount", 3]},
                        {"$min": [{"$floor": {"$divide": ["$skillCount", 3]}}, 3]},
                        {"$cond": ["$hasSummary", 1, 0]},
                    ]
                }
            }
        },
        {"$sort": {"completenessScore": -1, "title": 1}},
        {"$limit": limit},
    ]


def monthly_velocity() -> Pipeline:
    return [
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m", "date": "$createdAt"}},
                "resumesCreated": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
    ]
