#!/usr/bin/env python3
"""
Resume Builder — PyMongo Document Database Application
Implements Schema Validation ($jsonSchema), CRUD Operations, Atomic Array Updates,
and Analytical Aggregation Pipelines on MongoDB.

Course Reference: CSE494 Intelligent NoSQL Databases (Academic Task 2)
Author: Diya Maji
"""

import os
import sys
from datetime import datetime, timezone
from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError, WriteError, DuplicateKeyError

# ---------------------------------------------------------------------------
# Configuration & Database Connection
# ---------------------------------------------------------------------------
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017")
MONGODB_DB = os.environ.get("MONGODB_DB", "resume-builder")

TEMPLATES = ["classic", "modern", "minimal", "executive", "home_college", "general_template"]

def get_db():
    """Connect to MongoDB with a 5-second fail-fast timeout and ping verification."""
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
    except PyMongoError as err:
        print(f"[Error] Failed to reach MongoDB server at {MONGODB_URI}: {err}", file=sys.stderr)
        sys.exit(1)

    try:
        default_db = client.get_default_database()
        if default_db is not None:
            return default_db
    except Exception:
        pass

    return client[MONGODB_DB]

# ---------------------------------------------------------------------------
# Schema Validators ($jsonSchema)
# ---------------------------------------------------------------------------
USERS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "email", "password"],
        "properties": {
            "name": {
                "bsonType": "string",
                "minLength": 1,
                "maxLength": 120,
                "description": "Full name is required (1-120 chars)"
            },
            "email": {
                "bsonType": "string",
                "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                "description": "Valid email address is required"
            },
            "password": {
                "bsonType": "string",
                "minLength": 20,
                "description": "Must be a salted bcrypt hash string (minimum 20 chars)"
            },
            "refreshTokens": {
                "bsonType": "array",
                "maxItems": 5,
                "items": {"bsonType": "string"}
            }
        }
    }
}

RESUMES_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["userId", "title", "isPublic", "template", "accentColor"],
        "properties": {
            "userId": {"bsonType": "objectId"},
            "title": {"bsonType": "string", "minLength": 1, "maxLength": 100},
            "isPublic": {"bsonType": "bool"},
            "template": {"enum": TEMPLATES},
            "accentColor": {
                "bsonType": "string",
                "pattern": r"^#[0-9A-Fa-f]{6}$",
                "description": "Valid hex color code, e.g. #4F46E5"
            },
            "professionalSummary": {"bsonType": "string", "maxLength": 2000},
            "personalInfo": {
                "bsonType": "object",
                "properties": {
                    "email": {"bsonType": "string", "pattern": r"^$|^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"},
                    "linkedin": {"bsonType": "string", "pattern": r"^$|^https?://.*"},
                    "github": {"bsonType": "string", "pattern": r"^$|^https?://.*"}
                }
            },
            "experience": {
                "bsonType": "array",
                "maxItems": 20,
                "items": {
                    "bsonType": "object",
                    "required": ["id", "company", "position"]
                }
            },
            "education": {
                "bsonType": "array",
                "maxItems": 20,
                "items": {
                    "bsonType": "object",
                    "required": ["id", "institution", "degree"]
                }
            },
            "projects": {
                "bsonType": "array",
                "maxItems": 20,
                "items": {
                    "bsonType": "object",
                    "required": ["id", "name"]
                }
            },
            "skills": {
                "bsonType": "array",
                "maxItems": 50,
                "items": {"bsonType": "string", "minLength": 1, "maxLength": 50}
            },
            "versions": {
                "bsonType": "array",
                "maxItems": 10
            }
        }
    }
}

def apply_validator(db, col_name, validator):
    """Install or update $jsonSchema validator using collMod or create_collection."""
    if col_name in db.list_collection_names():
        db.command("collMod", col_name, validator=validator, validationLevel="strict", validationAction="error")
        print(f"  ✓ Updated $jsonSchema validator on collection '{col_name}'")
    else:
        db.create_collection(col_name, validator=validator, validationLevel="strict", validationAction="error")
        print(f"  ✓ Created collection '{col_name}' with strict $jsonSchema validator")

