"""
Password verification for accounts created by the original Node.js service.

That service stored bcrypt hashes ("$2b$...") with no algorithm prefix, which
Django's hashers do not recognise. These helpers let those accounts log in; the
caller re-hashes the password with Django's hasher on the next successful login.
"""

from __future__ import annotations

import bcrypt

_LEGACY_BCRYPT_PREFIXES = ("$2a$", "$2b$", "$2y$")

# bcrypt only uses the first 72 bytes of a password. Node's bcrypt truncated silently,
# so we truncate in the same way to keep existing passwords verifying.
_BCRYPT_MAX_BYTES = 72


def is_legacy_bcrypt_hash(encoded: str) -> bool:
    return encoded.startswith(_LEGACY_BCRYPT_PREFIXES)


def verify_legacy_bcrypt(raw_password: str, encoded: str) -> bool:
    try:
        return bcrypt.checkpw(raw_password.encode("utf-8")[:_BCRYPT_MAX_BYTES], encoded.encode("ascii"))
    except ValueError:
        return False
