"""
Parity with the original TypeScript ATS analyser.

The fixture was produced by running the original code (atsAnalyzer.ts) over every
starter resume against every benchmark job, plus two hand-written edge cases.
Any difference here is a behaviour change, not a style choice.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.test import SimpleTestCase

from resumes.ats import analyze_resume, extract_keywords
from resumes.starters import load_catalog

FIXTURE = Path(__file__).parent / "fixtures" / "ats_golden.json"

EDGE_RESUME: dict[str, Any] = {
    "title": "Edge",
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
}


class ATSParityTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.golden = json.loads(FIXTURE.read_text(encoding="utf-8"))
        catalog = load_catalog()
        cls.starters = {s["id"]: s for s in catalog["starters"]}
        cls.jobs = {j["id"]: j["description"] for j in catalog["benchmarkJobs"]}

    def test_every_starter_against_every_job_matches_original(self) -> None:
        checked = 0
        for case in self.golden["atsCases"]:
            if case["starter"] == "edge":
                continue
            with self.subTest(starter=case["starter"], job=case["job"]):
                actual = analyze_resume(self.starters[case["starter"]], self.jobs[case["job"]])
                self.assertEqual(actual, case["result"])
            checked += 1
        self.assertEqual(checked, len(self.starters) * len(self.jobs))

    def test_edge_cases_match_original(self) -> None:
        for case in self.golden["atsCases"]:
            if case["starter"] != "edge":
                continue
            with self.subTest(job=case["job"]):
                jd = {
                    "short-jd": "We need Python and Docker and GO skills",
                    "empty-jd": "nothing relevant here at all",
                }[case["job"]]
                self.assertEqual(analyze_resume(EDGE_RESUME, jd), case["result"])

    def test_keyword_extraction_matches_original(self) -> None:
        for sample in self.golden["kw"]:
            with self.subTest(text=sample["text"]):
                self.assertEqual(extract_keywords(sample["text"]), sample["keywords"])

    def test_rounding_uses_javascript_semantics(self) -> None:
        # Python's round(2.5) is 2 (banker's rounding); JavaScript's Math.round(2.5) is 3.
        from resumes.ats import _js_round

        self.assertEqual(_js_round(2.5), 3)
        self.assertEqual(_js_round(0.5), 1)
        self.assertEqual(_js_round(72.5), 73)
