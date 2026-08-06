from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import uuid
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any
from urllib import error, request

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.cloud import storage
from google.oauth2 import id_token

from apps.appointments.models import Encounter
from apps.imaging.models import ImagingAsset
from apps.notifications.models import Notification
from apps.patients.models import Patient

from .models import AIModelVersion, CTCase, InferenceJob, InferenceResult


class CTAnalysisError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        code: str = "CT_ANALYSIS_ERROR",
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable


@dataclass(frozen=True)
class UploadedCT:
    uri: str
    sha256: str
    size: int
    content_type: str


def _file_extension(filename: str) -> str:
    lowered = filename.lower()
    if lowered.endswith(".nii.gz"):
        return ".nii.gz"
    if lowered.endswith(".nii"):
        return ".nii"
    raise CTAnalysisError(
        "NIfTI 파일(.nii 또는 .nii.gz)만 업로드할 수 있습니다.",
        code="UNSUPPORTED_CT_FORMAT",
    )


def upload_ct_file(uploaded_file: Any, patient: Patient) -> UploadedCT:
    extension = _file_extension(uploaded_file.name)
    if uploaded_file.size <= 0:
        raise CTAnalysisError("빈 파일은 업로드할 수 없습니다.", code="EMPTY_CT_FILE")
    if uploaded_file.size > settings.CT_MAX_UPLOAD_BYTES:
        raise CTAnalysisError(
            "CT 파일이 허용된 최대 크기를 초과했습니다.",
            code="CT_FILE_TOO_LARGE",
        )

    digest = hashlib.sha256()
    for chunk in uploaded_file.chunks():
        digest.update(chunk)
    uploaded_file.seek(0)

    prefix = settings.CT_INPUT_PREFIX
    object_key = (
        f"{prefix}/{patient.id}/{uuid.uuid4()}/input{extension}"
        if prefix
        else f"{patient.id}/{uuid.uuid4()}/input{extension}"
    )
    content_type = (
        "application/gzip"
        if extension == ".nii.gz"
        else "application/octet-stream"
    )

    try:
        client = storage.Client()
        blob = client.bucket(settings.CT_INPUT_BUCKET).blob(object_key)
        blob.upload_from_file(
            uploaded_file,
            rewind=True,
            content_type=content_type,
            if_generation_match=0,
            timeout=300,
        )
    except Exception as exc:
        raise CTAnalysisError(
            "CT 파일을 Cloud Storage에 업로드하지 못했습니다.",
            code="CT_UPLOAD_FAILED",
            retryable=True,
        ) from exc

    return UploadedCT(
        uri=f"gs://{settings.CT_INPUT_BUCKET}/{object_key}",
        sha256=digest.hexdigest(),
        size=uploaded_file.size,
        content_type=content_type,
    )


def delete_gcs_uri(uri: str) -> None:
    try:
        bucket_name, object_key = parse_gcs_uri(uri)
        storage.Client().bucket(bucket_name).blob(object_key).delete()
    except Exception:
        # DB 생성 실패 뒤의 best-effort 정리다. 원래 예외를 가리지 않는다.
        return


def parse_gcs_uri(uri: str) -> tuple[str, str]:
    if not uri.startswith("gs://"):
        raise CTAnalysisError("올바르지 않은 GCS 경로입니다.", code="INVALID_GCS_URI")
    path = uri[5:]
    bucket_name, separator, object_key = path.partition("/")
    if not bucket_name or not separator or not object_key:
        raise CTAnalysisError("올바르지 않은 GCS 경로입니다.", code="INVALID_GCS_URI")
    return bucket_name, object_key


