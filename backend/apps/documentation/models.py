from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


class DocumentationRule(TimeStampedModel):
    """진료 유형별 필수 문서와 항목을 판정하는 규칙."""

    class DocumentType(models.TextChoices):
        CLINICAL_RECORD = "CLINICAL_RECORD", "진료기록"
        DIAGNOSIS = "DIAGNOSIS", "진단"
        PRESCRIPTION = "PRESCRIPTION", "처방"
        TEST_RESULT = "TEST_RESULT", "검사결과"
        CONSULTATION = "CONSULTATION", "협진기록"
        DISCHARGE_SUMMARY = "DISCHARGE_SUMMARY", "퇴원요약"
        SIGNATURE = "SIGNATURE", "전자서명"
        OTHER = "OTHER", "기타"

    hospital = models.ForeignKey(
        "hospitals.Hospital",
        on_delete=models.CASCADE,
        related_name="documentation_rules",
        null=True,
        blank=True,
        help_text="비어 있으면 모든 병원에 적용되는 기본 규칙입니다.",
    )
    rule_code = models.CharField(max_length=64)
    name = models.CharField(max_length=200)
    document_type = models.CharField(max_length=24, choices=DocumentType.choices)
    encounter_type = models.CharField(max_length=16, blank=True)
    required_fields = models.JSONField(default=list, blank=True)
    completion_due_minutes = models.PositiveIntegerField(default=1440)
    severity = models.CharField(max_length=16, default="WARNING")
    is_active = models.BooleanField(default=True, db_index=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["document_type", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["hospital", "rule_code", "encounter_type"],
                condition=models.Q(hospital__isnull=False),
                name="docrule_hospital_code_uniq",
            ),
            models.UniqueConstraint(
                fields=["rule_code", "encounter_type"],
                condition=models.Q(hospital__isnull=True),
                name="docrule_default_code_uniq",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.rule_code} - {self.name}"


class DocumentationDeficiency(TimeStampedModel):
    """진료 건에서 발견된 하나의 미비기록 보완 작업."""

    class DetectionSource(models.TextChoices):
        AUTOMATIC = "AUTOMATIC", "자동 판정"
        MANUAL = "MANUAL", "수동 등록"

    class Status(models.TextChoices):
        OPEN = "OPEN", "미비"
        IN_PROGRESS = "IN_PROGRESS", "보완 중"
        SUBMITTED = "SUBMITTED", "검토 요청"
        RESOLVED = "RESOLVED", "완료"
        REJECTED = "REJECTED", "보완 반려"
        WAIVED = "WAIVED", "면제"

    encounter = models.ForeignKey(
        "appointments.Encounter",
        on_delete=models.PROTECT,
        related_name="documentation_deficiencies",
    )
    rule = models.ForeignKey(
        DocumentationRule,
        on_delete=models.PROTECT,
        related_name="deficiencies",
        null=True,
        blank=True,
    )
    assigned_to = models.ForeignKey(
        "clinicians.Clinician",
        on_delete=models.PROTECT,
        related_name="assigned_documentation_deficiencies",
    )
    detected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="detected_documentation_deficiencies",
        null=True,
        blank=True,
    )
    detection_source = models.CharField(
        max_length=16,
        choices=DetectionSource.choices,
        default=DetectionSource.AUTOMATIC,
    )
    document_type = models.CharField(
        max_length=24,
        choices=DocumentationRule.DocumentType.choices,
        db_index=True,
    )
    clinical_record = models.ForeignKey(
        "clinical_records.ClinicalRecord",
        on_delete=models.PROTECT,
        related_name="documentation_deficiencies",
        null=True,
        blank=True,
    )
    prescription = models.ForeignKey(
        "prescriptions.Prescription",
        on_delete=models.PROTECT,
        related_name="documentation_deficiencies",
        null=True,
        blank=True,
    )
    test_result = models.ForeignKey(
        "test_results.TestResult",
        on_delete=models.PROTECT,
        related_name="documentation_deficiencies",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    detected_at = models.DateTimeField(default=timezone.now, db_index=True)
    due_at = models.DateTimeField(db_index=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="resolved_documentation_deficiencies",
        null=True,
        blank=True,
    )
    resolution_note = models.TextField(blank=True)

    class Meta:
        ordering = ["due_at", "-detected_at"]
        indexes = [
            models.Index(
                fields=["assigned_to", "status", "due_at"],
                name="docdef_assignee_status_idx",
            ),
            models.Index(
                fields=["encounter", "status"],
                name="docdef_encounter_status_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(due_at__gte=models.F("detected_at")),
                name="docdef_due_after_detected",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        status__in=["RESOLVED", "WAIVED"],
                        resolved_at__isnull=False,
                        resolved_by__isnull=False,
                    )
                    | ~models.Q(status__in=["RESOLVED", "WAIVED"])
                ),
                name="docdef_resolved_at_req",
            ),
            models.CheckConstraint(
                condition=(
                    ~(
                        models.Q(clinical_record__isnull=False)
                        & models.Q(prescription__isnull=False)
                    )
                    & ~(
                        models.Q(clinical_record__isnull=False)
                        & models.Q(test_result__isnull=False)
                    )
                    & ~(
                        models.Q(prescription__isnull=False)
                        & models.Q(test_result__isnull=False)
                    )
                ),
                name="docdef_at_most_one_source",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        linked = [
            self.clinical_record_id is not None,
            self.prescription_id is not None,
            self.test_result_id is not None,
        ]
        if sum(linked) > 1:
            raise ValidationError("미비기록의 원본 문서는 하나만 연결할 수 있습니다.")
        if self.clinical_record_id and self.clinical_record.encounter_id != self.encounter_id:
            raise ValidationError({"clinical_record": "진료기록과 미비기록의 진료 건이 일치해야 합니다."})
        if self.prescription_id and self.prescription.encounter_id != self.encounter_id:
            raise ValidationError({"prescription": "처방과 미비기록의 진료 건이 일치해야 합니다."})
        if self.test_result_id and self.test_result.encounter_id != self.encounter_id:
            raise ValidationError({"test_result": "검사결과와 미비기록의 진료 건이 일치해야 합니다."})
        if self.status in {self.Status.RESOLVED, self.Status.WAIVED}:
            if self.resolved_at is None or self.resolved_by_id is None:
                raise ValidationError("완료 또는 면제 시 처리 일시와 처리자가 필요합니다.")

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class DocumentationDeficiencyItem(TimeStampedModel):
    """한 미비기록에 포함된 개별 누락 항목."""

    class Status(models.TextChoices):
        MISSING = "MISSING", "누락"
        RESOLVED = "RESOLVED", "보완"
        WAIVED = "WAIVED", "면제"

    deficiency = models.ForeignKey(
        DocumentationDeficiency,
        on_delete=models.CASCADE,
        related_name="items",
    )
    item_code = models.CharField(max_length=64)
    field_name = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=255)
    sequence = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.MISSING,
        db_index=True,
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="resolved_documentation_items",
        null=True,
        blank=True,
    )
    resolution_note = models.TextField(blank=True)

    class Meta:
        ordering = ["sequence", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["deficiency", "item_code"],
                name="docdefitem_code_uniq",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(status="MISSING", resolved_at__isnull=True, resolved_by__isnull=True)
                    | models.Q(status__in=["RESOLVED", "WAIVED"], resolved_at__isnull=False, resolved_by__isnull=False)
                ),
                name="docdefitem_resolution_valid",
            ),
        ]


class DocumentationReview(TimeStampedModel):
    """보완 제출 건에 대한 검토 이력."""

    class Decision(models.TextChoices):
        APPROVED = "APPROVED", "승인"
        REJECTED = "REJECTED", "반려"
        WAIVED = "WAIVED", "면제"

    deficiency = models.ForeignKey(
        DocumentationDeficiency,
        on_delete=models.PROTECT,
        related_name="reviews",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="documentation_reviews",
    )
    decision = models.CharField(max_length=16, choices=Decision.choices)
    comment = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-reviewed_at"]


class DocumentationStatusHistory(TimeStampedModel):
    """미비기록 상태 변경 감사 이력."""

    deficiency = models.ForeignKey(
        DocumentationDeficiency,
        on_delete=models.PROTECT,
        related_name="status_history",
    )
    previous_status = models.CharField(max_length=16, blank=True)
    new_status = models.CharField(max_length=16, choices=DocumentationDeficiency.Status.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="documentation_status_changes",
    )
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(
                fields=["deficiency", "created_at"],
                name="docdefhist_def_date_idx",
            ),
        ]
