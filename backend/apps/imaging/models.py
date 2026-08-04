from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedModel


class ImagingStudy(TimeStampedModel):
    """환자에게 수행된 하나의 영상 검사 Study."""

    class Modality(models.TextChoices):
        CT = "CT", "CT"
        MR = "MR", "MRI"
        CR = "CR", "X-ray"
        US = "US", "초음파"
        PT = "PT", "PET"
        NM = "NM", "핵의학"
        OTHER = "OTHER", "기타"

    class Status(models.TextChoices):
        IMPORTING = "IMPORTING", "가져오는 중"
        VALIDATING = "VALIDATING", "검증 중"
        READY = "READY", "사용 가능"
        FAILED = "FAILED", "실패"
        ARCHIVED = "ARCHIVED", "보관"

    examination = models.OneToOneField(
        "diagnostics.Examination",
        on_delete=models.PROTECT,
        related_name="imaging_study",
    )
    modality = models.CharField(
        max_length=16,
        choices=Modality.choices,
        db_index=True,
    )
    study_instance_uid = models.CharField(max_length=128)
    study_description = models.CharField(max_length=255, blank=True)
    body_part = models.CharField(max_length=100, blank=True)
    referring_clinician_name = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.IMPORTING,
        db_index=True,
    )
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="imported_imaging_studies",
    )
    imported_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-examination__performed_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["study_instance_uid"],
                name="imagingstudy_uid_uniq",
            ),
        ]
        indexes = [
            models.Index(
                fields=["modality", "status"],
                name="imgstudy_modality_status_idx",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.examination_id and self.examination.category != "IMAGING":
            raise ValidationError({"examination": "영상 검사 유형의 검사만 연결할 수 있습니다."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.modality} - {self.study_instance_uid}"


class ImagingSeries(TimeStampedModel):
    """DICOM Study 안의 개별 Series."""

    study = models.ForeignKey(
        ImagingStudy,
        on_delete=models.CASCADE,
        related_name="series",
    )
    series_instance_uid = models.CharField(max_length=128)
    series_number = models.IntegerField(null=True, blank=True)
    modality = models.CharField(max_length=16, choices=ImagingStudy.Modality.choices)
    description = models.CharField(max_length=255, blank=True)
    body_part = models.CharField(max_length=100, blank=True)
    instance_count = models.PositiveIntegerField(default=0)
    rows = models.PositiveIntegerField(null=True, blank=True)
    columns = models.PositiveIntegerField(null=True, blank=True)
    slice_thickness = models.DecimalField(
        max_digits=10,
        decimal_places=5,
        null=True,
        blank=True,
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["series_number", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["study", "series_instance_uid"],
                name="imgseries_study_uid_uniq",
            ),
        ]
        indexes = [
            models.Index(
                fields=["study", "series_number"],
                name="imgseries_study_num_idx",
            ),
        ]


class ImagingAsset(TimeStampedModel):
    """영상 원본, 변환본, manifest 및 미리보기 파일."""

    class AssetType(models.TextChoices):
        ORIGINAL_DICOM = "ORIGINAL_DICOM", "DICOM 원본"
        DICOM_MANIFEST = "DICOM_MANIFEST", "DICOM Manifest"
        NIFTI_VOLUME = "NIFTI_VOLUME", "NIfTI 볼륨"
        NRRD_VOLUME = "NRRD_VOLUME", "NRRD 볼륨"
        THUMBNAIL = "THUMBNAIL", "썸네일"
        PREVIEW = "PREVIEW", "미리보기"
        OTHER = "OTHER", "기타"

    class ConversionStatus(models.TextChoices):
        NOT_REQUIRED = "NOT_REQUIRED", "변환 불필요"
        PENDING = "PENDING", "변환 대기"
        PROCESSING = "PROCESSING", "변환 중"
        COMPLETED = "COMPLETED", "변환 완료"
        FAILED = "FAILED", "변환 실패"

    study = models.ForeignKey(
        ImagingStudy,
        on_delete=models.CASCADE,
        related_name="assets",
    )
    series = models.ForeignKey(
        ImagingSeries,
        on_delete=models.CASCADE,
        related_name="assets",
        null=True,
        blank=True,
    )
    stored_object = models.OneToOneField(
        "assets.StoredObject",
        on_delete=models.PROTECT,
        related_name="imaging_asset",
    )
    asset_type = models.CharField(
        max_length=24,
        choices=AssetType.choices,
        db_index=True,
    )
    is_primary = models.BooleanField(default=False, db_index=True)
    conversion_status = models.CharField(
        max_length=16,
        choices=ConversionStatus.choices,
        default=ConversionStatus.NOT_REQUIRED,
        db_index=True,
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["asset_type", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["study", "asset_type"],
                condition=models.Q(is_primary=True),
                name="imgasset_primary_type_uniq",
            ),
        ]
        indexes = [
            models.Index(
                fields=["study", "asset_type"],
                name="imgasset_study_type_idx",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.series_id and self.series.study_id != self.study_id:
            raise ValidationError({"series": "Series는 동일한 Study에 속해야 합니다."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class ImagingAnnotation(TimeStampedModel):
    """Niivue에서 작성하거나 수정한 주석·마스크의 버전."""

    class AnnotationType(models.TextChoices):
        SEGMENTATION = "SEGMENTATION", "분할 마스크"
        ROI = "ROI", "관심 영역"
        DRAWING = "DRAWING", "그리기"
        MEASUREMENT = "MEASUREMENT", "측정"

    study = models.ForeignKey(
        ImagingStudy,
        on_delete=models.PROTECT,
        related_name="annotations",
    )
    inference_result = models.ForeignKey(
        "ct_analysis.InferenceResult",
        on_delete=models.PROTECT,
        related_name="annotations",
        null=True,
        blank=True,
    )
    parent_annotation = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="revisions",
        null=True,
        blank=True,
    )
    stored_object = models.OneToOneField(
        "assets.StoredObject",
        on_delete=models.PROTECT,
        related_name="imaging_annotation",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_imaging_annotations",
    )
    annotation_type = models.CharField(max_length=24, choices=AnnotationType.choices)
    version = models.PositiveIntegerField(default=1)
    label = models.CharField(max_length=100, blank=True)
    is_final = models.BooleanField(default=False, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["study", "annotation_type", "label", "version"],
                name="imgannotation_version_uniq",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.parent_annotation_id and self.parent_annotation.study_id != self.study_id:
            raise ValidationError({"parent_annotation": "이전 버전은 동일한 Study에 속해야 합니다."})
        if self.inference_result_id and self.inference_result.case.imaging_study_id != self.study_id:
            raise ValidationError({"inference_result": "AI 결과와 주석의 Study가 일치해야 합니다."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
