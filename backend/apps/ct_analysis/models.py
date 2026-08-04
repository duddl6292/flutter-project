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
        null=True,
        blank=True,
    )
    imaging_study = models.ForeignKey(
        "imaging.ImagingStudy",
        on_delete=models.PROTECT,
        related_name="ct_cases",
        null=True,
        blank=True,
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
            models.Index(
                fields=["imaging_study", "status"],
                name="ctcase_study_status_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(encounter__isnull=False)
                    | models.Q(imaging_study__isnull=False)
                ),
                name="ctcase_clinical_source_req",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.encounter_id is None and self.imaging_study_id is None:
            raise ValidationError("CT 분석 건에는 진료 건 또는 영상 Study가 필요합니다.")
        if self.imaging_study_id and self.imaging_study.modality != "CT":
            raise ValidationError({"imaging_study": "CT 영상 Study만 CT 분석에 사용할 수 있습니다."})
        if self.encounter_id and self.imaging_study_id:
            examination = self.imaging_study.examination
            if self.encounter.patient_id and examination.patient_id != self.encounter.patient_id:
                raise ValidationError({"imaging_study": "영상 환자와 진료 환자가 일치해야 합니다."})
            if self.encounter.hospital_id and examination.hospital_id != self.encounter.hospital_id:
                raise ValidationError({"imaging_study": "영상 병원과 진료 병원이 일치해야 합니다."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"CTCase #{self.pk} - {self.study_type} - {self.status}"


class AIModelVersion(TimeStampedModel):
    """재현 가능한 AI 모델과 체크포인트 버전."""

    model_key = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200)
    version = models.CharField(max_length=64)
    framework = models.CharField(max_length=64, blank=True)
    checkpoint_uri = models.CharField(max_length=1024, blank=True)
    checkpoint_object = models.ForeignKey(
        "assets.StoredObject",
        on_delete=models.PROTECT,
        related_name="ai_model_checkpoints",
        null=True,
        blank=True,
    )
    checkpoint_sha256 = models.CharField(max_length=64, blank=True)
    input_schema_version = models.CharField(max_length=32, blank=True)
    output_schema_version = models.CharField(max_length=32, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    deployed_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["model_key", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["model_key", "version"],
                name="aimodel_key_version_uniq",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.model_key}:{self.version}"


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
    model_version = models.ForeignKey(
        AIModelVersion,
        on_delete=models.PROTECT,
        related_name="inference_jobs",
        null=True,
        blank=True,
    )
    idempotency_key = models.CharField(
        max_length=100,
        null=True,
        blank=True,
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
            models.UniqueConstraint(
                fields=["case", "idempotency_key"],
                condition=(
                    models.Q(idempotency_key__isnull=False)
                    & ~models.Q(idempotency_key="")
                ),
                name="inferjob_case_idem_uniq",
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
    model_version_ref = models.ForeignKey(
        AIModelVersion,
        on_delete=models.PROTECT,
        related_name="inference_results",
        null=True,
        blank=True,
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


class InferenceArtifact(TimeStampedModel):
    """추론 결과에 포함된 마스크·확률맵·설명가능성 파일."""

    class ArtifactType(models.TextChoices):
        SEGMENTATION_MASK = "SEGMENTATION_MASK", "분할 마스크"
        PROBABILITY_MAP = "PROBABILITY_MAP", "확률맵"
        ENTROPY_MAP = "ENTROPY_MAP", "엔트로피맵"
        UNCERTAINTY_MAP = "UNCERTAINTY_MAP", "불확실성맵"
        XAI_MAP = "XAI_MAP", "XAI 맵"
        PREVIEW_IMAGE = "PREVIEW_IMAGE", "미리보기"
        REPORT_JSON = "REPORT_JSON", "결과 JSON"
        OTHER = "OTHER", "기타"

    result = models.ForeignKey(
        InferenceResult,
        on_delete=models.CASCADE,
        related_name="artifacts",
    )
    stored_object = models.OneToOneField(
        "assets.StoredObject",
        on_delete=models.PROTECT,
        related_name="inference_artifact",
    )
    artifact_type = models.CharField(
        max_length=24,
        choices=ArtifactType.choices,
        db_index=True,
    )
    label = models.CharField(max_length=100, blank=True)
    coordinate_space = models.CharField(max_length=64, blank=True)
    is_primary = models.BooleanField(default=False, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["artifact_type", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["result", "artifact_type", "label"],
                condition=models.Q(is_primary=True),
                name="inferartifact_primary_uniq",
            ),
        ]


class InferenceFinding(TimeStampedModel):
    """추론 결과에서 탐지된 개별 병변과 측정값."""

    result = models.ForeignKey(
        InferenceResult,
        on_delete=models.CASCADE,
        related_name="findings",
    )
    finding_number = models.PositiveIntegerField()
    finding_type = models.CharField(max_length=100)
    label = models.CharField(max_length=100, blank=True)
    confidence = models.DecimalField(
        max_digits=7,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )
    lesion_voxels = models.PositiveBigIntegerField(default=0)
    lesion_volume_ml = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        null=True,
        blank=True,
    )
    slice_start = models.PositiveIntegerField(null=True, blank=True)
    slice_end = models.PositiveIntegerField(null=True, blank=True)
    max_slice = models.PositiveIntegerField(null=True, blank=True)
    centroid = models.JSONField(default=list, blank=True)
    bounding_box = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["finding_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["result", "finding_number"],
                name="inferfinding_number_uniq",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(confidence__isnull=True)
                    | (models.Q(confidence__gte=0) & models.Q(confidence__lte=1))
                ),
                name="inferfinding_confidence_valid",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(slice_start__isnull=True)
                    | models.Q(slice_end__isnull=True)
                    | models.Q(slice_end__gte=models.F("slice_start"))
                ),
                name="inferfinding_slice_valid",
            ),
        ]


class InferenceReview(TimeStampedModel):
    """AI 결과에 대한 의료진의 승인·반려·수정 검토."""

    class Decision(models.TextChoices):
        NEEDS_REVIEW = "NEEDS_REVIEW", "검토 필요"
        ACCEPTED = "ACCEPTED", "승인"
        REJECTED = "REJECTED", "반려"
        MODIFIED = "MODIFIED", "수정"

    result = models.ForeignKey(
        InferenceResult,
        on_delete=models.PROTECT,
        related_name="reviews",
    )
    reviewer = models.ForeignKey(
        "clinicians.Clinician",
        on_delete=models.PROTECT,
        related_name="inference_reviews",
    )
    sequence = models.PositiveIntegerField(default=1)
    decision = models.CharField(
        max_length=16,
        choices=Decision.choices,
        default=Decision.NEEDS_REVIEW,
        db_index=True,
    )
    comment = models.TextField(blank=True)
    corrected_artifact = models.ForeignKey(
        InferenceArtifact,
        on_delete=models.PROTECT,
        related_name="review_corrections",
        null=True,
        blank=True,
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["sequence", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["result", "sequence"],
                name="inferreview_result_seq_uniq",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.corrected_artifact_id and self.corrected_artifact.result_id != self.result_id:
            raise ValidationError({"corrected_artifact": "수정 파일은 동일한 추론 결과에 속해야 합니다."})
        if self.decision == self.Decision.MODIFIED and self.corrected_artifact_id is None:
            raise ValidationError({"corrected_artifact": "수정 검토에는 수정 결과 파일이 필요합니다."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
