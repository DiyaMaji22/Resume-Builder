"""Root URL configuration. Every API route lives under /api/."""

from django.urls import include, path

from core.views import health

urlpatterns = [
    path("health", health, name="health"),
    path("api/", include("accounts.urls")),
    path("api/", include("resumes.urls")),
    path("api/", include("ai.urls")),
    path("api/", include("analytics.urls")),
]

handler404 = "core.views.not_found"
handler400 = "core.views.bad_request"
handler500 = "core.views.server_error"
