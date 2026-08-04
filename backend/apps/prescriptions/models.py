from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


class Prescription(TimeStampedModel):
    """진료 과정에서 의료진이 발행한 처방전."""

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "작성 중"
        ACTIVE = "ACTIVE", "처방 중"
        COMPLETED = "COMPLETED", "처방 완료"
        DISCONTINUED = "DISCONTINUED", "중단"
        CANCELLED = "CANCELLED", "취소"

    encounter = models.ForeignKey(
        "appointments.Encounter",
        on_delete=models.PROTECT,
        related_name="prescriptions",
        verbose_name="진료 건",
    )
    clinical_record = models.ForeignKey(
        "clinical_records.ClinicalRecord",
        on_delete=models.PROTECT,
        related_name="prescriptions",
        verbose_name="진료기록",
    )
    clinician = models.ForeignKey(
        "clinicians.Clinician",
        on_delete=models.PROTECT,
        related_name="prescriptions",
        verbose_name="처방 의료진",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="처방 상태",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="처방 참고사항",
    )
    prescribed_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="처방 일시",
    )
    discontinued_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="중단 일시",
    )

    class Meta:
        ordering = ["-prescribed_at", "-created_at"]
        indexes = [
            models.Index(
                fields=["encounter", "prescribed_at"],
                name="presc_encounter_date_idx",
            ),
            models.Index(
                fields=["clinician", "prescribed_at"],
                name="presc_clinician_date_idx",
            ),
            models.Index(
                fields=["status", "prescribed_at"],
                name="presc_status_date_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    ~models.Q(status="DISCONTINUED")
                    | models.Q(discontinued_at__isnull=False)
                ),
                name="prescription_discontinued_at_required",
            ),
        ]
        verbose_name = "처방전"
        verbose_name_plural = "처방전"

    def clean(self) -> None:
        super().clean()

        if (
            self.clinical_record_id
            and self.encounter_id
            and self.clinical_record.encounter_id
            != self.encounter_id
        ):
            raise ValidationError(
                {
                    "clinical_record": (
                        "처방전의 진료기록과 진료 건이 "
                        "일치해야 합니다."
                    )
                }
            )

        if (
            self.status == self.Status.DISCONTINUED
            and self.discontinued_at is None
        ):
            raise ValidationError(
                {
                    "discontinued_at": (
                        "중단된 처방에는 중단 일시가 필요합니다."
                    )
                }
            )

        if (
            self.status != self.Status.DISCONTINUED
            and self.discontinued_at is not None
        ):
            raise ValidationError(
                {
                    "discontinued_at": (
                        "중단 상태가 아닌 처방에는 "
                        "중단 일시를 입력할 수 없습니다."
                    )
                }
            )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"Prescription #{self.pk} - "
            f"{self.status}"
        )


class PrescriptionItem(TimeStampedModel):
    """처방전에 포함된 개별 약품."""

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="처방전",
    )
    drug = models.ForeignKey(
        "prescriptions.DrugMaster",
        on_delete=models.PROTECT,
        related_name="prescription_items",
        null=True,
        blank=True,
    )
    medicine_name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name="약품명",
    )
    dosage = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[
            MinValueValidator(Decimal("0.0001")),
        ],
        verbose_name="1회 투여량",
    )
    dose_unit = models.CharField(
        max_length=30,
        verbose_name="투여 단위",
        help_text="예: mg, mL, 정, 캡슐",
    )
    frequency = models.CharField(
        max_length=100,
        verbose_name="복용 빈도",
        help_text="예: 1일 3회, BID, TID",
    )
    route = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="투여 경로",
        help_text="예: 경구, 정맥, 근육, 피하",
    )
    instructions = models.TextField(
        blank=True,
        verbose_name="복약 지시",
    )
    start_date = models.DateField(
        verbose_name="복용 시작일",
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="복용 종료일",
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(
                fields=["prescription", "created_at"],
                name="prescitem_presc_idx",
            ),
            models.Index(
                fields=["medicine_name"],
                name="prescitem_medicine_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(end_date__isnull=True)
                    | models.Q(
                        end_date__gte=models.F("start_date")
                    )
                ),
                name="prescriptionitem_end_after_start",
            ),
        ]
        verbose_name = "처방 약품"
        verbose_name_plural = "처방 약품"

    def clean(self) -> None:
        super().clean()

        if (
            self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValidationError(
                {
                    "end_date": (
                        "복용 종료일은 시작일보다 "
                        "빠를 수 없습니다."
                    )
                }
            )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{self.medicine_name} "
            f"{self.dosage}{self.dose_unit}"
        )

class DrugMaster(TimeStampedModel):
    """처방 항목이 참조하는 표준 약품 정보."""

    drug_code = models.CharField(max_length=100, unique=True)
    product_name = models.CharField(max_length=255)
    ingredient = models.TextField()
    strength = models.CharField(max_length=100, blank=True)
    route = models.CharField(max_length=100, blank=True)
    dose_example = models.TextField(blank=True)
    frequency_example = models.CharField(max_length=100, blank=True)
    timing_example = models.CharField(max_length=255, blank=True)
    stroke_related_use_and_caution = models.TextField(blank=True)
    source_url = models.URLField(max_length=500, blank=True)
    clinical_disclaimer = models.TextField(blank=True)

    class Meta:
        db_table = "drug_master"

    def __str__(self):
        return f"{self.drug_code} - {self.product_name}"