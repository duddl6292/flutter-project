import secrets

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import ClinicianOrAdmin
from apps.core.responses import success
from apps.core.viewsets import WrappedModelViewSet

from .models import CTCase, InferenceJob
from .selectors import visible_cases, visible_jobs
from .serializers import (
    CTCaseSerializer, InferenceCallbackSerializer, InferenceJobSerializer,
    InferenceResultSerializer, InferenceStartSerializer,
    UploadCompleteSerializer, UploadUrlSerializer,
)
from .services import complete_upload, issue_upload_url, process_callback, request_inference


class CTCaseViewSet(WrappedModelViewSet):
    serializer_class = CTCaseSerializer
    permission_classes = (ClinicianOrAdmin,)
    queryset = CTCase.objects.none()
    lookup_url_kwarg = "case_id"

    def get_queryset(self):
        return visible_cases(self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=("post",), url_path="upload-url")
    def upload_url(self, request, case_id=None):
        serializer = UploadUrlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target = issue_upload_url(self.get_object(), serializer.validated_data["content_type"])
        return success({"upload_url": target.upload_url, "object_path": target.object_path, "expires_in": target.expires_in})

    @action(detail=True, methods=("post",), url_path="upload-complete")
    def upload_complete(self, request, case_id=None):
        serializer = UploadCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return success(CTCaseSerializer(complete_upload(self.get_object(), serializer.validated_data)).data)

    @action(detail=True, methods=("post",))
    def inference(self, request, case_id=None):
        serializer = InferenceStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = request_inference(self.get_object(), request.user, serializer.validated_data["parameters"])
        return success(InferenceJobSerializer(job).data, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=("get",))
    def result(self, request, case_id=None):
        return success(InferenceResultSerializer(self.get_object().result).data)

    @action(detail=True, methods=("get",))
    def viewer(self, request, case_id=None):
        case = self.get_object()
        result = case.result
        return success({"case_id": str(case.id), "input_uri": case.input_uri, "mask_uri": result.mask_uri, "preview_uri": result.preview_uri})


class InferenceJobViewSet(WrappedModelViewSet):
    serializer_class = InferenceJobSerializer
    permission_classes = (ClinicianOrAdmin,)
    queryset = InferenceJob.objects.none()
    lookup_url_kwarg = "job_id"
    http_method_names = ("get", "post", "head", "options")

    def get_queryset(self):
        return visible_jobs(self.request.user)

    @action(detail=True, methods=("post",))
    def cancel(self, request, job_id=None):
        job = self.get_object()
        if job.status not in {InferenceJob.Status.QUEUED, InferenceJob.Status.RUNNING}:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Only queued or running jobs can be cancelled.")
        job.status, job.completed_at = InferenceJob.Status.CANCELLED, timezone.now()
        job.save(update_fields=("status", "completed_at", "updated_at"))
        return success(InferenceJobSerializer(job).data)


class InferenceCallbackView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request):
        supplied = request.headers.get("X-Internal-API-Key", "")
        if not secrets.compare_digest(supplied, settings.INFERENCE_INTERNAL_API_KEY):
            return Response({"error": {"code": "INVALID_INTERNAL_API_KEY", "message": "Invalid internal API key.", "details": {}}}, status=401)
        serializer = InferenceCallbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return success(InferenceJobSerializer(process_callback(serializer.validated_data)).data)
