from django.urls import path
from .views import CTCaseViewSet, InferenceJobViewSet

urlpatterns = [
    path("cases", CTCaseViewSet.as_view({"get": "list", "post": "create"}), name="case-list"),
    path("cases/<uuid:case_id>", CTCaseViewSet.as_view({"get": "retrieve"}), name="case-detail"),
    path("cases/<uuid:case_id>/upload-url", CTCaseViewSet.as_view({"post": "upload_url"}), name="case-upload-url"),
    path("cases/<uuid:case_id>/upload-complete", CTCaseViewSet.as_view({"post": "upload_complete"}), name="case-upload-complete"),
    path("cases/<uuid:case_id>/inference", CTCaseViewSet.as_view({"post": "inference"}), name="case-inference"),
    path("cases/<uuid:case_id>/result", CTCaseViewSet.as_view({"get": "result"}), name="case-result"),
    path("cases/<uuid:case_id>/viewer", CTCaseViewSet.as_view({"get": "viewer"}), name="case-viewer"),
    path("inference-jobs/<uuid:job_id>", InferenceJobViewSet.as_view({"get": "retrieve"}), name="inference-job-detail"),
    path("inference-jobs/<uuid:job_id>/cancel", InferenceJobViewSet.as_view({"post": "cancel"}), name="inference-job-cancel"),
]