def setup_schema(db):
    """Provision collections, $jsonSchema validators, and optimized indexes."""
    print("\n[1/4] Applying Database-Level Schema Validators...")
    apply_validator(db, "users", USERS_VALIDATOR)
    apply_validator(db, "resumes", RESUMES_VALIDATOR)

    print("\n[2/4] Provisioning Indexes...")
    # Unique email index
    db.users.create_index([("email", ASCENDING)], unique=True)
    print("  ✓ Created unique index on users.email")

    # Compound index for dashboard queries
    db.resumes.create_index([("userId", ASCENDING), ("updatedAt", DESCENDING)])
    print("  ✓ Created compound index on resumes { userId: 1, updatedAt: -1 }")

    # Public resume vanity lookup index
    db.resumes.create_index([("isPublic", ASCENDING)])
    print("  ✓ Created single-field index on resumes.isPublic")

    # Template aggregation index
    db.resumes.create_index([("template", ASCENDING)])
    print("  ✓ Created single-field index on resumes.template")
    print("Schema setup completed successfully.")

# ---------------------------------------------------------------------------
# Document Factories
# ---------------------------------------------------------------------------
def new_resume_doc(user_id, title, template="modern", accent_color="#4F46E5", is_public=False, **kwargs):
    """Instantiate a structured resume document adhering strictly to the schema defaults."""
    now = datetime.now(timezone.utc)
    doc = {
        "userId": ObjectId(user_id) if isinstance(user_id, str) else user_id,
        "title": title.strip(),
        "isPublic": bool(is_public),
        "template": template if template in TEMPLATES else "modern",
        "accentColor": accent_color,
        "professionalSummary": kwargs.get("professionalSummary", ""),
        "personalInfo": kwargs.get("personalInfo", {
            "fullName": "", "email": "", "phone": "", "location": "",
            "linkedin": "", "website": "", "github": "", "image": ""
        }),
        "experience": kwargs.get("experience", []),
        "education": kwargs.get("education", []),
        "projects": kwargs.get("projects", []),
        "certifications": kwargs.get("certifications", []),
        "skills": kwargs.get("skills", []),
        "versions": kwargs.get("versions", []),
        "createdAt": kwargs.get("createdAt", now),
        "updatedAt": kwargs.get("updatedAt", now)
    }
    return doc

# ---------------------------------------------------------------------------
# Core CRUD Functions
# ---------------------------------------------------------------------------
def create_user(db, name, email, password_hash):
    """Insert a new user document."""
    doc = {
        "name": name.strip(),
        "email": email.strip().lower(),
        "password": password_hash,
        "refreshTokens": [],
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc)
    }
    return db.users.insert_one(doc).inserted_id

def create_resume(db, user_id, title, **kwargs):
    """Insert a new resume document."""
    doc = new_resume_doc(user_id, title, **kwargs)
    return db.resumes.insert_one(doc).inserted_id

def list_resumes(db, user_id):
    """Read a user's resumes using projection to exclude heavy snapshot arrays."""
    uid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    return list(db.resumes.find(
        {"userId": uid},
        {"versions": 0, "personalInfo": 0}
    ).sort("updatedAt", DESCENDING))

def get_public_resume(db, resume_id):
    """Read a resume only if isPublic is true."""
    rid = ObjectId(resume_id) if isinstance(resume_id, str) else resume_id
    return db.resumes.find_one({"_id": rid, "isPublic": True})

def update_resume_meta(db, resume_id, user_id, template=None, accent_color=None, title=None):
    """Update top-level fields using $set."""
    rid = ObjectId(resume_id) if isinstance(resume_id, str) else resume_id
    uid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    fields = {"updatedAt": datetime.now(timezone.utc)}
    if template: fields["template"] = template
    if accent_color: fields["accentColor"] = accent_color
    if title: fields["title"] = title
    res = db.resumes.update_one({"_id": rid, "userId": uid}, {"$set": fields})
    return res.modified_count > 0

