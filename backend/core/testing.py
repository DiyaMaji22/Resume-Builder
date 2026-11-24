"""Helpers shared by test modules across apps. Not imported by application code."""

from __future__ import annotations

from typing import Any

from rest_framework.test import APIClient

from accounts.models import User
from accounts.tokens import issue_access_token

TEST_PASSWORD = "correct-horse-battery-1"  # noqa: S105 - test fixture

# bcrypt hash of "password123", as written by the original Node.js service.
LEGACY_BCRYPT_HASH = "$2b$10$x2QABXw3QPFY4dO4msJuOe5I9h8dYhzJGTGClEuqKfpIeR7U8.SRa"


def make_user(
    email: str = "user@example.com", name: str = "Test User", password: str = TEST_PASSWORD
) -> User:
    return User.objects.create_user(email=email, name=name, password=password)


def authenticate(client: APIClient, user: User) -> APIClient:
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {issue_access_token(str(user.pk))}")
    return client


def build_pdf(lines: list[str]) -> bytes:
    """A minimal single-page PDF with one line of Helvetica text per entry (ASCII only)."""
    content = ["BT", "/F1 11 Tf", "14 TL", "50 760 Td"]
    for line in lines:
        escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content.append(f"({escaped}) Tj T*")
    content.append("ET")
    stream = "\n".join(content).encode("latin-1")

    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1") + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode("latin-1") + body + b"\nendobj\n"

    xref_offset = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode("latin-1")
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode("latin-1")
    out += (f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n").encode(
        "latin-1"
    )
    return bytes(out)


def strip_generated_ids(value: Any) -> Any:
    """Replace the random ``id`` fields the PDF parser generates, so outputs can be compared."""
    if isinstance(value, dict):
        return {k: ("<id>" if k == "id" else strip_generated_ids(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [strip_generated_ids(v) for v in value]
    return value
