"""
Database-level guardrails: MongoDB ``$jsonSchema`` validators.

Django enforces rules in the application layer. These validators enforce the same
document shape inside the database, so writes from other tools (scripts, the
Mongo shell, a future service) cannot corrupt documents. Install or refresh them
with ``python manage.py setup_mongodb``. The command is idempotent.
"""

from __future__ import annotations

from typing import Any

from pymongo.database import Database

TEMPLATE_IDS = ["classic", "modern", "minimal", "executive", "home_college", "general_template"]

_EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
_OPTIONAL_EMAIL_PATTERN = r"^$|^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
_OPTIONAL_URL_PATTERN = r"^$|^https?://.*"

USERS_VALIDATOR: dict[str, Any] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "email", "password"],
        "properties": {
            "name": {"bsonType": "string", "minLength": 1, "maxLength": 120},
            "email": {
                "bsonType": "string",
                "pattern": _EMAIL_PATTERN,
                "description": "Valid email address is required",
            },
            "password": {
                "bsonType": "string",
                "minLength": 20,
                "description": "Must be a salted password hash",
            },
            "refreshTokens": {
                "bsonType": "array",
                "maxItems": 5,
                "items": {"bsonType": "string"},
            },
        },
    }
}

RESUMES_VALIDATOR: dict[str, Any] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["userId", "title", "isPublic", "template", "accentColor"],
        "properties": {
            "userId": {"bsonType": "objectId"},
            "title": {"bsonType": "string", "minLength": 1, "maxLength": 100},
            "isPublic": {"bsonType": "bool"},
            "template": {"enum": TEMPLATE_IDS},
            "accentColor": {"bsonType": "string", "pattern": r"^#[0-9A-Fa-f]{6}$"},
            "professionalSummary": {"bsonType": "string", "maxLength": 2000},
            "personalInfo": {
                "bsonType": "object",
                "properties": {
                    "email": {"bsonType": "string", "pattern": _OPTIONAL_EMAIL_PATTERN},
                    "linkedin": {"bsonType": "string", "pattern": _OPTIONAL_URL_PATTERN},
                    "github": {"bsonType": "string", "pattern": _OPTIONAL_URL_PATTERN},
                },
            },
            "experience": {
                "bsonType": "array",
                "maxItems": 20,
                "items": {"bsonType": "object", "required": ["id", "company", "position"]},
            },
            "education": {
                "bsonType": "array",
                "maxItems": 10,
                "items": {"bsonType": "object", "required": ["id", "institution", "degree"]},
            },
            "projects": {
                "bsonType": "array",
                "maxItems": 20,
                "items": {"bsonType": "object", "required": ["id", "name"]},
            },
            "skills": {
                "bsonType": "array",
                "maxItems": 50,
                "items": {"bsonType": "string", "minLength": 1, "maxLength": 50},
            },
            "versions": {"bsonType": "array", "maxItems": 10},
        },
    }
}

VALIDATORS: dict[str, dict[str, Any]] = {
    "users": USERS_VALIDATOR,
    "resumes": RESUMES_VALIDATOR,
}


def install_validator(db: Database, collection: str, validator: dict[str, Any]) -> str:
    """Create the collection with the validator, or update the validator if it exists."""
    options: dict[str, Any] = {
        "validator": validator,
        "validationLevel": "strict",
        "validationAction": "error",
    }
    if collection in db.list_collection_names():
        db.command("collMod", collection, **options)
        return "updated"
    db.create_collection(collection, **options)
    return "created"


def _has_index_on(collection: Any, keys: list[tuple[str, int]]) -> bool:
    wanted = dict(keys)
    return any(dict(info["key"]) == wanted for info in collection.index_information().values())


def ensure_indexes(db: Database) -> list[str]:
    """
    Create the indexes the application relies on, unless an index with the same key exists.

    Databases written by the original service already have equivalent indexes under
    different names. Checking by key avoids creating duplicates, which MongoDB would refuse
    anyway when the names differ but the keys match.
    """
    created: list[str] = []
    wanted: list[tuple[str, list[tuple[str, int]], dict[str, Any]]] = [
        ("users", [("email", 1)], {"unique": True}),
        ("resumes", [("userId", 1), ("updatedAt", -1)], {}),
    ]
    for name, keys, options in wanted:
        collection = db.get_collection(name)
        if not _has_index_on(collection, keys):
            collection.create_index(keys, **options)
            created.append(f"{name}{keys}")
    return created
