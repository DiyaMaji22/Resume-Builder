"""
Turns the plain text of a PDF resume into a structured resume, on a best-effort basis.

This is a port of the original heuristic parser. It is intentionally simple:
section headers, date ranges, and keyword matching. Output uses the API's camelCase
shape, so the same validation as a normal create applies to it. Every string is
clipped to the field limits first, so a long line cannot make an import fail.
"""

from __future__ import annotations

import re
import secrets
from io import BytesIO
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from core.exceptions import UnprocessableError
from resumes.ats import extract_keywords
from resumes.constants import MAX_DESCRIPTION, MAX_NAME, MAX_URL

PDF_READ_FAILED = "Could not read text from the uploaded PDF."

_EMAIL = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", re.IGNORECASE)
_PHONE = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
_LINKEDIN = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/(?:in|profile)/[a-zA-Z0-9_.-]+", re.IGNORECASE)
_GITHUB = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_.-]+", re.IGNORECASE)
_LOCATION = re.compile(r"([A-Z][a-zA-Z\s.-]+),\s*([A-Z]{2}|[A-Z][a-zA-Z\s]+)")
_NAME_BLOCKLIST = re.compile(r"resume|curriculum|vitae|page|contact", re.IGNORECASE)

_SECTION_HEADERS: dict[str, re.Pattern[str]] = {
    "summary": re.compile(
        r"^(?:professional\s+summary|summary|profile|about\s+me|objective)$", re.IGNORECASE
    ),
    "experience": re.compile(
        r"^(?:experience|work\s+experience|professional\s+experience|employment\s+history|work\s+history)$",
        re.IGNORECASE,
    ),
    "education": re.compile(
        r"^(?:education|academic\s+background|academic\s+history|qualifications)$", re.IGNORECASE
    ),
    "skills": re.compile(
        r"^(?:skills|technical\s+skills|core\s+competencies|technologies|tools)$", re.IGNORECASE
    ),
    "projects": re.compile(r"^(?:projects|key\s+projects|personal\s+projects)$", re.IGNORECASE),
    "certifications": re.compile(
        r"^(?:certifications|certificates|licenses(?:\s+&\s+certifications)?)$", re.IGNORECASE
    ),
}

_MONTH = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*"
_DATE_RANGE = re.compile(
    rf"(?:{_MONTH}\s+)?(?:\d{{4}})\s*(?:-|–|to)\s*(?:{_MONTH}\s+)?(?:\d{{4}}|present|current)",
    re.IGNORECASE,
)
_CURRENT = re.compile(r"present|current", re.IGNORECASE)
_BULLET_START = re.compile(r"^[•\-*]")
_CAPITAL_START = re.compile(r"^[A-Z]")
_DEGREE = re.compile(
    r"(?:Bachelor|Master|Doctor|Ph\.?D|Associate|B\.?S|M\.?S|B\.?A|M\.?A|B\.?Tech|M\.?Tech)[^,\n]*",
    re.IGNORECASE,
)
_INSTITUTION = re.compile(r"(?:University|College|Institute|School)[^,\n]*", re.IGNORECASE)
_YEAR = re.compile(r"(?:19|20)\d{2}")


def extract_text(pdf_bytes: bytes) -> str:
    """Plain text of every page. Image-only (scanned) PDFs yield an empty string."""
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        if reader.is_encrypted:
            reader.decrypt("")  # Owner-password-only files open with an empty user password.
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except (PdfReadError, ValueError, KeyError, IndexError, TypeError) as exc:
        raise UnprocessableError(PDF_READ_FAILED) from exc


def _new_id(prefix: str) -> str:
    return f"{prefix}-{secrets.token_hex(5)}"


def _clip(value: str, limit: int) -> str:
    return value[:limit]


def _as_url(match: re.Match[str] | None) -> str:
    if match is None:
        return ""
    value = match.group(0)
    clipped = value if value.startswith("http") else f"https://{value}"
    return _clip(clipped, MAX_URL)


def _valid_email_or_blank(candidate: str) -> str:
    if not candidate:
        return ""
    try:
        validate_email(candidate)
    except DjangoValidationError:
        return ""
    return candidate


def _keywords_in(text: str) -> list[str]:
    """Known keywords in ``text``, formatted the way the original parser displayed them."""
    formatted: dict[str, None] = {}
    for keyword in extract_keywords(text):
        if len(keyword) <= 4 and "." not in keyword:
            formatted[keyword.upper()] = None
        else:
            formatted[keyword[:1].upper() + keyword[1:]] = None
    return list(formatted)


def _skills_from_section(lines: list[str]) -> list[str]:
    if not lines:
        return []
    tokens = [t.strip() for t in re.split(r"[,•|·\n;/]", " ".join(lines))]
    skills: dict[str, None] = {}
    for token in tokens:
        if 1 < len(token) < 35 and len(token.split(" ")) <= 4:
            skills[token] = None
    return list(skills)