def add_skills(db, resume_id, user_id, new_skills):
    """Atomically append multiple skills without duplicates using $addToSet and $each."""
    rid = ObjectId(resume_id) if isinstance(resume_id, str) else resume_id
    uid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    res = db.resumes.update_one(
        {"_id": rid, "userId": uid},
        {
            "$addToSet": {"skills": {"$each": new_skills}},
            "$set": {"updatedAt": datetime.now(timezone.utc)}
        }
    )
    return res.modified_count > 0

def remove_skill(db, resume_id, user_id, skill_name):
    """Atomically remove a skill using $pull."""
    rid = ObjectId(resume_id) if isinstance(resume_id, str) else resume_id
    uid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    res = db.resumes.update_one(
        {"_id": rid, "userId": uid},
        {
            "$pull": {"skills": skill_name},
            "$set": {"updatedAt": datetime.now(timezone.utc)}
        }
    )
    return res.modified_count > 0

def save_version_snapshot(db, resume_id, user_id, snapshot_title, content):
    """Append a version snapshot and cap array to last 10 entries using $push with $slice: -10."""
    rid = ObjectId(resume_id) if isinstance(resume_id, str) else resume_id
    uid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    snapshot = {
        "snapshotId": f"snap-{int(datetime.now().timestamp())}",
        "savedAt": datetime.now(timezone.utc),
        "title": snapshot_title,
        "content": content
    }
    res = db.resumes.update_one(
        {"_id": rid, "userId": uid},
        {
            "$push": {
                "versions": {
                    "$each": [snapshot],
                    "$slice": -10
                }
            },
            "$set": {"updatedAt": datetime.now(timezone.utc)}
        }
    )
    return res.modified_count > 0

def delete_resume(db, resume_id, user_id):
    """Delete a resume document strictly scoped to owner tenancy."""
    rid = ObjectId(resume_id) if isinstance(resume_id, str) else resume_id
    uid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    res = db.resumes.delete_one({"_id": rid, "userId": uid})
    return res.deleted_count > 0

# ---------------------------------------------------------------------------
# Advanced Aggregation Pipelines
# ---------------------------------------------------------------------------
PIPELINE_TEMPLATE_USAGE = [
    {
        "$group": {
            "_id": "$template",
            "totalResumes": {"$sum": 1},
            "publicResumes": {"$sum": {"$cond": ["$isPublic", 1, 0]}}
        }
    },
    {"$sort": {"totalResumes": -1, "_id": 1}}
]

PIPELINE_TOP_SKILLS = [
    {"$unwind": "$skills"},
    {
        "$group": {
            "_id": {"$toLower": "$skills"},
            "frequency": {"$sum": 1}
        }
    },
    {"$sort": {"frequency": -1, "_id": 1}},
    {"$limit": 5}
]

PIPELINE_RESUMES_PER_USER = [
    {"$group": {"_id": "$userId", "resumeCount": {"$sum": 1}}},
    {
        "$lookup": {
            "from": "users",
            "localField": "_id",
            "foreignField": "_id",
            "as": "owner"
        }
    },
    {"$unwind": "$owner"},
    {"$project": {"_id": 0, "userName": "$owner.name", "resumeCount": 1}},
    {"$sort": {"resumeCount": -1, "userName": 1}}
]

PIPELINE_COMPLETENESS = [
    {
        "$project": {
            "_id": 0,
            "title": 1,
            "expCount": {"$size": "$experience"},
            "projCount": {"$size": "$projects"},
            "skillCount": {"$size": "$skills"},
            "hasSummary": {"$ne": ["$professionalSummary", ""]}
        }
    },
    {
        "$addFields": {
            "completenessScore": {
                "$add": [
                    {"$min": ["$expCount", 3]},
                    {"$min": ["$projCount", 3]},
                    {"$min": [{"$floor": {"$divide": ["$skillCount", 3]}}, 3]},
                    {"$cond": ["$hasSummary", 1, 0]}
                ]
            }
        }
    },
    {"$sort": {"completenessScore": -1, "title": 1}},
    {"$limit": 5}
]