def create_case_and_job(
    *,
    patient: Patient,
    encounter: Encounter | None,
    imaging_asset: ImagingAsset | None,
    source_case: CTCase | None,
    uploaded: UploadedCT,
    requested_by: Any,
    study_type: str,
    description: str,
    delete_input_on_failure: bool = False,
) -> tuple[CTCase, InferenceJob]:
    try:
        with transaction.atomic():
            case = CTCase.objects.create(
                encounter=encounter,
                imaging_study=(
                    imaging_asset.study
                    if imaging_asset
                    else source_case.imaging_study
                    if source_case
                    else None
                ),
                study_type=study_type,
                description=description,
                status=CTCase.Status.READY,
                input_uri=uploaded.uri,
                input_sha256=uploaded.sha256,
                file_size_bytes=uploaded.size,
                content_type=uploaded.content_type,
                created_by=requested_by,
            )
            gateway_case_id = case.id.int % 2_147_483_646 + 1
            job = InferenceJob.objects.create(
                case=case,
                requested_by=requested_by,
                status=InferenceJob.Status.QUEUED,
                progress=0,
                parameters={"gateway_case_id": gateway_case_id},
            )
    except Exception:
        if delete_input_on_failure:
            delete_gcs_uri(uploaded.uri)
        raise
    return case, job


def input_from_imaging_asset(imaging_asset: ImagingAsset) -> UploadedCT:
    stored = imaging_asset.stored_object
    uri = f"gs://{stored.bucket_name}/{stored.object_key}"
    sha256 = stored.sha256
    if not sha256:
        digest = hashlib.sha256()
        stream, _blob = open_gcs_uri(uri)
        try:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
        finally:
            stream.close()
        sha256 = digest.hexdigest()
    return UploadedCT(
        uri=uri,
        sha256=sha256,
        size=stored.file_size_bytes,
        content_type=stored.content_type or "application/gzip",
    )


def input_from_case(source_case: CTCase) -> UploadedCT:
    return UploadedCT(
        uri=source_case.input_uri,
        sha256=source_case.input_sha256,
        size=source_case.file_size_bytes,
        content_type=source_case.content_type,
    )


def _gateway_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    audience = settings.CT_INFERENCE_GATEWAY_AUDIENCE
    if audience:
        try:
            token = id_token.fetch_id_token(GoogleAuthRequest(), audience)
        except Exception as exc:
            if not (settings.DEBUG and settings.CT_GATEWAY_USE_GCLOUD_AUTH):
                raise CTAnalysisError(
                    "Cloud Run Gateway 인증 토큰을 발급하지 못했습니다.",
                    code="GATEWAY_AUTH_FAILED",
                    retryable=True,
                ) from exc
            executable = shutil.which("gcloud.cmd") or shutil.which("gcloud")
            if not executable:
                raise CTAnalysisError(
                    "로컬 gcloud CLI를 찾을 수 없습니다.",
                    code="GATEWAY_AUTH_FAILED",
                ) from exc
            try:
                token = subprocess.run(
                    [executable, "auth", "print-identity-token"],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                ).stdout.strip()
            except (subprocess.SubprocessError, OSError) as cli_exc:
                raise CTAnalysisError(
                    "gcloud 로그인으로 Gateway 인증 토큰을 발급하지 못했습니다.",
                    code="GATEWAY_AUTH_FAILED",
                    retryable=True,
                ) from cli_exc
            if not token:
                raise CTAnalysisError(
                    "gcloud가 빈 인증 토큰을 반환했습니다.",
                    code="GATEWAY_AUTH_FAILED",
                )
        headers["Authorization"] = f"Bearer {token}"
    return headers


def call_inference_gateway(payload: dict[str, Any]) -> dict[str, Any]:
    endpoint = f"{settings.CT_INFERENCE_GATEWAY_URL}/api/v1/inference"
    http_request = request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers=_gateway_headers(),
        method="POST",
    )
    try:
        with request.urlopen(
            http_request,
            timeout=settings.CT_GATEWAY_TIMEOUT_SECONDS,
        ) as response:
            body = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        try:
            body = json.loads(exc.read().decode("utf-8"))
            message = body.get("error", {}).get("message") or body.get("detail")
        except (ValueError, AttributeError):
            message = None
        raise CTAnalysisError(
            message or f"추론 Gateway가 HTTP {exc.code}을 반환했습니다.",
            code="GATEWAY_HTTP_ERROR",
            retryable=exc.code >= 500,
        ) from exc
    except (error.URLError, TimeoutError) as exc:
        raise CTAnalysisError(
            "추론 Gateway에 연결하지 못했습니다.",
            code="GATEWAY_UNAVAILABLE",
            retryable=True,
        ) from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CTAnalysisError(
            "추론 Gateway 응답을 해석하지 못했습니다.",
            code="INVALID_GATEWAY_RESPONSE",
        ) from exc

    if not isinstance(body, dict):
        raise CTAnalysisError(
            "추론 Gateway 응답 형식이 올바르지 않습니다.",
            code="INVALID_GATEWAY_RESPONSE",
        )
    return body


