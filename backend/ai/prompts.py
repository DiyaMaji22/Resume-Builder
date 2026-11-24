"""Prompt construction for resume-writing suggestions. Wording matches the original service."""

from __future__ import annotations

from typing import Literal, TypedDict

SuggestField = Literal["summary", "experience_description"]

SYSTEM_PROMPT = "You are a professional resume writing expert. Be concise, specific, and impactful."


class ExistingExperience(TypedDict):
    position: str
    company: str
    description: str


class SuggestContext(TypedDict, total=False):
    currentText: str
    position: str
    company: str
    existingExperience: list[ExistingExperience]
    skills: list[str]


def build_prompt(field: SuggestField, context: SuggestContext) -> str:
    current = context.get("currentText")

    if field == "summary":
        experience_lines = "\n".join(
            f"- {entry['position']} at {entry['company']}"
            for entry in context.get("existingExperience", [])[:3]
        )
        skill_line = ", ".join(context.get("skills", [])[:8])
        parts = [
            "Write a professional resume summary (2-3 sentences, first person, no filler).",
            f"Experience:\n{experience_lines}" if experience_lines else "",
            f"Skills: {skill_line}" if skill_line else "",
            f"Current draft: {current}" if current else "",
            "Return ONLY the summary text. No preamble, no quotes.",
        ]
        return "\n\n".join(part for part in parts if part)

    parts = [
        "Write 3-4 concise resume bullet points for this role "
        "(start each with an action verb, quantify impact where possible).",
        f"Position: {context.get('position', 'unknown')}",
        f"Company: {context.get('company', 'unknown')}",
        f"Current draft: {current}" if current else "",
        "Return ONLY the bullet points, one per line, starting with •. No preamble.",
    ]
    return "\n".join(part for part in parts if part)