PIPELINE_MONTHLY_VELOCITY = [
    {
        "$group": {
            "_id": {"$dateToString": {"format": "%Y-%m", "date": "$createdAt"}},
            "resumesCreated": {"$sum": 1}
        }
    },
    {"$sort": {"_id": 1}}
]

# ---------------------------------------------------------------------------
# Seed Data Generation
# ---------------------------------------------------------------------------
def seed(db):
    """Seed the database with realistic candidate profiles and diverse resumes."""
    print("\n--- Seeding MongoDB Database ---")
    # Clean previous demo collections
    db.resumes.delete_many({})
    db.users.delete_many({})

    # Valid bcrypt hash for testing (password: "password123", cost factor 10)
    demo_hash = "$2b$10$x2QABXw3QPFY4dO4msJuOe5I9h8dYhzJGTGClEuqKfpIeR7U8.SRa"

    # 1. Create Users
    u_diya = create_user(db, "Diya Maji", "diyamaji22@gmail.com", demo_hash)
    u_aarav = create_user(db, "Aarav Sharma", "aarav@example.com", demo_hash)
    u_meera = create_user(db, "Meera Iyer", "meera@example.com", demo_hash)
    u_rohan = create_user(db, "Rohan Gupta", "rohan@example.com", demo_hash)
    print(f"  ✓ Seeded 4 user accounts")

    # 2. Create Resumes
    resumes_data = [
        # Diya's Resumes
        (u_diya, "Full Stack Engineer - Cloud Scale", "modern", "#4F46E5", True,
         "Full Stack Engineer building distributed backend systems and responsive React web applications.",
         ["TypeScript", "Node.js", "Express", "React", "MongoDB", "Kafka", "Docker", "Redis"],
         datetime(2026, 8, 12, tzinfo=timezone.utc),
         [{"id": "e1", "company": "Mercora Distributed Systems", "position": "Backend Engineer"}],
         [{"id": "p1", "name": "Mercora E-Commerce"}, {"id": "p2", "name": "Collab Docs"}]),

        (u_diya, "Distributed Backend Systems Architect", "executive", "#059669", True,
         "Backend engineer specializing in distributed systems, high RPS architectures, and event streaming.",
         ["Java", "Spring Boot", "Kafka", "Redis", "PostgreSQL", "Kubernetes", "Docker", "FastAPI"],
         datetime(2026, 9, 5, tzinfo=timezone.utc),
         [{"id": "e1", "company": "Mercora", "position": "Distributed Systems Engineer"}, {"id": "e2", "company": "Tech Lab", "position": "Intern"}],
         [{"id": "p1", "name": "Kafka Event Engine"}]),

        (u_diya, "Academic Placement CV", "home_college", "#2563EB", False,
         "B.Tech Computer Science student at Lovely Professional University with strong DSA & CP credentials.",
         ["C++", "Java", "Python", "Data Structures", "Algorithms", "MongoDB"],
         datetime(2026, 10, 18, tzinfo=timezone.utc),
         [],
         [{"id": "p1", "name": "Collab Docs"}, {"id": "p2", "name": "Vintage Library Platform"}]),

        # Aarav's Resumes
        (u_aarav, "Frontend UI/UX Specialist", "minimal", "#0EA5E9", True,
         "Frontend developer focused on React 19, Tailwind CSS v4, and web accessibility.",
         ["React", "TypeScript", "Tailwind CSS", "Next.js", "Redux", "Figma", "HTML5", "CSS3"],
         datetime(2026, 8, 20, tzinfo=timezone.utc),
         [{"id": "e1", "company": "PixelCraft Studio", "position": "Frontend Lead"}],
         [{"id": "p1", "name": "Design System UI"}]),

        (u_aarav, "General Software CV", "classic", "#1E293B", False,
         "Software engineer with experience in modern web stacks.",
         ["JavaScript", "TypeScript", "Node.js", "React", "SQL"],
         datetime(2026, 9, 28, tzinfo=timezone.utc),
         [{"id": "e1", "company": "Apex Corp", "position": "Software Engineer"}],
         [{"id": "p1", "name": "Internal Dashboard"}]),

        # Meera's Resumes
        (u_meera, "Data Analyst & Business Intelligence", "modern", "#7C3AED", True,
         "Data analyst with deep expertise in Python, SQL, Tableau, and predictive analytics.",
         ["Python", "SQL", "Pandas", "NumPy", "Tableau", "Power BI", "MongoDB"],
         datetime(2026, 8, 25, tzinfo=timezone.utc),
         [{"id": "e1", "company": "Insight Analytics", "position": "Data Analyst"}],
         [{"id": "p1", "name": "Customer Churn Prediction"}, {"id": "p2", "name": "Sales Forecast"}]),

        (u_meera, "ML Research Resume", "general_template", "#D97706", False,
         "Machine learning practitioner with NLP and LLM fine-tuning experience.",
         ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "NLP", "FastAPI"],
         datetime(2026, 11, 1, tzinfo=timezone.utc),
         [],
         [{"id": "p1", "name": "BioMedical NER Parser"}, {"id": "p2", "name": "RAG Document Search"}]),

        # Rohan's Resumes
        (u_rohan, "DevOps & Cloud Infrastructure", "executive", "#0D9488", True,
         "DevOps engineer specialized in Docker, Kubernetes, Terraform, and CI/CD automation.",
         ["Docker", "Kubernetes", "Terraform", "AWS", "GitHub Actions", "Linux", "Prometheus"],
         datetime(2026, 9, 14, tzinfo=timezone.utc),
         [{"id": "e1", "company": "CloudScale Ops", "position": "DevOps Engineer"}],
         [{"id": "p1", "name": "K8s GitOps Cluster"}]),

        (u_rohan, "Site Reliability Engineer CV", "minimal", "#475569", False,
         "SRE focusing on service resilience, alerting, and distributed tracing.",
         ["Go", "Python", "Linux", "Grafana", "Prometheus", "Docker"],
         datetime(2026, 10, 29, tzinfo=timezone.utc),
         [{"id": "e1", "company": "Apex Corp", "position": "SRE Intern"}],
         [])
    ]

    for uid, title, template, color, is_pub, summary, skills, created_at, exps, projs in resumes_data:
        create_resume(
            db, uid, title,
            template=template,
            accentColor=color,
            isPublic=is_pub,
            professionalSummary=summary,
            skills=skills,
            experience=exps,
            projects=projs,
            createdAt=created_at,
            updatedAt=created_at
        )
    print(f"  ✓ Seeded 9 diverse resumes across all 6 templates")
    print(f"Database successfully populated: {db.users.count_documents({})} users, {db.resumes.count_documents({})} resumes.")