def _decimal(value: Any, *, decimal_places: int = 6) -> Decimal | None:
    if value is None:
        return None
    quantum = Decimal(1).scaleb(-decimal_places)
    return Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP)


def _notify_ct_analysis(
    job: InferenceJob,
    *,
    event: str,
) -> Notification:
    completed = event == "CT_ANALYSIS_COMPLETED"
    notification, _created = Notification.objects.get_or_create(
        recipient=job.requested_by,
        deduplication_key=f"ct-analysis:{job.id}:{event}",
        defaults={
            "type": Notification.Type.TEST_RESULT,
            "title": (
                "CT AI 분석 완료"
                if completed
                else "CT AI 분석 실패"
            ),
            "body": (
                "CT 분석 결과를 확인해주세요."
                if completed
                else "CT 분석을 완료하지 못했습니다. 다시 시도해주세요."
            ),
            "data": {
                "case_id": str(job.case_id),
                "job_id": str(job.id),
                "path": f"/ct-analysis/{job.case_id}",
                "event": event,
            },
        },
    )
    return notification


def _mark_failed(job: InferenceJob, exc: CTAnalysisError) -> None:
    now = timezone.now()
    with transaction.atomic():
        job.status = InferenceJob.Status.FAILED
        job.progress = 100
        job.error_code = exc.code
        job.error_message = str(exc)
        job.error_retryable = exc.retryable
        job.completed_at = now
        job.save(update_fields=[
            "status", "progress", "error_code", "error_message",
            "error_retryable", "completed_at", "updated_at",
        ])
        job.case.status = CTCase.Status.FAILED
        job.case.save(update_fields=["status", "updated_at"])
        _notify_ct_analysis(
            job,
            event="CT_ANALYSIS_FAILED",
        )


def create_retry_job(
    previous_job: InferenceJob,
    *,
    requested_by: Any,
) -> InferenceJob:
    """Create a retry with a new ID so result artifacts use a new GCS path."""

    with transaction.atomic():
        case = CTCase.objects.select_for_update().get(id=previous_job.case_id)
        retry_job = InferenceJob.objects.create(
            case=case,
            requested_by=requested_by,
            status=InferenceJob.Status.QUEUED,
            progress=0,
            parameters=dict(previous_job.parameters),
        )
        case.status = CTCase.Status.READY
        case.save(update_fields=["status", "updated_at"])
    return retry_job


