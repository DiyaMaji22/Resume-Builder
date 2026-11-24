"""
Account use cases: registration, sign-in, sessions and profile management.

Views translate HTTP into calls here; nothing in this module knows about requests.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from bson import ObjectId
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError

from accounts.login_limiter import LoginFailureLimiter
from accounts.models import User
from accounts.tokens import (
    MAX_ACTIVE_SESSIONS,
    REFRESH_TYPE,
    InvalidTokenError,
    decode_token,
    issue_access_token,
    issue_refresh_token,
)
from core.exceptions import AuthenticationError, ConflictError, ServiceError

EMAIL_IN_USE = "Email already in use"


@dataclass(frozen=True)
class AuthSession:
    token: str
    refresh_token: str
    user: User


@lru_cache(maxsize=1)
def _dummy_password_hash() -> str:
    """A real hash used to keep the response time of unknown-email logins close to known-email logins."""
    return make_password("timing-equaliser-not-a-real-password")


def _load_active_user(subject: object) -> User | None:
    value = str(subject or "")
    if not ObjectId.is_valid(value):
        return None
    return User.objects.filter(pk=value, is_active=True).first()


def _start_session(user: User, *, remember_me: bool) -> AuthSession:
    refresh = issue_refresh_token(str(user.pk), remember_me=remember_me)
    user.refresh_token_ids = [*user.refresh_token_ids, refresh.jti][-MAX_ACTIVE_SESSIONS:]
    user.save(update_fields=["refresh_token_ids", "updated_at"])
    return AuthSession(
        token=issue_access_token(str(user.pk)),
        refresh_token=refresh.token,
        user=user,
    )


def register(*, name: str, email: str, password: str, remember_me: bool) -> AuthSession:
    if User.objects.filter(email=email).exists():
        raise ConflictError(EMAIL_IN_USE)
    try:
        user = User.objects.create_user(email=email, name=name, password=password)
    except IntegrityError as exc:  # Lost a race with a concurrent registration.
        raise ConflictError(EMAIL_IN_USE) from exc
    return _start_session(user, remember_me=remember_me)


def sign_in(*, email: str, password: str, remember_me: bool, ip_address: str) -> AuthSession:
    limiter = LoginFailureLimiter(ip_address)
    limiter.ensure_not_blocked()

    user = User.objects.filter(email=email).first()
    if user is None:
        # Spend comparable time as for a real account so response timing does not reveal
        # which emails are registered.
        User(password=_dummy_password_hash()).check_password(password)
        limiter.record_failure()
        raise AuthenticationError("Invalid email or password")

    if not user.is_active or not user.check_password(password):
        limiter.record_failure()
        raise AuthenticationError("Invalid email or password")

    return _start_session(user, remember_me=remember_me)


def refresh_access_token(refresh_token: str) -> str:
    try:
        payload = decode_token(refresh_token, expected_type=REFRESH_TYPE)
    except InvalidTokenError as exc:
        raise AuthenticationError("Invalid or expired refresh token") from exc

    user = _load_active_user(payload.get("sub"))
    if user is None or payload.get("jti") not in user.refresh_token_ids:
        raise AuthenticationError("Refresh token revoked")
    return issue_access_token(str(user.pk))


def sign_out(user: User, refresh_token: str | None) -> None:
    """Revoke one session. Silently does nothing for tokens that are already invalid."""
    if not refresh_token:
        return
    try:
        payload = decode_token(refresh_token, expected_type=REFRESH_TYPE)
    except InvalidTokenError:
        return
    if payload.get("sub") != str(user.pk):
        return

    jti = payload.get("jti")
    user.refresh_token_ids = [existing for existing in user.refresh_token_ids if existing != jti]
    user.save(update_fields=["refresh_token_ids", "updated_at"])


def update_profile(user: User, *, name: str | None, email: str | None) -> User:
    update_fields = ["updated_at"]
    if email is not None and email != user.email:
        if User.objects.filter(email=email).exclude(pk=user.pk).exists():
            raise ConflictError(EMAIL_IN_USE)
        user.email = email
        update_fields.append("email")
    if name is not None and name != user.name:
        user.name = name
        update_fields.append("name")

    try:
        user.save(update_fields=update_fields)
    except IntegrityError as exc:
        raise ConflictError(EMAIL_IN_USE) from exc
    return user


def change_password(user: User, *, current_password: str, new_password: str) -> None:
    if not user.check_password(current_password):
        # 400, not 401: a 401 would make the client treat this as an expired session and log out.
        raise ServiceError("Current password is incorrect")

    user.set_password(new_password)
    # A password change ends every session, including those on other devices.
    user.refresh_token_ids = []
    user.save(update_fields=["password", "refresh_token_ids", "updated_at"])


def delete_account(user: User, *, password: str) -> None:
    if not user.check_password(password):
        raise ServiceError("Incorrect password")
    user.delete()  # Resumes are removed by the foreign key's CASCADE.