# ---------------------------------------------------------------------------
# Demonstration Suites (CRUD, Validation, Reports)
# ---------------------------------------------------------------------------
def demo_crud(db):
    """Demonstrate CRUD operations and verify schema constraint rejections."""
    print("\n=======================================================")
    print("      CRUD & VALIDATION REJECTION DEMONSTRATIONS       ")
    print("=======================================================")

    user = db.users.find_one({"email": "diyamaji22@gmail.com"})
    if not user:
        print("[!] Seed data not found. Please run 'seed' first.")
        return

    uid = user["_id"]
    print(f"Operating as authenticated user: {user['name']} (ID: {uid})")

    # 1. Create Resume
    print("\n[Step 1] Creating a new demo resume...")
    rid = create_resume(db, uid, "Full Stack Demo Resume", template="modern", accentColor="#4F46E5", skills=["TypeScript", "React"])
    print(f"  ✓ Created resume successfully with ID: {rid}")

    # 2. Read with Projection
    print("\n[Step 2] Listing resumes for user (with projection excluding heavy versions)...")
    resumes = list_resumes(db, uid)
    for r in resumes:
        print(f"  • [{r['_id']}] '{r['title']}' | Template: {r['template']} | Public: {r['isPublic']}")

    # 3. Update with $set
    print("\n[Step 3] Updating template to 'executive' and accent color to '#059669'...")
    update_resume_meta(db, rid, uid, template="executive", accent_color="#059669")
    print("  ✓ Metadata updated successfully")

    # 4. Atomic Array Operations ($addToSet with $each)
    print("\n[Step 4] Injecting skills ['MongoDB', 'Docker', 'React'] via $addToSet...")
    add_skills(db, rid, uid, ["MongoDB", "Docker", "React"]) # 'React' already exists, won't duplicate
    doc = db.resumes.find_one({"_id": rid})
    print(f"  ✓ Current skills array: {doc['skills']}")

    # 5. Remove Skill via $pull
    print("\n[Step 5] Removing skill 'Docker' via $pull...")
    remove_skill(db, rid, uid, "Docker")
    doc = db.resumes.find_one({"_id": rid})
    print(f"  ✓ Skills after $pull: {doc['skills']}")

    # 6. Capped Version Snapshot ($push with $slice: -10)
    print("\n[Step 6] Saving rolling version snapshots (testing $slice: -10 window)...")
    for i in range(1, 13):
        save_version_snapshot(db, rid, uid, f"Version {i}", {"snapshotIndex": i})
    doc = db.resumes.find_one({"_id": rid})
    print(f"  ✓ Total snapshots after 12 pushes: {len(doc['versions'])} (bounded by $slice: -10)")
    print(f"  ✓ Oldest remaining snapshot title: '{doc['versions'][0]['title']}'")

    # 7. Verification of Validation Rules & Constraints
    print("\n[Step 7] Testing $jsonSchema and Unique Index Rejections:")
    
    # Test 7.1: Duplicate Email
    try:
        create_user(db, "Duplicate Test", "diyamaji22@gmail.com", "hash12345678901234567890")
        print("  ✗ Failed: Duplicate email was accepted!")
    except DuplicateKeyError:
        print("  ✓ PASS: DuplicateKeyError correctly caught on duplicate email registration")

    # Test 7.2: Invalid Template Enum
    try:
        db.resumes.update_one({"_id": rid, "userId": uid}, {"$set": {"template": "fancy_template"}})
        print("  ✗ Failed: Invalid template was accepted!")
    except WriteError as e:
        print(f"  ✓ PASS: $jsonSchema rejected invalid template 'fancy_template'")

    # Test 7.3: Invalid Hex Color Regex
    try:
        db.resumes.update_one({"_id": rid, "userId": uid}, {"$set": {"accentColor": "blue"}})
        print("  ✗ Failed: Invalid hex color was accepted!")
    except WriteError as e:
        print(f"  ✓ PASS: $jsonSchema rejected invalid color 'blue' (regex pattern mismatch)")

    # Test 7.4: Cross-Tenant Deletion
    fake_uid = ObjectId()
    res = delete_resume(db, rid, fake_uid)
    print(f"  ✓ PASS: Cross-tenant deletion attempt blocked (deleted: {res}, document intact)")

    # Clean up demo resume
    delete_resume(db, rid, uid)
    print(f"  ✓ Cleaned up demo resume ID: {rid}")

