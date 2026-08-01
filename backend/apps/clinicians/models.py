from __future__ import annotations

import uuid

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from django.core.exceptions import ValidationError

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