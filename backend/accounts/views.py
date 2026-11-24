"""HTTP layer for authentication and account management."""

from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts import services
from accounts.serializers import (
    AccountDeleteSerializer,
    AuthPayloadSerializer,
    LoginSerializer,
    LogoutSerializer,
    PasswordChangeSerializer,
    ProfileUpdateSerializer,
    RefreshSerializer,
    RegisterSerializer,
    UserSerializer,
)
from core.request import client_ip
from core.responses import envelope
from core.throttling import GlobalIPThrottle, RefreshThrottle, RegisterThrottle


class RegisterView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    throttle_classes = (GlobalIPThrottle, RegisterThrottle)

    def post(self, request: Request) -> Response:
        data = RegisterSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        v = data.validated_data
        session = services.register(
            name=v["name"], email=v["email"], password=v["password"], remember_me=v["rememberMe"]
        )
        return envelope(
            "Account created",
            AuthPayloadSerializer(session).data,
            status_code=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    throttle_classes = (GlobalIPThrottle,)

    def post(self, request: Request) -> Response:
        data = LoginSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        v = data.validated_data
        session = services.sign_in(
            email=v["email"],
            password=v["password"],
            remember_me=v["rememberMe"],
            ip_address=client_ip(request),
        )
        return envelope("Login successful", AuthPayloadSerializer(session).data)


class RefreshView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    throttle_classes = (GlobalIPThrottle, RefreshThrottle)

    def post(self, request: Request) -> Response:
        data = RefreshSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        token = services.refresh_access_token(data.validated_data["refreshToken"])
        return envelope("Token refreshed", {"token": token})


class LogoutView(APIView):
    def post(self, request: Request) -> Response:
        data = LogoutSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        services.sign_out(request.user, data.validated_data["refreshToken"] or None)
        return envelope("Logged out")


class MeView(APIView):
    def get(self, request: Request) -> Response:
        return envelope("Profile fetched", UserSerializer(request.user).data)


class UserProfileView(APIView):
    def put(self, request: Request) -> Response:
        data = ProfileUpdateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        user = services.update_profile(
            request.user,
            name=data.validated_data.get("name"),
            email=data.validated_data.get("email"),
        )
        return envelope("Profile updated", UserSerializer(user).data)

    def delete(self, request: Request) -> Response:
        data = AccountDeleteSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        services.delete_account(request.user, password=data.validated_data["password"])
        return envelope("Account deleted")


class PasswordChangeView(APIView):
    def put(self, request: Request) -> Response:
        data = PasswordChangeSerializer(data=request.data, context={"user": request.user})
        data.is_valid(raise_exception=True)
        services.change_password(
            request.user,
            current_password=data.validated_data["currentPassword"],
            new_password=data.validated_data["newPassword"],
        )
        return envelope("Password changed successfully")
