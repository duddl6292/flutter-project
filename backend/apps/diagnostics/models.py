from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedModel


class ExaminationCatalog(TimeStampedModel):
    """병원에서 사용하는 검사 코드와 표시 정보를 관리한다."""

    class Category(models.TextChoices):
        LABORATORY = "LABORATORY", "진단검사"
        IMAGING = "IMAGING", "영상검사"
        PHYSIOLOGY = "PHYSIOLOGY", "생리기능검사"
        PATHOLOGY = "PATHOLOGY", "병리검사"
        NEURO_ASSESSMENT = "NEURO_ASSESSMENT", "신경계 평가"
        OTHER = "OTHER", "기타"

    code = models.CharField(max_length=64)
    name = models.CharField(max_length=200)
    category = models.CharField(
        max_length=24,
        choices=Category.choices,
        db_index=True,
    )
    specimen_type = models.CharField(max_length=100, blank=True)
    default_unit = models.CharField(max_length=40, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["category", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "code"],
                name="examcatalog_category_code_uniq",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class Examination(TimeStampedModel):
    """환자에게 수행된 범용 검사의 공통 헤더."""

    class Status(models.TextChoices):
        REGISTERED = "REGISTERED", "등록"
        IN_PROGRESS = "IN_PROGRESS", "검사 중"
        PRELIMINARY = "PRELIMINARY", "예비 결과"
        FINAL = "FINAL", "최종 결과"
        CORRECTED = "CORRECTED", "정정"
        CANCELLED = "CANCELLED", "취소"

    class Source(models.TextChoices):
        INTERNAL = "INTERNAL", "원내"
        EXTERNAL = "EXTERNAL", "외부 기관"
        PATIENT_UPLOAD = "PATIENT_UPLOAD", "환자 업로드"

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="examinations",
    )
    encounter = models.ForeignKey(
        "appointments.Encounter",
        on_delete=models.PROTECT,
        related_name="examinations",
        null=True,
        blank=True,
    )
    hospital = models.ForeignKey(
        "hospitals.Hospital",
        on_delete=models.PROTECT,
        related_name="examinations",
    )
    catalog = models.ForeignKey(
        ExaminationCatalog,
        on_delete=models.PROTECT,
        related_name="examinations",
        null=True,
        blank=True,
    )
    test_code = models.CharField(max_length=64, db_index=True)
    test_name = models.CharField(max_length=200)
    category = models.CharField(
        max_length=24,
        choices=ExaminationCatalog.Category.choices,
        db_index=True,
    )
    accession_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.REGISTERED,
        db_index=True,
    )
    source = models.CharField(
        max_length=24,
        choices=Source.choices,
        default=Source.INTERNAL,
    )
    ordered_by = models.ForeignKey(
        "clinicians.Clinician",
        on_delete=models.PROTECT,
        related_name="ordered_examinations",
        null=True,
        blank=True,
    )
    performed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    result_available_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-performed_at", "-created_at"]
        indexes = [
            models.Index(
                fields=["patient", "performed_at"],
                name="exam_patient_performed_idx",
            ),
            models.Index(
                fields=["hospital", "status"],
                name="exam_hospital_status_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["hospital", "accession_number"],
                condition=~models.Q(accession_number=""),
                name="exam_hospital_accession_uniq",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.encounter_id and self.encounter.patient_id != self.patient_id:
            raise ValidationError({"encounter": "검사 환자와 진료 건의 환자가 일치해야 합니다."})
        if self.encounter_id and self.encounter.hospital_id != self.hospital_id:
            raise ValidationError({"hospital": "검사 병원과 진료 병원이 일치해야 합니다."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.test_name} - {self.patient_id}"


class ExaminationObservation(TimeStampedModel):
    """혈액 수치처럼 한 검사에 포함되는 개별 관찰 결과."""

    class ValueType(models.TextChoices):
        NUMERIC = "NUMERIC", "숫자"
        TEXT = "TEXT", "문자"
        CODED = "CODED", "코드"
        BOOLEAN = "BOOLEAN", "참/거짓"

    class Interpretation(models.TextChoices):
        NORMAL = "NORMAL", "정상"
        LOW = "LOW", "낮음"
        HIGH = "HIGH", "높음"
        ABNORMAL = "ABNORMAL", "이상"
        CRITICAL = "CRITICAL", "위험"
        UNKNOWN = "UNKNOWN", "미판정"

    examination = models.ForeignKey(
        Examination,
        on_delete=models.CASCADE,
        related_name="observations",
    )
    code = models.CharField(max_length=64)
    name = models.CharField(max_length=200)
    sequence = models.PositiveIntegerField(default=1)
    value_type = models.CharField(max_length=16, choices=ValueType.choices)
    numeric_value = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
    )
    text_value = models.TextField(blank=True)
    coded_value = models.CharField(max_length=100, blank=True)
    boolean_value = models.BooleanField(null=True, blank=True)
    unit = models.CharField(max_length=40, blank=True)
    reference_low = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
    )
    reference_high = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
    )
    reference_text = models.CharField(max_length=200, blank=True)
    interpretation = models.CharField(
        max_length=16,
        choices=Interpretation.choices,
        default=Interpretation.UNKNOWN,
        db_index=True,
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["sequence", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["examination", "code", "sequence"],
                name="examobs_exam_code_seq_uniq",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(reference_low__isnull=True)
                    | models.Q(reference_high__isnull=True)
                    | models.Q(reference_high__gte=models.F("reference_low"))
                ),
                name="examobs_reference_range_valid",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        present = {
            self.ValueType.NUMERIC: self.numeric_value is not None,
            self.ValueType.TEXT: bool(self.text_value),
            self.ValueType.CODED: bool(self.coded_value),
            self.ValueType.BOOLEAN: self.boolean_value is not None,
        }
        if not present.get(self.value_type, False):
            raise ValidationError("검사 결과 유형에 맞는 값이 필요합니다.")
        if self.reference_low is not None and self.reference_high is not None:
            if Decimal(self.reference_high) < Decimal(self.reference_low):
                raise ValidationError({"reference_high": "상한값은 하한값보다 작을 수 없습니다."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class DiagnosticReport(TimeStampedModel):
    """범용 검사에 대한 의료진의 공식 판독 보고서."""

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "작성 중"
        FINAL = "FINAL", "최종"
        CORRECTED = "CORRECTED", "정정"
        CANCELLED = "CANCELLED", "취소"

    examination = models.ForeignKey(
        Examination,
        on_delete=models.PROTECT,
        related_name="reports",
    )
    supersedes = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="corrections",
        null=True,
        blank=True,
    )
    revision_number = models.PositiveIntegerField(default=1)
    author = models.ForeignKey(
        "clinicians.Clinician",
        on_delete=models.PROTECT,
        related_name="diagnostic_reports",
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    conclusion = models.TextField(blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="signed_diagnostic_reports",
        null=True,
        blank=True,
    )
    is_released_to_patient = models.BooleanField(default=False, db_index=True)
    released_at = models.DateTimeField(null=True, blank=True)
    released_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="released_diagnostic_reports",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-issued_at", "-created_at"]
        indexes = [
            models.Index(
                fields=["examination", "status"],
                name="diagreport_exam_status_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["examination", "revision_number"],
                name="diagreport_exam_revision_uniq",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(is_released_to_patient=False)
                    | models.Q(
                        status__in=["FINAL", "CORRECTED"],
                        released_at__isnull=False,
                        released_by__isnull=False,
                    )
                ),
                name="diagreport_release_valid",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.supersedes_id and self.supersedes.examination_id != self.examination_id:
            raise ValidationError(
                {"supersedes": "정정 보고서는 동일한 검사의 보고서를 대상으로 해야 합니다."}
            )

    def save(self, *args, **kwargs) -> None:
        if self._state.adding and self.examination_id:
            latest = (
                type(self).objects
                .filter(examination_id=self.examination_id)
                .order_by("-revision_number", "-created_at")
                .first()
            )
            if latest and self.revision_number <= latest.revision_number:
                self.revision_number = latest.revision_number + 1
            if (
                latest
                and self.status == self.Status.CORRECTED
                and self.supersedes_id is None
            ):
                self.supersedes = latest
        self.full_clean()
        super().save(*args, **kwargs)


class DiagnosticReportAsset(TimeStampedModel):
    """공식 검사 보고서와 함께 제공되는 PDF·이미지·원본 파일."""

    class AssetType(models.TextChoices):
        REPORT = "REPORT", "보고서"
        PATIENT_COPY = "PATIENT_COPY", "환자용 사본"
        SOURCE = "SOURCE", "검사 원본"
        OTHER = "OTHER", "기타"

    report = models.ForeignKey(
        DiagnosticReport,
        on_delete=models.CASCADE,
        related_name="assets",
    )
    stored_object = models.OneToOneField(
        "assets.StoredObject",
        on_delete=models.PROTECT,
        related_name="diagnostic_report_asset",
    )
    asset_type = models.CharField(max_length=16, choices=AssetType.choices)
    display_name = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["asset_type", "created_at"]


class ExaminationStatusHistory(TimeStampedModel):
    """검사 진행 상태의 변경 이력."""

    examination = models.ForeignKey(
        Examination,
        on_delete=models.PROTECT,
        related_name="status_history",
    )
    previous_status = models.CharField(max_length=16, blank=True)
    new_status = models.CharField(max_length=16, choices=Examination.Status.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="examination_status_changes",
    )
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(
                fields=["examination", "created_at"],
                name="examhist_exam_date_idx",
            ),
        ]


class DiagnosticReportStatusHistory(TimeStampedModel):
    """공식 검사 보고서의 확정·정정·공개 이력."""

    report = models.ForeignKey(
        DiagnosticReport,
        on_delete=models.PROTECT,
        related_name="status_history",
    )
    previous_status = models.CharField(max_length=16, blank=True)
    new_status = models.CharField(max_length=16, choices=DiagnosticReport.Status.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="diagnostic_report_status_changes",
    )
    reason = models.TextField(blank=True)
    is_released_to_patient = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(
                fields=["report", "created_at"],
                name="diagreporthist_report_idx",
            ),
        ]
