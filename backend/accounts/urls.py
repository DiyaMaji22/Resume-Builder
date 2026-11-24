from django.urls import path

from accounts.views import (
    LoginView,
    LogoutView,
    MeView,
    PasswordChangeView,
    RefreshView,
    RegisterView,
    UserProfileView,
)

urlpatterns = [
    path("auth/register", RegisterView.as_view(), name="auth-register"),
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/refresh", RefreshView.as_view(), name="auth-refresh"),
    path("auth/logout", LogoutView.as_view(), name="auth-logout"),
    path("auth/me", MeView.as_view(), name="auth-me"),
    path("users/me", UserProfileView.as_view(), name="user-profile"),
    path("users/me/password", PasswordChangeView.as_view(), name="user-password"),
]
