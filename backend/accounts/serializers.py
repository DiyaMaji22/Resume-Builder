"""Request validation and response shapes for account endpoints."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from accounts.models import User
from core.serializer_fields import IsoDateTimeField


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=2, max_length=100)
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(max_length=128, write_only=True, trim_whitespace=False)
    rememberMe = serializers.BooleanField(default=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        candidate = User(name=attrs["name"], email=attrs["email"])
        try:
            validate_password(attrs["password"], user=candidate)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc
        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(max_length=128, write_only=True, trim_whitespace=False)
    rememberMe = serializers.BooleanField(default=False)


class RefreshSerializer(serializers.Serializer):
    refreshToken = serializers.CharField(max_length=2048)


class LogoutSerializer(serializers.Serializer):
    refreshToken = serializers.CharField(max_length=2048, required=False, allow_blank=True, default="")


class ProfileUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=2, max_length=100, required=False)
    email = serializers.EmailField(max_length=254, required=False)

    def validate_email(self, value: str) -> str:
        # Same normalisation as registration, so uniqueness checks compare like with like.
        return value.strip().lower()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if not attrs:
            raise serializers.ValidationError("Nothing to update.")
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(max_length=128, write_only=True, trim_whitespace=False)
    newPassword = serializers.CharField(max_length=128, write_only=True, trim_whitespace=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        user: User = self.context["user"]
        try:
            validate_password(attrs["newPassword"], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"newPassword": list(exc.messages)}) from exc
        return attrs


class AccountDeleteSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128, write_only=True, trim_whitespace=False)


class UserSerializer(serializers.Serializer):
    _id = serializers.CharField(source="pk", read_only=True)
    name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    createdAt = IsoDateTimeField(source="created_at")
    updatedAt = IsoDateTimeField(source="updated_at")


class AuthPayloadSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)
    refreshToken = serializers.CharField(source="refresh_token", read_only=True)
    user = UserSerializer(read_only=True)