def run_inference(job: InferenceJob) -> InferenceResult:
    now = timezone.now()
    job.status = InferenceJob.Status.RUNNING
    job.progress = 20
    job.started_at = now
    job.save(update_fields=["status", "progress", "started_at", "updated_at"])
    job.case.status = CTCase.Status.PROCESSING
    job.case.save(update_fields=["status", "updated_at"])

    try:
        payload = {
            "schema_version": "1.0",
            "job_id": str(job.id),
            "case_id": int(job.parameters["gateway_case_id"]),
            "input_uri": job.case.input_uri,
            "model_version": settings.CT_MODEL_VERSION,
        }
        response = call_inference_gateway(payload)
        if response.get("status") != "completed":
            failure = response.get("error") or {}
            raise CTAnalysisError(
                failure.get("message") or "AI 추론이 실패했습니다.",
                code=failure.get("code") or "INFERENCE_FAILED",
                retryable=bool(failure.get("retryable")),
            )

        model = response["model"]
        artifacts = response["artifacts"]
        lesion = response["result"]
        performance = response["performance"]
        input_info = response["input"]

        with transaction.atomic():
            model_version, _ = AIModelVersion.objects.get_or_create(
                model_key=model["model_id"],
                version=model["model_version"],
                defaults={
                    "display_name": "BrainOn CT 2.5D",
                    "framework": "nnU-Net v2",
                    "checkpoint_uri": "",
                    "checkpoint_sha256": "",
                    "input_schema_version": "1.0",
                    "output_schema_version": "1.0",
                    "is_active": True,
                    "metadata": model,
                },
            )
            result = InferenceResult.objects.create(
                case=job.case,
                job=job,
                model_version_ref=model_version,
                model_id=model["model_id"],
                model_version=model["model_version"],
                checkpoint=model.get("checkpoint", ""),
                mask_uri=artifacts["mask_uri"],
                preview_uri=artifacts.get("preview_uri") or "",
                probability_uri=artifacts.get("probability_uri") or "",
                entropy_uri=artifacts.get("entropy_uri") or "",
                uncertainty_uri=artifacts.get("uncertainty_uri") or "",
                lesion_voxels=lesion["lesion_voxel_count"],
                lesion_volume_ml=_decimal(lesion["lesion_volume_ml"]),
                lesion_slice_count=lesion["lesion_slice_count"],
                lesion_slice_start=lesion.get("lesion_slice_start"),
                lesion_slice_end=lesion.get("lesion_slice_end"),
                max_lesion_slice=lesion.get("max_lesion_slice"),
                shape=input_info["shape"],
                spacing=input_info["spacing_mm"],
                preprocessing_seconds=_decimal(
                    performance["input_download_seconds"]
                    + performance["context_preparation_seconds"]
                ),
                inference_seconds=_decimal(performance["inference_seconds"]),
                postprocessing_seconds=_decimal(
                    performance["postprocessing_seconds"]
                    + performance["output_upload_seconds"]
                ),
                total_seconds=_decimal(performance["total_seconds"]),
                gpu_memory_peak_mb=_decimal(
                    performance.get("gpu_peak_memory_mb"),
                    decimal_places=3,
                ),
                raw_result=response,
            )
            completed_at = timezone.now()
            job.status = InferenceJob.Status.SUCCEEDED
            job.progress = 100
            job.model_version = model_version
            job.completed_at = completed_at
            job.error_code = ""
            job.error_message = ""
            job.error_retryable = False
            job.save(update_fields=[
                "status", "progress", "model_version", "completed_at",
                "error_code", "error_message", "error_retryable", "updated_at",
            ])
            job.case.status = CTCase.Status.COMPLETED
            job.case.save(update_fields=["status", "updated_at"])
            _notify_ct_analysis(
                job,
                event="CT_ANALYSIS_COMPLETED",
            )
        return result
    except CTAnalysisError as exc:
        _mark_failed(job, exc)
        raise
    except (KeyError, TypeError, ValueError) as exc:
        wrapped = CTAnalysisError(
            "추론 결과에 필요한 값이 누락되었습니다.",
            code="INVALID_GATEWAY_RESPONSE",
        )
        _mark_failed(job, wrapped)
        raise wrapped from exc
    except Exception as exc:
        wrapped = CTAnalysisError(
            "추론 작업을 처리하는 중 예상하지 못한 오류가 발생했습니다.",
            code="INFERENCE_INTERNAL_ERROR",
            retryable=True,
        )
        _mark_failed(job, wrapped)
        raise wrapped from exc


def open_gcs_uri(uri: str):
    bucket_name, object_key = parse_gcs_uri(uri)
    blob = storage.Client().bucket(bucket_name).blob(object_key)
    if not blob.exists():
        raise CTAnalysisError("영상 파일을 찾을 수 없습니다.", code="CT_ASSET_NOT_FOUND")
    return blob.open("rb"), blob
