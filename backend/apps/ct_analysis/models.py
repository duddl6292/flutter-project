from django.conf import settings
from django.db import models

from apps.core.models import UUIDTimeStampedModel
from apps.patients.models import Patient


class CTCase(UUIDTimeStampedModel):
    class StudyType(models.TextChoices):
        BRAIN_CT = "BRAIN_CT", "Brain CT"

    class Status(models.TextChoices):
        CREATED = "CREATED", "Created"
        UPLOADING = "UPLOADING", "Uploading"
        UPLOADED = "UPLOADED", "Uploaded"
        INFERENCE_QUEUED = "INFERENCE_QUEUED", "Inference queued"
        INFERENCE_RUNNING = "INFERENCE_RUNNING", "Inference running"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="ct_cases")
    study_type = models.CharField(max_length=16, choices=StudyType.choices, default=StudyType.BRAIN_CT)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.CREATED)
    input_uri = models.CharField(max_length=1000, blank=True)
    input_sha256 = models.CharField(max_length=64, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_ct_cases")


class InferenceJob(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        QUEUED = "QUEUED", "Queued"
        RUNNING = "RUNNING", "Running"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    case = models.ForeignKey(CTCase, on_delete=models.CASCADE, related_name="jobs")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    progress = models.PositiveSmallIntegerField(default=0)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="inference_jobs")
    parameters = models.JSONField(default=dict, blank=True)
    error_code = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    error_retryable = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(progress__gte=0) & models.Q(progress__lte=100),
                name="inference_job_progress_range",
            )
        ]


class InferenceResult(UUIDTimeStampedModel):
    case = models.OneToOneField(CTCase, on_delete=models.CASCADE, related_name="result")
    job = models.OneToOneField(InferenceJob, on_delete=models.CASCADE, related_name="result")
    model_id = models.CharField(max_length=100)
    model_version = models.CharField(max_length=100)
    checkpoint = models.CharField(max_length=255, blank=True)
    threshold = models.FloatField(null=True, blank=True)
    mask_uri = models.CharField(max_length=1000, blank=True)
    preview_uri = models.CharField(max_length=1000, blank=True)
    lesion_voxels = models.BigIntegerField(default=0)
    lesion_volume_ml = models.FloatField(default=0)
    lesion_slice_count = models.PositiveIntegerField(default=0)
    lesion_slice_start = models.IntegerField(null=True, blank=True)
    lesion_slice_end = models.IntegerField(null=True, blank=True)
    max_lesion_slice = models.IntegerField(null=True, blank=True)
    shape = models.JSONField(default=list)
    spacing = models.JSONField(default=list)
    preprocessing_seconds = models.FloatField(default=0)
    inference_seconds = models.FloatField(default=0)
    postprocessing_seconds = models.FloatField(default=0)
    total_seconds = models.FloatField(default=0)
    raw_result = models.JSONField(default=dict)
