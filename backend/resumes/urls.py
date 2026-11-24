"""
Resume routes. Literal paths (``starters``, ``upload``) are listed before the
``<oid:resume_id>`` routes so they are never mistaken for an identifier.
"""

from django.urls import path

from resumes.views import (
    ATSAnalyzeView,
    PublicResumeView,
    ResumeDetailView,
    ResumeDuplicateView,
    ResumeListCreateView,
    ResumeRestoreView,
    ResumeUploadView,
    ResumeVersionsView,
    StartersView,
)

urlpatterns = [
    path("resumes", ResumeListCreateView.as_view(), name="resume-list"),
    path("resumes/starters", StartersView.as_view(), name="resume-starters"),
    path("resumes/upload", ResumeUploadView.as_view(), name="resume-upload"),
    path("resumes/public/<oid:resume_id>", PublicResumeView.as_view(), name="resume-public"),
    path("resumes/<oid:resume_id>", ResumeDetailView.as_view(), name="resume-detail"),
    path("resumes/<oid:resume_id>/duplicate", ResumeDuplicateView.as_view(), name="resume-duplicate"),
    path("resumes/<oid:resume_id>/versions", ResumeVersionsView.as_view(), name="resume-versions"),
    path(
        "resumes/<oid:resume_id>/versions/<oid:snapshot_id>/restore",
        ResumeRestoreView.as_view(),
        name="resume-restore",
    ),
    path("resumes/<oid:resume_id>/ats-analyze", ATSAnalyzeView.as_view(), name="resume-ats"),
]