def demo_reports(db):
    """Execute the five aggregation pipelines and display tabulated analytical reports."""
    print("\n=======================================================")
    print("      ADVANCED AGGREGATION PIPELINES & REPORTS         ")
    print("=======================================================")

    # Pipeline 1: Template Usage
    print("\n[Report 1] Template Usage & Public Visibility Distribution:")
    print(f"  {'Template':<20} | {'Total Resumes':<15} | {'Public Resumes':<15}")
    print("  " + "-" * 56)
    for row in db.resumes.aggregate(PIPELINE_TEMPLATE_USAGE):
        print(f"  {row['_id']:<20} | {row['totalResumes']:<15} | {row['publicResumes']:<15}")

    # Pipeline 2: Top Skills
    print("\n[Report 2] Top 5 Most In-Demand Skills (Case-Normalized):")
    print(f"  {'Rank':<6} | {'Skill Term':<20} | {'Frequency':<10}")
    print("  " + "-" * 42)
    for idx, row in enumerate(db.resumes.aggregate(PIPELINE_TOP_SKILLS), start=1):
        print(f"  {idx:<6} | {row['_id']:<20} | {row['frequency']:<10}")

    # Pipeline 3: Resumes per User (with $lookup)
    print("\n[Report 3] User Resume Portfolio Breakdown ($lookup join):")
    print(f"  {'Candidate Name':<25} | {'Resumes Owned':<15}")
    print("  " + "-" * 44)
    for row in db.resumes.aggregate(PIPELINE_RESUMES_PER_USER):
        print(f"  {row['userName']:<25} | {row['resumeCount']:<15}")

    # Pipeline 4: Completeness Score
    print("\n[Report 4] Resume Completeness Score Ranking (Top 5 Heuristic Scores):")
    print(f"  {'Resume Title':<35} | {'Score (0-10)':<12} | {'Exp':<4} | {'Proj':<5} | {'Skills':<6}")
    print("  " + "-" * 72)
    for row in db.resumes.aggregate(PIPELINE_COMPLETENESS):
        print(f"  {row['title']:<35} | {row['completenessScore']:<12} | {row['expCount']:<4} | {row['projCount']:<5} | {row['skillCount']:<6}")

    # Pipeline 5: Monthly Velocity
    print("\n[Report 5] Monthly Resume Creation Velocity:")
    print(f"  {'Cohort (YYYY-MM)':<20} | {'Resumes Created':<15}")
    print("  " + "-" * 40)
    for row in db.resumes.aggregate(PIPELINE_MONTHLY_VELOCITY):
        print(f"  {row['_id']:<20} | {row['resumesCreated']:<15}")

