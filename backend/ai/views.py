from __future__ import annotations

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ai.serializers import SuggestRequestSerializer
from ai.services import suggest
from core.responses import envelope
from core.throttling import AISuggestThrottle


class SuggestView(APIView):
    throttle_classes = (AISuggestThrottle,)

    def post(self, request: Request) -> Response:
        data = SuggestRequestSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        text = suggest(data.validated_data["field"], data.validated_data["context"])
        return envelope("Suggestion generated", {"suggestion": text})
