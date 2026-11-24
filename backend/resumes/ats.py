"""
ATS keyword analyser: scores a resume against a job description.

This is a faithful port of the original TypeScript analyser. Behaviour is pinned by
golden tests (tests/test_ats_parity.py) that compare against outputs recorded from
the original code. Two details preserve that parity:

* JavaScript's Math.round rounds halves upward. Python's round() uses banker's
  rounding, so ``_js_round`` implements the JavaScript behaviour explicitly.
* Keyword matching uses the same word-boundary rules as before.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import Any

from resumes.ats_data import ATS_KEYWORDS, DISPLAY_NAMES, STRONG_ACTION_VERBS, WEAK_PHRASES

_BOUNDARY = r"[\s,;:.()\[\]/]"
_QUANTIFIED_PATTERN = re.compile(
    r"\d+[%$xX]|\d+\s*(percent|hours|users|customers|days|team|requests|reduction|growth)",
    re.IGNORECASE,
)


def _keyword_pattern(keyword: str) -> re.Pattern[str]:
    return re.compile(rf"(?:^|{_BOUNDARY}){re.escape(keyword)}(?:$|{_BOUNDARY})", re.IGNORECASE)


# Compiled once at import time. The original compiled ~170 regexes on every call.
_KEYWORD_PATTERNS: dict[str, re.Pattern[str]] = {
    kw: _keyword_pattern(kw) for kw in dict.fromkeys(ATS_KEYWORDS)
}


def _js_round(value: float) -> int:
    """Round half up, matching JavaScript's Math.round for the non-negative values used here."""
    return math.floor(value + 0.5)


def extract_keywords(text: str) -> list[str]:
    """Known keywords present in ``text``, in lexicon order and without duplicates."""
    normalized = f" {text.lower()} "
    return [kw for kw, pattern in _KEYWORD_PATTERNS.items() if pattern.search(normalized)]


def format_keyword(word: str) -> str:
    return DISPLAY_NAMES.get(word) or word[:1].upper() + word[1:]


def _resume_text_pieces(resume: Mapping[str, Any]) -> list[str]:
    personal_pieces: list[str] = [resume["title"], resume["professionalSummary"], *resume["skills"]]
    for entry in resume["experience"]:
        personal_pieces.extend([entry["company"], entry["position"], entry["description"]])
    for project in resume["projects"]:
        personal_pieces.extend(
            [project["name"], project["type"], project["description"], *project.get("technologies", [])]
        )
    for education in resume["education"]:
        personal_pieces.extend([education["institution"], education["degree"], education["field"]])
    for certification in resume["certifications"]:
        personal_pieces.extend([certification["name"], certification["issuer"]])
    return personal_pieces


def _formatting_score(resume: Mapping[str, Any]) -> int:
    info = resume["personalInfo"]
    score = 0
    if info["email"] and info["phone"]:
        score += 25
    if info["linkedin"]:
        score += 15
    if 80 <= len(resume["professionalSummary"]) <= 600:
        score += 25
    if len(resume["skills"]) >= 6:
        score += 20
    if len(resume["experience"]) >= 1:
        score += 15
    return score


def analyze_resume(resume: Mapping[str, Any], job_description: str) -> dict[str, Any]:
    """Score ``resume`` (in API shape) against ``job_description``."""
    job_keywords = extract_keywords(job_description)

    resume_keywords = set(extract_keywords(" ".join(_resume_text_pieces(resume))))
    resume_keywords.update(skill.lower().strip() for skill in resume["skills"])

    matched = [kw for kw in job_keywords if kw in resume_keywords]
    missing = [kw for kw in job_keywords if kw not in resume_keywords]

    keyword_score = _js_round((len(matched) / len(job_keywords)) * 100) if job_keywords else 80

    format_score = _formatting_score(resume)

    lower_experience = " ".join(entry["description"].lower() for entry in resume["experience"])
    number_matches = sum(1 for _ in _QUANTIFIED_PATTERN.finditer(lower_experience))
    quantified_score = min(100, _js_round((number_matches / 3) * 100))

    strong_verbs = [verb for verb in STRONG_ACTION_VERBS if verb in lower_experience]

    overall = _js_round(
        keyword_score * 0.45
        + format_score * 0.25
        + quantified_score * 0.15
        + min(100, len(strong_verbs) * 20) * 0.15
    )

    recommendations = _recommendations(resume, missing, quantified_score, strong_verbs, lower_experience)

    return {
        "overallScore": max(10, min(100, overall)),
        "keywordScore": keyword_score,
        "formattingScore": format_score,
        "quantifiedScore": quantified_score,
        "matchedKeywords": [format_keyword(kw) for kw in matched],
        "missingKeywords": [format_keyword(kw) for kw in missing],
        "strongActionVerbs": [format_keyword(verb) for verb in strong_verbs],
        "recommendations": recommendations,
    }


def _recommendations(
    resume: Mapping[str, Any],
    missing: list[str],
    quantified_score: int,
    strong_verbs: list[str],
    lower_experience: str,
) -> list[str]:
    tips: list[str] = []

    if missing:
        top_missing = ", ".join(format_keyword(kw) for kw in missing[:5])
        tips.append(f"Include target job keywords missing from your resume: {top_missing}.")

    if quantified_score < 60:
        tips.append(
            "Quantify your bullet points with metrics (e.g. 'reduced latency by 35%', "
            "'managed $60k budget', 'scaled to 1M users')."
        )

    if len(strong_verbs) < 3:
        tips.append(
            "Begin experience bullet points with authoritative action verbs "
            "(e.g., Architected, Engineered, Spearheaded, Optimized)."
        )

    for phrase in WEAK_PHRASES:
        if phrase in lower_experience:
            tips.append(f"Replace passive phrasing like '{phrase}' with active impact verbs.")
            break

    if not resume["personalInfo"]["linkedin"]:
        tips.append("Add a LinkedIn URL; recruiter ATS algorithms favor profiles with verified links.")

    if len(resume["skills"]) < 8:
        tips.append("Expand your Skills section to at least 8-15 relevant hard skills.")

    if not tips:
        tips.append("Outstanding resume! Well aligned with this job specification.")
    return tips
