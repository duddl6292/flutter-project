from __future__ import annotations

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel

class Department(models.Model):
    """신경외과·영상의학과·재활의학과 등의 진료과."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="진료과 UUID",
    )

    code = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        verbose_name="진료과 코드",
    )

    name = models.CharField(
        max_length=100,
        verbose_name="진료과명",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="사용 여부",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성 일시",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정 일시",
    )

    class Meta:
        db_table = "departments"
        ordering = ["name"]
        verbose_name = "진료과"
        verbose_name_plural = "진료과"

    def __str__(self) -> str:
        return self.name


class Clinician(models.Model):
    """의료진 프로필."""

    class ApprovalStatus(models.TextChoices):
        PENDING = "PENDING", "승인 대기"
        APPROVED = "APPROVED", "승인 완료"
        REJECTED = "REJECTED", "승인 거절"
        SUSPENDED = "SUSPENDED", "이용 정지"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="의료진 UUID",
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="clinician",
        verbose_name="사용자 계정",
    )

    name = models.CharField(
        max_length=100,
        verbose_name="의료진 이름",
    )

    license_number = models.CharField(
        max_length=6,
        unique=True,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r"^\d{6}$",
                message="면허번호는 숫자 6자리여야 합니다.",
                code="invalid_license_number",
            ),
        ],
        verbose_name="면허번호",
    )

    hospital = models.ForeignKey(
        "hospitals.Hospital",
        on_delete=models.PROTECT,
        related_name="clinicians",
        verbose_name="소속 병원",
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="clinicians",
        verbose_name="진료과",
    )

    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
        db_index=True,
        verbose_name="승인 상태",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="승인 일시",
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_clinicians",
        verbose_name="승인 관리자",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="가입 일시",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정 일시",
    )

    def clean(self):
        super().clean()

        if (
            self.user_id
            and getattr(self.user, "role", None) != "CLINICIAN"
        ):
            raise ValidationError({
                "user": (
                    "CLINICIAN 역할 사용자만 "
                    "의료진으로 등록할 수 있습니다."
                ),
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        db_table = "clinicians"
        ordering = ["name"]
        verbose_name = "의료진"
        verbose_name_plural = "의료진"
        indexes = [
            models.Index(
                fields=["hospital", "department"],
                name="clinician_hospital_dept_idx",
            ),
            models.Index(
                fields=["approval_status"],
                name="clinician_approval_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.name} / "
            f"{self.department.name} / "
            f"{self.hospital.name}"
        )


class ClinicianAvailability(TimeStampedModel):
    """의료진의 요일별 반복 진료 가능 시간을 관리한다."""

    class Weekday(models.IntegerChoices):
        MONDAY = 0, "월요일"
        TUESDAY = 1, "화요일"
        WEDNESDAY = 2, "수요일"
        THURSDAY = 3, "목요일"
        FRIDAY = 4, "금요일"
        SATURDAY = 5, "토요일"
        SUNDAY = 6, "일요일"

    clinician = models.ForeignKey(
        Clinician,
        on_delete=models.CASCADE,
        related_name="availabilities",
        verbose_name="의료진",
    )
    weekday = models.PositiveSmallIntegerField(
        choices=Weekday.choices,
        verbose_name="요일",
    )
    start_time = models.TimeField(
        verbose_name="진료 시작 시간",
    )
    end_time = models.TimeField(
        verbose_name="진료 종료 시간",
    )
    effective_from = models.DateField(
        default=timezone.localdate,
        verbose_name="적용 시작일",
    )
    effective_to = models.DateField(
        null=True,
        blank=True,
        verbose_name="적용 종료일",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="활성 여부",
    )

    class Meta:
        ordering = ["clinician", "weekday", "start_time"]
        indexes = [
            models.Index(
                fields=["clinician", "weekday", "is_active"],
                name="clin_avail_day_idx",
            ),
            models.Index(
                fields=["effective_from", "effective_to"],
                name="clin_avail_period_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(weekday__range=(0, 6)),
                name="clin_avail_weekday_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="clin_avail_end_after_start",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(effective_to__isnull=True)
                    | models.Q(effective_to__gte=models.F("effective_from"))
                ),
                name="clin_avail_period_valid",
            ),
            models.UniqueConstraint(
                fields=[
                    "clinician",
                    "weekday",
                    "start_time",
                    "end_time",
                    "effective_from",
                ],
                name="clin_avail_slot_unique",
            ),
        ]
        verbose_name = "의료진 진료 가능 시간"
        verbose_name_plural = "의료진 진료 가능 시간"

    def clean(self) -> None:
        super().clean()

        if self.start_time >= self.end_time:
            raise ValidationError({
                "end_time": "종료 시간은 시작 시간보다 늦어야 합니다.",
            })

        if (
            self.effective_to is not None
            and self.effective_to < self.effective_from
        ):
            raise ValidationError({
                "effective_to": "적용 종료일은 시작일보다 빠를 수 없습니다.",
            })

        if self.is_active and self.clinician_id:
            overlapping = type(self).objects.filter(
                clinician_id=self.clinician_id,
                weekday=self.weekday,
                is_active=True,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            ).exclude(pk=self.pk)

            overlapping = overlapping.filter(
                models.Q(effective_to__isnull=True)
                | models.Q(effective_to__gte=self.effective_from)
            )

            if self.effective_to is not None:
                overlapping = overlapping.filter(
                    effective_from__lte=self.effective_to,
                )

            if overlapping.exists():
                raise ValidationError({
                    "__all__": (
                        "같은 의료진의 적용 기간과 "
                        "진료 시간이 겹칩니다."
                    ),
                })

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{self.clinician_id} - "
            f"{self.get_weekday_display()} "
            f"{self.start_time}~{self.end_time}"
        )


class ClinicianTimeOff(TimeStampedModel):
    """휴가·학회 등 의료진의 예외적인 진료 불가 시간을 관리한다."""

    clinician = models.ForeignKey(
        Clinician,
        on_delete=models.CASCADE,
        related_name="time_offs",
        verbose_name="의료진",
    )
    start_at = models.DateTimeField(
        db_index=True,
        verbose_name="시작 일시",
    )
    end_at = models.DateTimeField(
        db_index=True,
        verbose_name="종료 일시",
    )
    reason = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="사유",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_clinician_time_offs",
        null=True,
        blank=True,
        verbose_name="등록자",
    )

    class Meta:
        ordering = ["start_at"]
        indexes = [
            models.Index(
                fields=["clinician", "start_at", "end_at"],
                name="clin_time_off_period_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_at__gt=models.F("start_at")),
                name="clin_time_off_end_after_start",
            ),
            models.UniqueConstraint(
                fields=["clinician", "start_at", "end_at"],
                name="clin_time_off_period_unique",
            ),
        ]
        verbose_name = "의료진 진료 불가 시간"
        verbose_name_plural = "의료진 진료 불가 시간"

    def clean(self) -> None:
        super().clean()

        if self.start_at >= self.end_at:
            raise ValidationError({
                "end_at": "종료 일시는 시작 일시보다 늦어야 합니다.",
            })

        if self.clinician_id:
            overlapping = type(self).objects.filter(
                clinician_id=self.clinician_id,
                start_at__lt=self.end_at,
                end_at__gt=self.start_at,
            ).exclude(pk=self.pk)

            if overlapping.exists():
                raise ValidationError({
                    "__all__": (
                        "같은 의료진의 다른 휴진 시간과 겹칩니다."
                    ),
                })

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{self.clinician_id} - "
            f"{self.start_at}~{self.end_at}"
        )
