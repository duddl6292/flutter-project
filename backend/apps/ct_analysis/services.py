import logging

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .adapters import InferenceClientError, get_inference_client, get_storage_service
from .models import CTCase, InferenceJob, InferenceResult

logger = logging.getLogger(__name__)


@transaction.atomic
def issue_upload_url(case, content_type):
    case = CTCase.objects.select_for_update().get(pk=case.pk)
    if case.status not in {CTCase.Status.CREATED, CTCase.Status.UPLOADING}:
        raise ValidationError("Upload URL cannot be issued in the current state.")
    target = get_storage_service().create_upload_url(case, content_type)
    case.status = CTCase.Status.UPLOADING
    case.input_uri = target.object_path
    case.save(update_fields=("status", "input_uri", "updated_at"))
    return target


@transaction.atomic
def complete_upload(case, metadata):
    case = CTCase.objects.select_for_update().get(pk=case.pk)
    if case.status != CTCase.Status.UPLOADING:
        raise ValidationError("Case is not uploading.")
    try:
        get_storage_service().verify_upload(expected_path=case.input_uri, **metadata)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc
    prefix = "gs://" + settings.GCS_BUCKET_MEDICAL_DATA + "/" if settings.STORAGE_BACKEND == "gcs" else "mock://"
    case.input_uri = prefix + metadata["object_path"]
    case.input_sha256 = metadata["sha256"].lower()
    case.status = CTCase.Status.UPLOADED
    case.save(update_fields=("input_uri", "input_sha256", "status", "updated_at"))
    return case


def _dispatch(job_id):
    job = InferenceJob.objects.select_related("case").get(pk=job_id)
    try:
        get_inference_client().create_job({
            "job_id": job.id, "case_id": job.case_id,
            "input_uri": job.case.input_uri, "parameters": job.parameters,
        })
    except InferenceClientError as exc:
        logger.exception("inference_dispatch_failed", extra={"job_id": str(job_id)})
        with transaction.atomic():
            locked = InferenceJob.objects.select_for_update().get(pk=job_id)
            locked.status = InferenceJob.Status.FAILED
            locked.error_code = "INFERENCE_GATEWAY_UNAVAILABLE"
            locked.error_message = str(exc)
            locked.error_retryable = True
            locked.completed_at = timezone.now()
            locked.save()
            CTCase.objects.filter(pk=locked.case_id).update(status=CTCase.Status.FAILED)


@transaction.atomic
def request_inference(case, requested_by, parameters):
    case = CTCase.objects.select_for_update().get(pk=case.pk)
    if case.status != CTCase.Status.UPLOADED:
        raise ValidationError("Case must be uploaded before inference.")
    job = InferenceJob.objects.create(
        case=case, requested_by=requested_by, parameters=parameters,
        status=InferenceJob.Status.QUEUED,
    )
    case.status = CTCase.Status.INFERENCE_QUEUED
    case.save(update_fields=("status", "updated_at"))
    transaction.on_commit(lambda: _dispatch(job.id))
    return job


@transaction.atomic
def process_callback(payload):
    job = InferenceJob.objects.select_for_update().select_related("case").get(pk=payload["job_id"])
    status = payload["status"]
    if job.status in {InferenceJob.Status.COMPLETED, InferenceJob.Status.FAILED, InferenceJob.Status.CANCELLED}:
        return job
    if status == InferenceJob.Status.COMPLETED:
        raw = payload.get("result", {})
        defaults = {field: raw.get(field, default) for field, default in {
            "model_id": "unknown", "model_version": "unknown", "checkpoint": "",
            "threshold": None, "mask_uri": "", "preview_uri": "", "lesion_voxels": 0,
            "lesion_volume_ml": 0, "lesion_slice_count": 0, "lesion_slice_start": None,
            "lesion_slice_end": None, "max_lesion_slice": None, "shape": [], "spacing": [],
            "preprocessing_seconds": 0, "inference_seconds": 0,
            "postprocessing_seconds": 0, "total_seconds": 0,
        }.items()}
        defaults["raw_result"] = raw
        InferenceResult.objects.update_or_create(job=job, defaults={"case": job.case, **defaults})
        job.status, job.progress, job.completed_at = status, 100, timezone.now()
        job.case.status = CTCase.Status.COMPLETED
    elif status == InferenceJob.Status.FAILED:
        error = payload.get("error", {})
        job.status, job.completed_at = status, timezone.now()
        job.error_code = error.get("code", "INFERENCE_FAILED")
        job.error_message = error.get("message", "")
        job.error_retryable = error.get("retryable", False)
        job.case.status = CTCase.Status.FAILED
    else:
        job.status = status
        job.progress = payload.get("progress", job.progress)
        if status == InferenceJob.Status.RUNNING and not job.started_at:
            job.started_at = timezone.now()
        job.case.status = CTCase.Status.INFERENCE_RUNNING
    job.save()
    job.case.save(update_fields=("status", "updated_at"))
    return job
