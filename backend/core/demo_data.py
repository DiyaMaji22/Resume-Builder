"""Development seed data. Ported from the original PyMongo script, with two corrections:

* The original passed ``isPublic`` and ``accentColor`` as keyword arguments that the
  factory ignored, so every seeded resume was private with the default colour.
* Seeding deleted every document in both collections with no confirmation. It now
  requires an explicit ``flush`` and refuses to run outside development unless forced.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from accounts.models import User
from resumes.models import EducationEntry, ExperienceEntry, ProjectEntry, Resume

DEMO_PASSWORD = "password123"  # noqa: S105 - published demo credential, dev only


@dataclass(frozen=True)
class DemoUser:
    key: str
    name: str
    email: str


@dataclass(frozen=True)
class DemoResume:
    owner: str
    title: str
    template: str
    accent_color: str
    is_public: bool
    summary: str
    skills: tuple[str, ...]
    created_at: datetime
    experience: tuple[tuple[str, str], ...] = ()  # (company, position)
    projects: tuple[str, ...] = ()
    education: tuple[tuple[str, str], ...] = field(default=())  # (institution, degree)


DEMO_USERS: tuple[DemoUser, ...] = (
    DemoUser("diya", "Diya Maji", "diyamaji22@gmail.com"),
    DemoUser("aarav", "Aarav Sharma", "aarav@example.com"),
    DemoUser("meera", "Meera Iyer", "meera@example.com"),
    DemoUser("rohan", "Rohan Gupta", "rohan@example.com"),
)

DEMO_RESUMES: tuple[DemoResume, ...] = (
    DemoResume(
        "diya",
        "Full Stack Engineer - Cloud Scale",
        "modern",
        "#4F46E5",
        True,
        "Full Stack Engineer building distributed backend systems and responsive React web applications.",
        ("TypeScript", "Node.js", "Express", "React", "MongoDB", "Kafka", "Docker", "Redis"),
        datetime(2026, 8, 12, tzinfo=UTC),
        experience=(("Mercora Distributed Systems", "Backend Engineer"),),
        projects=("Mercora E-Commerce", "Collab Docs"),
    ),
    DemoResume(
        "diya",
        "Distributed Backend Systems Architect",
        "executive",
        "#059669",
        True,
        "Backend engineer specializing in distributed systems, high RPS architectures, and event streaming.",
        ("Java", "Spring Boot", "Kafka", "Redis", "PostgreSQL", "Kubernetes", "Docker", "FastAPI"),
        datetime(2026, 9, 5, tzinfo=UTC),
        experience=(("Mercora", "Distributed Systems Engineer"), ("Tech Lab", "Intern")),
        projects=("Kafka Event Engine",),
    ),
    DemoResume(
        "diya",
        "Academic Placement CV",
        "home_college",
        "#2563EB",
        False,
        "B.Tech Computer Science student at Lovely Professional University with strong DSA & CP credentials.",
        ("C++", "Java", "Python", "Data Structures", "Algorithms", "MongoDB"),
        datetime(2026, 10, 18, tzinfo=UTC),
        projects=("Collab Docs", "Vintage Library Platform"),
    ),
    DemoResume(
        "aarav",
        "Frontend UI/UX Specialist",
        "minimal",
        "#0EA5E9",
        True,
        "Frontend developer focused on React 19, Tailwind CSS v4, and web accessibility.",
        ("React", "TypeScript", "Tailwind CSS", "Next.js", "Redux", "Figma", "HTML5", "CSS3"),
        datetime(2026, 8, 20, tzinfo=UTC),
        experience=(("PixelCraft Studio", "Frontend Lead"),),
        projects=("Design System UI",),
    ),
    DemoResume(
        "aarav",
        "General Software CV",
        "classic",
        "#1E293B",
        False,
        "Software engineer with experience in modern web stacks.",
        ("JavaScript", "TypeScript", "Node.js", "React", "SQL"),
        datetime(2026, 9, 28, tzinfo=UTC),
        experience=(("Apex Corp", "Software Engineer"),),
        projects=("Internal Dashboard",),
    ),
    DemoResume(
        "meera",
        "Data Analyst & Business Intelligence",
        "modern",
        "#7C3AED",
        True,
        "Data analyst with deep expertise in Python, SQL, Tableau, and predictive analytics.",
        ("Python", "SQL", "Pandas", "NumPy", "Tableau", "Power BI", "MongoDB"),
        datetime(2026, 8, 25, tzinfo=UTC),
        experience=(("Insight Analytics", "Data Analyst"),),
        projects=("Customer Churn Prediction", "Sales Forecast"),
    ),
    DemoResume(
        "meera",
        "ML Research Resume",
        "general_template",
        "#D97706",
        False,
        "Machine learning practitioner with NLP and LLM fine-tuning experience.",
        ("Python", "PyTorch", "TensorFlow", "Scikit-Learn", "NLP", "FastAPI"),
        datetime(2026, 11, 1, tzinfo=UTC),
        projects=("BioMedical NER Parser", "RAG Document Search"),
    ),
    DemoResume(
        "rohan",
        "DevOps & Cloud Infrastructure",
        "executive",
        "#0D9488",
        True,
        "DevOps engineer specialized in Docker, Kubernetes, Terraform, and CI/CD automation.",
        ("Docker", "Kubernetes", "Terraform", "AWS", "GitHub Actions", "Linux", "Prometheus"),
        datetime(2026, 9, 14, tzinfo=UTC),
        experience=(("CloudScale Ops", "DevOps Engineer"),),
        projects=("K8s GitOps Cluster",),
    ),
    DemoResume(
        "rohan",
        "Site Reliability Engineer CV",
        "minimal",
        "#475569",
        False,
        "SRE focusing on service resilience, alerting, and distributed tracing.",
        ("Go", "Python", "Linux", "Grafana", "Prometheus", "Docker"),
        datetime(2026, 10, 29, tzinfo=UTC),
        experience=(("Apex Corp", "SRE Intern"),),
    ),
)


def seed_demo_data(*, flush: bool) -> dict[str, int]:
    """Create the demo users and resumes. Returns the number of documents created."""
    if flush:
        Resume.objects.all().delete()
        User.objects.all().delete()

    users: dict[str, User] = {}
    for spec in DEMO_USERS:
        users[spec.key] = User.objects.create_user(email=spec.email, name=spec.name, password=DEMO_PASSWORD)

    for spec in DEMO_RESUMES:
        resume = Resume.objects.create(
            user=users[spec.owner],
            title=spec.title,
            template=spec.template,
            accent_color=spec.accent_color,
            is_public=spec.is_public,
            professional_summary=spec.summary,
            skills=list(spec.skills),
            experience=[
                ExperienceEntry(id=f"e{i}", company=company, position=position)
                for i, (company, position) in enumerate(spec.experience, start=1)
            ],
            education=[
                EducationEntry(id=f"ed{i}", institution=institution, degree=degree)
                for i, (institution, degree) in enumerate(spec.education, start=1)
            ],
            projects=[ProjectEntry(id=f"p{i}", name=name) for i, name in enumerate(spec.projects, start=1)],
            certifications=[],
        )
        # auto_now_add would stamp "now"; update() bypasses it so the seed keeps historical dates.
        Resume.objects.filter(pk=resume.pk).update(created_at=spec.created_at, updated_at=spec.created_at)

    return {"users": len(users), "resumes": len(DEMO_RESUMES)}
