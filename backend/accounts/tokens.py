"""
JSON Web Tokens for the API.

* Access tokens are short-lived (15 minutes) and stateless.
* Refresh tokens are long-lived (24 hours, or 7 days with "remember me"). Each one
  carries a unique ``jti`` that is stored on the user. Logging out, or a password
  change, removes it, which revokes the token.

Refresh tokens are not hashed, and this is deliberate. The JTI is only an identifier;
the security comes from the HMAC signature. Storing the JTI avoids the 72-byte
truncation problem the old implementation had with bcrypt-hashing long JWTs.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from django.conf import settings

ALGORITHM = "HS256"
ACCESS_TYPE = "access"
REFRESH_TYPE = "refresh"

ACCESS_TOKEN_TTL = timedelta(minutes=15)
REFRESH_TOKEN_TTL = timedelta(hours=24)
REFRESH_TOKEN_TTL_REMEMBER_ME = timedelta(days=7)

# Maximum concurrent sessions (refresh tokens) per user. The oldest is dropped first.
MAX_ACTIVE_SESSIONS = 5


class InvalidTokenError(Exception):
    """Raised when a token is malformed, expired, mis-signed or of the wrong type."""


@dataclass(frozen=True)
class IssuedRefreshToken:
    token: str
    jti: str


def _now() -> datetime:
    return datetime.now(tz=UTC)


def issue_access_token(user_id: str) -> str:
    now = _now()
    payload = {
        "sub": user_id,
        "type": ACCESS_TYPE,
        "iat": now,
        "exp": now + ACCESS_TOKEN_TTL,
    }
    return jwt.encode(payload, settings.JWT_KEY, algorithm=ALGORITHM)


def issue_refresh_token(user_id: str, *, remember_me: bool) -> IssuedRefreshToken:
    now = _now()
    ttl = REFRESH_TOKEN_TTL_REMEMBER_ME if remember_me else REFRESH_TOKEN_TTL
    jti = uuid.uuid4().hex
    payload = {
        "sub": user_id,
        "type": REFRESH_TYPE,
        "jti": jti,
        "iat": now,
        "exp": now + ttl,
    }
    return IssuedRefreshToken(token=jwt.encode(payload, settings.JWT_KEY, algorithm=ALGORITHM), jti=jti)


def decode_token(token: str, *, expected_type: str) -> dict[str, Any]:
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.JWT_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "iat", "sub", "type"]},
        )
    except jwt.PyJWTError as exc:
        raise InvalidTokenError(str(exc)) from exc

    if payload.get("type") != expected_type:
        raise InvalidTokenError("Unexpected token type")
    return payload
