from django.urls import path

from analytics.views import AnalyticsView, SeedView, SetupView

urlpatterns = [
    path("analytics", AnalyticsView.as_view(), name="analytics"),
    path("analytics/setup", SetupView.as_view(), name="analytics-setup"),
    path("analytics/seed", SeedView.as_view(), name="analytics-seed"),
]
