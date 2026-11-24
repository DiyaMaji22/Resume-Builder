"""DRF authentication backend that validates the Bearer access token."""

from __future__ import annotations

from typing import Any

from bson import ObjectId
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.request import Request

from accounts.models import User
from accounts.tokens import ACCESS_TYPE, InvalidTokenError, decode_token


class JWTAuthentication(BaseAuthentication):
    """
    Expects ``Authorization: Bearer <access token>``.

    Unlike the old service, which trusted the user id in the token alone, this loads
    the user on each request. A deleted or deactivated account therefore loses access
    immediately, not when its token expires.
    """

    keyword = b"bearer"

    def authenticate(self, request: Request) -> tuple[User, str] | None:
        header = get_authorization_header(request).split()
        if not header or header[0].lower() != self.keyword:
            return None  # Not our scheme; let other authenticators (or AnonymousUser) handle it.
        if len(header) != 2:
            raise exceptions.AuthenticationFailed("Unauthorized")

        token = header[1].decode("ascii", errors="ignore")
        try:
            payload: dict[str, Any] = decode_token(token, expected_type=ACCESS_TYPE)
        except InvalidTokenError as exc:
            raise exceptions.AuthenticationFailed("Unauthorized") from exc

        subject = str(payload.get("sub", ""))
        if not ObjectId.is_valid(subject):
            raise exceptions.AuthenticationFailed("Unauthorized")

        user = User.objects.filter(pk=subject, is_active=True).first()
        if user is None:
            raise exceptions.AuthenticationFailed("Unauthorized")
        return user, token

    def authenticate_header(self, request: Request) -> str:
        return 'Bearer realm="api"'
