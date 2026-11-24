from django.urls import path

from ai.views import SuggestView

urlpatterns = [
    path("ai/suggest", SuggestView.as_view(), name="ai-suggest"),
]