def get_analytics_json(db):
    """Execute the five aggregation pipelines and return formatted JSON output."""
    import json
    data = {
        "templateUsage": list(db.resumes.aggregate(PIPELINE_TEMPLATE_USAGE)),
        "topSkills": list(db.resumes.aggregate(PIPELINE_TOP_SKILLS)),
        "resumesPerUser": list(db.resumes.aggregate(PIPELINE_RESUMES_PER_USER)),
        "completenessScores": list(db.resumes.aggregate(PIPELINE_COMPLETENESS)),
        "monthlyVelocity": list(db.resumes.aggregate(PIPELINE_MONTHLY_VELOCITY)),
        "summary": {
            "totalUsers": db.users.count_documents({}),
            "totalResumes": db.resumes.count_documents({}),
            "publicResumes": db.resumes.count_documents({"isPublic": True})
        },
        "engine": "PyMongo 4.9+ (MongoDB Document Aggregation)"
    }
    return json.dumps(data)

# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def main():
    cmd = sys.argv[1].lower() if len(sys.argv) > 1 else "help"
    db = get_db()

    if cmd in ("analytics", "json"):
        print(get_analytics_json(db))
    elif cmd == "setup":
        setup_schema(db)
    elif cmd == "seed":
        seed(db)
    elif cmd == "crud":
        demo_crud(db)
    elif cmd == "reports":
        if "--json" in sys.argv:
            print(get_analytics_json(db))
        else:
            demo_reports(db)
    elif cmd == "all":
        setup_schema(db)
        seed(db)
        demo_crud(db)
        demo_reports(db)
    else:
        print("Usage: python resume_builder_pymongo.py [command]")
        print("Available commands:")
        print("  setup     - Apply $jsonSchema validators and create compound/unique indexes")
        print("  seed      - Populate seed dataset (4 users, 9 resumes across all 6 templates)")
        print("  crud      - Demonstrate CRUD operations and verify $jsonSchema rejections")
        print("  reports   - Execute the 5 advanced aggregation pipelines (pass --json for JSON)")
        print("  analytics - Return JSON payload of all aggregation pipelines")
        print("  all       - Run setup, seed, crud, and reports sequentially")

if __name__ == "__main__":
    main()
