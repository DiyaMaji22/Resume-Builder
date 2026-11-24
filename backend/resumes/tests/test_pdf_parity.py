"""Parity with the original TypeScript PDF text parser (pdfParser.ts parseResumeFromText)."""

from __future__ import annotations

import json
from pathlib import Path

from django.test import SimpleTestCase

from core.testing import strip_generated_ids
from resumes.pdf_import import parse_resume_text

FIXTURE = Path(__file__).parent / "fixtures" / "pdf_golden.json"


class PdfParserParityTests(SimpleTestCase):
    def test_parser_output_matches_original_for_each_sample(self) -> None:
        cases = json.loads(FIXTURE.read_text(encoding="utf-8"))
        for case in cases:
            with self.subTest(sample=case["name"]):
                actual = parse_resume_text(case["text"], f"{case['name']}.pdf")
                self.assertEqual(strip_generated_ids(actual), strip_generated_ids(case["parsed"]))

    def test_generated_ids_are_unique_within_a_resume(self) -> None:
        text = (
            "Jane Doe\njane@example.com\n\nExperience\n"
            "Engineer | Acme | 2020 - 2021\n• Built things\n"
            "Analyst | Beta | 2018 - 2019\n• Analysed things"
        )
        parsed = parse_resume_text(text)
        ids = [entry["id"] for entry in parsed["experience"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 2)

    def test_invalid_email_candidate_is_dropped_not_stored(self) -> None:
        parsed = parse_resume_text("Jane Doe\na..b@example.com\nSkills\nPython")
        self.assertEqual(parsed["personalInfo"]["email"], "")
