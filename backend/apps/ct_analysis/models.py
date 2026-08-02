from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import TimeStampedModel


class CTCase(TimeStampedModel):
    """환자의 CT 검사와 AI 추론 입력 파일을 관리한다."""

    class StudyType(models.TextChoices):
        NCCT = "NCCT", "비조영 뇌 CT"
        CTA = "CTA", "CT 혈관조영"
        CTP = "CTP", "CT 관류"
        OTHER = "OTHER", "기타"

    class Status(models.TextChoices):
        UPLOADED = "UPLOADED", "업로드 완료"
        VALIDATING = "VALIDATING", "검증 중"
        READY = "READY", "추론 준비"
        PROCESSING = "PROCESSING", "추론 중"
        COMPLETED = "COMPLETED", "분석 완료"
        FAILED = "FAILED", "실패"
        ARCHIVED = "ARCHIVED", "보관"

    encounter = models.ForeignKey(
        "appointments.Encounter",
        on_delete=models.PROTECT,
        related_name="ct_cases",
    )
    study_type = models.CharField(
        max_length=16,
        choices=StudyType.choices,
        default=StudyType.NCCT,
    )
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.UPLOADED,
    )

    input_uri = models.CharField(max_length=1024)
    input_sha256 = models.CharField(
        max_length=64,
        db_index=True,
    )
    file_size_bytes = models.PositiveBigIntegerField()
    content_type = models.CharField(
        max_length=100,
        default="application/gzip",
    )

    performed_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_ct_cases",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["status", "created_at"],
                name="ctcase_status_created_idx",
            ),
            models.Index(
                fields=["encounter", "performed_at"],
                name="ctcase_encounter_date_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"CTCase #{self.pk} - {self.study_type} - {self.status}"


class InferenceJob(TimeStampedModel):
    """AI 추론 요청과 실행 상태를 관리한다."""

    class Status(models.TextChoices):
        QUEUED = "QUEUED", "대기"
        PREPARING = "PREPARING", "준비 중"
        RUNNING = "RUNNING", "추론 중"
        SUCCEEDED = "SUCCEEDED", "완료"
        FAILED = "FAILED", "실패"
        CANCELLED = "CANCELLED", "취소"
        TIMED_OUT = "TIMED_OUT", "시간 초과"

    case = models.ForeignKey(
        CTCase,
        on_delete=models.PROTECT,
        related_name="inference_jobs",
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.QUEUED,
    )
    progress = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requested_inference_jobs",
    )

    parameters = models.JSONField(
        default=dict,
        blank=True,
    )
    error_code = models.CharField(
        max_length=100,
        blank=True,
    )
    error_message = models.TextField(blank=True)
    error_retryable = models.BooleanField(default=False)

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["status", "created_at"],
                name="inferjob_status_created_idx",
            ),
            models.Index(
                fields=["case", "status"],
                name="inferjob_case_status_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(progress__gte=0)
                    & models.Q(progress__lte=100)
                ),
                name="inferjob_progress_0_100",
            ),
        ]

    def clean(self) -> None:
        super().clean()

        if (
            self.started_at
            and self.completed_at
            and self.completed_at < self.started_at
        ):
            raise ValidationError(
                {
                    "completed_at": (
                        "완료일시는 시작일시보다 빠를 수 없습니다."
                    )
                }
            )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"InferenceJob #{self.pk} - {self.status}"


class InferenceResult(TimeStampedModel):
    """AI가 생성한 원본 기술 추론 결과를 관리한다."""

    case = models.ForeignKey(
        CTCase,
        on_delete=models.PROTECT,
        related_name="inference_results",
    )
    job = models.OneToOneField(
        InferenceJob,
        on_delete=models.PROTECT,
        related_name="result",
    )

    model_id = models.CharField(max_length=100)
    model_version = models.CharField(max_length=50)
    checkpoint = models.CharField(
        max_length=255,
        blank=True,
    )

    threshold = models.DecimalField(
        max_digits=6,
        decimal_places=5,
        null=True,
        blank=True,
    )

    mask_uri = models.CharField(max_length=1024)
    preview_uri = models.CharField(
        max_length=1024,
        blank=True,
    )

    probability_uri = models.CharField(
        max_length=1024,
        blank=True,
    )
    entropy_uri = models.CharField(
        max_length=1024,
        blank=True,
    )
    uncertainty_uri = models.CharField(
        max_length=1024,
        blank=True,
    )
    xai_uri = models.CharField(
        max_length=1024,
        blank=True,
    )

    lesion_voxels = models.PositiveBigIntegerField(default=0)
    lesion_volume_ml = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        null=True,
        blank=True,
    )
    lesion_slice_count = models.PositiveIntegerField(default=0)
    lesion_slice_start = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    lesion_slice_end = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    max_lesion_slice = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    shape = models.JSONField(
        default=list,
        blank=True,
    )
    spacing = models.JSONField(
        default=list,
        blank=True,
    )

    preprocessing_seconds = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
    )
    inference_seconds = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
    )
    postprocessing_seconds = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
    )
    total_seconds = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
    )
    gpu_memory_peak_mb = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
    )

    raw_result = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["case", "created_at"],
                name="inferresult_case_created_idx",
            ),
            models.Index(
                fields=["model_id", "model_version"],
                name="inferresult_model_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(threshold__isnull=True)
                    | (
                        models.Q(threshold__gte=0)
                        & models.Q(threshold__lte=1)
                    )
                ),
                name="inferresult_threshold_0_1",
            ),
        ]

    def clean(self) -> None:
        super().clean()

        if (
            self.job_id
            and self.case_id
            and self.job.case_id != self.case_id
        ):
            raise ValidationError(
                {
                    "case": (
                        "InferenceResult의 case와 "
                        "InferenceJob의 case가 같아야 합니다."
                    )
                }
            )

        if (
            self.lesion_slice_start is not None
            and self.lesion_slice_end is not None
            and self.lesion_slice_end < self.lesion_slice_start
        ):
            raise ValidationError(
                {
                    "lesion_slice_end": (
                        "병변 종료 슬라이스는 시작 슬라이스보다 "
                        "작을 수 없습니다."
                    )
                }
            )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"InferenceResult #{self.pk} - "
            f"{self.model_id}:{self.model_version}"
        )