from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


def validate_days_of_week(value) -> None:
    """요일 목록을 ISO 기준 1(월요일)~7(일요일)로 검증한다."""

    if not isinstance(value, list):
        raise ValidationError(
            "복용 요일은 배열 형식이어야 합니다."
        )

    invalid_days = [
        day
        for day in value
        if (
            isinstance(day, bool)
            or not isinstance(day, int)
            or day < 1
            or day > 7
        )
    ]

    if invalid_days:
        raise ValidationError(
            "복용 요일은 1(월요일)부터 "
            "7(일요일) 사이의 정수여야 합니다."
        )

    if len(value) != len(set(value)):
        raise ValidationError(
            "복용 요일에는 중복된 값을 입력할 수 없습니다."
        )


class MedicationSchedule(TimeStampedModel):
    """처방 약품의 복약 예정 시간과 반복 요일을 관리한다."""

    prescription_item = models.ForeignKey(
        "prescriptions.PrescriptionItem",
        on_delete=models.PROTECT,
        related_name="medication_schedules",
        verbose_name="처방 약품",
    )
    dose_time = models.TimeField(
        verbose_name="복용 예정 시간",
    )
    days_of_week = models.JSONField(
        default=list,
        blank=True,
        validators=[validate_days_of_week],
        verbose_name="복용 요일",
        help_text=(
            "ISO 요일 기준 1=월요일, 7=일요일입니다. "
            "빈 배열은 매일 복용을 의미합니다."
        ),
    )
    start_date = models.DateField(
        verbose_name="복약 시작일",
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="복약 종료일",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="활성 여부",
    )

    class Meta:
        ordering = [
            "start_date",
            "dose_time",
            "created_at",
        ]
        indexes = [
            models.Index(
                fields=["prescription_item", "is_active"],
                name="medsched_item_active_idx",
            ),
            models.Index(
                fields=["is_active", "start_date", "end_date"],
                name="medsched_active_date_idx",
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
                name="medschedule_end_after_start",
            ),
        ]
        verbose_name = "복약 일정"
        verbose_name_plural = "복약 일정"

    def clean(self) -> None:
        super().clean()

        if (
            self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValidationError(
                {
                    "end_date": (
                        "복약 종료일은 시작일보다 "
                        "빠를 수 없습니다."
                    )
                }
            )

        if self.prescription_item_id:
            prescription_item = self.prescription_item

            if self.start_date < prescription_item.start_date:
                raise ValidationError(
                    {
                        "start_date": (
                            "복약 일정 시작일은 처방 약품의 "
                            "복용 시작일보다 빠를 수 없습니다."
                        )
                    }
                )

            if prescription_item.end_date is not None:
                if self.end_date is None:
                    raise ValidationError(
                        {
                            "end_date": (
                                "처방 약품에 복용 종료일이 있으면 "
                                "복약 일정에도 종료일이 필요합니다."
                            )
                        }
                    )

                if self.end_date > prescription_item.end_date:
                    raise ValidationError(
                        {
                            "end_date": (
                                "복약 일정 종료일은 처방 약품의 "
                                "복용 종료일을 초과할 수 없습니다."
                            )
                        }
                    )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{self.prescription_item.medicine_name} "
            f"- {self.dose_time}"
        )


class MedicationRecord(TimeStampedModel):
    """환자의 실제 복약 여부와 복약 시각을 기록한다."""

    class Status(models.TextChoices):
        TAKEN = "TAKEN", "복용 완료"
        MISSED = "MISSED", "미복용"
        SKIPPED = "SKIPPED", "복용 건너뜀"

    schedule = models.ForeignKey(
        MedicationSchedule,
        on_delete=models.PROTECT,
        related_name="medication_records",
        verbose_name="복약 일정",
    )
    prescription_item = models.ForeignKey(
        "prescriptions.PrescriptionItem",
        on_delete=models.PROTECT,
        related_name="medication_records",
        verbose_name="처방 약품",
    )
    scheduled_at = models.DateTimeField(
        db_index=True,
        verbose_name="복용 예정 일시",
    )
    taken_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="실제 복용 일시",
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        db_index=True,
        verbose_name="복약 상태",
    )
    note = models.TextField(
        blank=True,
        verbose_name="복약 메모",
    )

    class Meta:
        ordering = [
            "-scheduled_at",
            "-created_at",
        ]
        indexes = [
            models.Index(
                fields=["schedule", "scheduled_at"],
                name="medrecord_schedule_time_idx",
            ),
            models.Index(
                fields=["prescription_item", "scheduled_at"],
                name="medrecord_item_time_idx",
            ),
            models.Index(
                fields=["status", "scheduled_at"],
                name="medrecord_status_time_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["schedule", "scheduled_at"],
                name="medrecord_schedule_at_uniq",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        status="TAKEN",
                        taken_at__isnull=False,
                    )
                    | (
                        ~models.Q(status="TAKEN")
                        & models.Q(taken_at__isnull=True)
                    )
                ),
                name="medrecord_taken_at_valid",
            ),
        ]
        verbose_name = "복약 기록"
        verbose_name_plural = "복약 기록"

    def clean(self) -> None:
        super().clean()

        if (
            self.schedule_id
            and self.prescription_item_id
            and self.schedule.prescription_item_id
            != self.prescription_item_id
        ):
            raise ValidationError(
                {
                    "prescription_item": (
                        "복약 기록의 처방 약품은 "
                        "복약 일정의 처방 약품과 일치해야 합니다."
                    )
                }
            )

        if self.status == self.Status.TAKEN:
            if self.taken_at is None:
                raise ValidationError(
                    {
                        "taken_at": (
                            "복용 완료 상태에는 "
                            "실제 복용 일시가 필요합니다."
                        )
                    }
                )
        elif self.taken_at is not None:
            raise ValidationError(
                {
                    "taken_at": (
                        "미복용 또는 건너뜀 상태에는 "
                        "실제 복용 일시를 입력할 수 없습니다."
                    )
                }
            )

        if self.schedule_id and self.scheduled_at:
            if timezone.is_aware(self.scheduled_at):
                scheduled_date = timezone.localtime(
                    self.scheduled_at
                ).date()
            else:
                scheduled_date = self.scheduled_at.date()

            if scheduled_date < self.schedule.start_date:
                raise ValidationError(
                    {
                        "scheduled_at": (
                            "복용 예정 일시는 복약 일정의 "
                            "시작일보다 빠를 수 없습니다."
                        )
                    }
                )

            if (
                self.schedule.end_date is not None
                and scheduled_date > self.schedule.end_date
            ):
                raise ValidationError(
                    {
                        "scheduled_at": (
                            "복용 예정 일시는 복약 일정의 "
                            "종료일을 초과할 수 없습니다."
                        )
                    }
                )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{self.prescription_item.medicine_name} "
            f"- {self.scheduled_at} - {self.status}"
        )