def _parse_experience(lines: list[str]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    bullets: list[str] = []

    def flush() -> None:
        nonlocal current, bullets
        if current is not None:
            current["description"] = _clip("\n".join(bullets), MAX_DESCRIPTION)
            entries.append(current)
        current = None
        bullets = []

    for line in lines:
        has_date = _DATE_RANGE.search(line) is not None

        if has_date and current is not None:
            flush()

        if has_date and current is None:
            current = {
                "id": _new_id("exp"),
                "company": "",
                "position": "",
                "startDate": "",
                "endDate": "",
                "isCurrent": _CURRENT.search(line) is not None,
                "description": "",
            }
            before_date = _DATE_RANGE.sub("", line, count=1).strip()
            tokens = [t.strip() for t in re.split(r"[|,\-–]", before_date) if t.strip()]
            if len(tokens) >= 2:
                current["position"] = _clip(tokens[0], MAX_NAME)
                current["company"] = _clip(tokens[1], MAX_NAME)
            elif len(tokens) == 1:
                current["position"] = _clip(tokens[0], MAX_NAME)
        elif current is not None:
            if _BULLET_START.match(line):
                bullets.append(line)
            elif not current["company"] and len(line) < 50:
                current["company"] = _clip(line, MAX_NAME)
            else:
                bullets.append(f"• {line}")
        elif _CAPITAL_START.match(line) and len(line) < 50 and not entries:
            # No date range: treat the first short capitalised line as a role title.
            current = {
                "id": _new_id("exp"),
                "company": "Company",
                "position": _clip(line, MAX_NAME),
                "startDate": "2022",
                "endDate": "Present",
                "isCurrent": True,
                "description": "",
            }

    flush()
    return entries


def _parse_education(lines: list[str]) -> list[dict[str, Any]]:
    if not lines:
        return []
    text = "\n".join(lines)
    degree = _DEGREE.search(text)
    institution = _INSTITUTION.search(text)
    graduation = _YEAR.search(text)
    return [
        {
            "id": _new_id("edu"),
            "institution": _clip(
                institution.group(0).strip() if institution else lines[0] or "University", MAX_NAME
            ),
            "degree": _clip(degree.group(0).strip() if degree else "Bachelor of Science", MAX_NAME),
            "field": "",
            "graduationDate": graduation.group(0) if graduation else "2022",
            "gpa": "",
        }
    ]


def parse_resume_text(raw_text: str, original_filename: str | None = None) -> dict[str, Any]:
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    email_match = _EMAIL.search(text)
    phone_match = _PHONE.search(text)
    location = ""
    for line in lines[:10]:
        match = _LOCATION.search(line)
        if match and "@" not in line:
            location = match.group(0)
            break

    full_name = ""
    for line in lines[:5]:
        if (
            2 < len(line) < 40
            and "@" not in line
            and "http" not in line
            and not re.search(r"\d", line)
            and not _NAME_BLOCKLIST.search(line)
        ):
            full_name = line
            break

    sections: dict[str, list[str]] = {key: [] for key in ("header", *_SECTION_HEADERS)}
    current_section = "header"
    for line in lines:
        for key, pattern in _SECTION_HEADERS.items():
            if pattern.match(line):
                current_section = key
                break
        else:
            sections[current_section].append(line)

    skills = _skills_from_section(sections["skills"])
    for keyword in _keywords_in(text):
        if keyword not in skills:
            skills.append(keyword)
    skills = skills[:25]

    projects: list[dict[str, Any]] = []
    if sections["projects"]:
        projects.append(
            {
                "id": _new_id("proj"),
                "name": _clip(sections["projects"][0] or "Featured Project", MAX_NAME),
                "type": "Application",
                "description": _clip(" ".join(sections["projects"][1:4]), 1000),
                "url": "",
                "technologies": [_clip(s, 50) for s in skills[:4]],
            }
        )

    certifications: list[dict[str, Any]] = [
        {
            "id": _new_id("cert"),
            "name": _clip(cert_line, MAX_NAME),
            "issuer": "Accredited Provider",
            "date": "",
            "url": "",
        }
        for cert_line in sections["certifications"][:3]
        if 3 < len(cert_line) < 80
    ]

    if full_name:
        title = f"{full_name}'s Resume"
    elif original_filename:
        title = re.sub(r"\.pdf$", "", original_filename, flags=re.IGNORECASE)
    else:
        title = "Uploaded Resume"

    return {
        "title": _clip(title, 100),
        "professionalSummary": _clip(" ".join(sections["summary"]), 1000),
        "personalInfo": {
            "fullName": _clip(full_name, MAX_NAME),
            "email": _valid_email_or_blank(email_match.group(0) if email_match else ""),
            "phone": _clip(phone_match.group(0) if phone_match else "", 30),
            "location": _clip(location, 100),
            "linkedin": _as_url(_LINKEDIN.search(text)),
            "website": "",
            "github": _as_url(_GITHUB.search(text)),
            "image": "",
        },
        "experience": _parse_experience(sections["experience"]),
        "education": _parse_education(sections["education"]),
        "projects": projects,
        "certifications": certifications,
        "skills": [_clip(s, 50) for s in skills],
    }
