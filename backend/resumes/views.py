"""HTTP layer for resumes. Every lookup is scoped to the requesting user."""

from __future__ import annotations

from django.conf import settings
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import NotFoundError, ServiceError
from core.responses import envelope
from core.throttling import GlobalIPThrottle
from resumes import services
from resumes.ats import analyze_resume
from resumes.models import Resume
from resumes.serializers import (
    ATSAnalyzeSerializer,
    ResumeCreateSerializer,
    ResumeListItemSerializer,
    ResumeSerializer,
    ResumeWriteSerializer,
)
from resumes.starters import load_catalog


def _owned_resume(request: Request, resume_id: str) -> Resume:
    """Fetch a resume the requesting user owns. Other users' resumes look like missing ones."""
    resume = Resume.objects.filter(pk=resume_id, user=request.user).first()
    if resume is None:
        raise NotFoundError("Resume not found")
    return resume


class ResumeListCreateView(APIView):
    def get(self, request: Request) -> Response:
        resumes = (
            Resume.objects.filter(user=request.user)
            .defer("versions")  # Version snapshots are large and not needed in lists.
            .order_by("-updated_at")
        )
        return envelope("Resumes fetched", ResumeListItemSerializer(resumes, many=True).data)

    def post(self, request: Request) -> Response:
        data = ResumeCreateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        resume = services.create_resume(request.user, data.validated_data)
        return envelope(
            "Resume created",
            ResumeSerializer(resume).data,
            status_code=status.HTTP_201_CREATED,
        )


class ResumeDetailView(APIView):
    def get(self, request: Request, resume_id: str) -> Response:
        resume = _owned_resume(request, resume_id)
        return envelope("Resume fetched", ResumeSerializer(resume).data)

    def put(self, request: Request, resume_id: str) -> Response:
        resume = _owned_resume(request, resume_id)
        data = ResumeWriteSerializer(data=request.data, partial=True)
        data.is_valid(raise_exception=True)
        resume = services.update_resume(resume, data.validated_data)
        return envelope("Resume updated", ResumeSerializer(resume).data)

    def delete(self, request: Request, resume_id: str) -> Response:
        resume = _owned_resume(request, resume_id)
        services.delete_resume(resume)
        return envelope("Resume deleted")


class ResumeDuplicateView(APIView):
    def post(self, request: Request, resume_id: str) -> Response:
        source = _owned_resume(request, resume_id)
        copy = services.duplicate_resume(source)
        return envelope(
            "Resume duplicated",
            ResumeSerializer(copy).data,
            status_code=status.HTTP_201_CREATED,
        )


class ResumeVersionsView(APIView):
    def post(self, request: Request, resume_id: str) -> Response:
        resume = services.save_version(_owned_resume(request, resume_id))
        return envelope("Version saved", ResumeSerializer(resume).data)


class ResumeRestoreView(APIView):
    def post(self, request: Request, resume_id: str, snapshot_id: str) -> Response:
        resume = services.restore_version(_owned_resume(request, resume_id), snapshot_id)
        return envelope("Version restored", ResumeSerializer(resume).data)


class ATSAnalyzeView(APIView):
    def post(self, request: Request, resume_id: str) -> Response:
        data = ATSAnalyzeSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        resume = _owned_resume(request, resume_id)
        result = analyze_resume(ResumeSerializer(resume).data, data.validated_data["jobDescription"])
        return envelope("ATS analysis completed", result)


class ResumeUploadView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request: Request) -> Response:
        upload = request.FILES.get("file")
        if upload is None:
            raise ServiceError("No PDF file uploaded")

        max_bytes: int = settings.RESUME_UPLOAD_MAX_BYTES
        if upload.size > max_bytes:
            raise ServiceError(
                f"PDF is too large. The limit is {max_bytes // (1024 * 1024)} MB.",
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

        content = upload.read()
        if not content.startswith(b"%PDF-"):
            raise ServiceError("Only PDF files can be imported.")

        resume = services.import_resume_from_pdf(request.user, content, upload.name or "resume.pdf")
        return envelope(
            "Resume uploaded and parsed successfully",
            ResumeSerializer(resume).data,
            status_code=status.HTTP_201_CREATED,
        )


class StartersView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request: Request) -> Response:
        return envelope("Starter templates fetched", load_catalog())


class PublicResumeView(APIView):
    """A resume the owner has published. Exposes contact details, but never version history."""

    permission_classes = (AllowAny,)
    authentication_classes = ()
    throttle_classes = (GlobalIPThrottle,)

    def get(self, request: Request, resume_id: str) -> Response:
        resume = Resume.objects.filter(pk=resume_id, is_public=True).defer("versions").first()
        if resume is None:
            raise NotFoundError("Resume not found")
        return envelope("Resume fetched", ResumeListItemSerializer(resume).data)
