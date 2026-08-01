from __future__ import annotations

import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Patient(models.Model):
    """
    신원이 확인된 정식 환자.

    로그인 계정은 accounts.User에 저장하고,
    환자 상세 정보는 이 모델에 저장합니다.
    """

    class Sex(models.TextChoices):
        MALE = "M", "남성"
        FEMALE = "F", "여성"
        UNKNOWN = "UNKNOWN", "미상"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "활성"
        INACTIVE = "INACTIVE", "비활성"
        MERGED = "MERGED", "다른 환자에 통합됨"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="환자 UUID",
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_profile",
        verbose_name="사용자 계정",
        help_text="환자 앱 로그인 계정과 연결합니다.",
    )

    medical_record_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name="병원 환자번호",
        help_text="병원에서 부여하는 환자번호입니다.",
    )

    name = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="환자 이름",
    )

    birth_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="생년월일",
    )

    sex = models.CharField(
        max_length=10,
        choices=Sex.choices,
        default=Sex.UNKNOWN,
        db_index=True,
        verbose_name="성별",
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
        db_index=True,
        verbose_name="전화번호",
    )

    emergency_contact = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="비상 연락처",
    )

    address = models.TextField(
        blank=True,
        verbose_name="주소",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        verbose_name="환자 상태",
    )

    merged_into = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="merged_patients",
        verbose_name="통합 대상 환자",
        help_text="중복 등록된 환자를 실제 환자에게 통합할 때 사용합니다.",
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
        db_table = "patients"
        ordering = ["name", "-created_at"]
        verbose_name = "환자"
        verbose_name_plural = "환자"
        indexes = [
            models.Index(
                fields=["name", "birth_date"],
                name="patient_name_birth_idx",
            ),
            models.Index(
                fields=["status", "name"],
                name="patient_status_name_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        status="MERGED",
                        merged_into__isnull=False,
                    )
                    | models.Q(
                        status__in=["ACTIVE", "INACTIVE"],
                        merged_into__isnull=True,
                    )
                ),
                name="patient_merged_target_valid",
            ),
        ]

    def __str__(self) -> str:
        if self.medical_record_number:
            return f"{self.name} ({self.medical_record_number})"

        return self.name

    @property
    def canonical_patient(self) -> "Patient":
        """
        중복 환자가 통합된 경우 최종 정식 환자를 반환합니다.
        """

        patient = self
        visited: set[uuid.UUID] = set()

        while (
            patient.status == self.Status.MERGED
            and patient.merged_into_id is not None
        ):
            if patient.id in visited:
                break

            visited.add(patient.id)
            patient = patient.merged_into

        return patient


class ProvisionalIdentity(models.Model):
    """
    신원미상 환자의 임시 신원.

    신원미상 환자를 patients 테이블에 가짜 환자로 생성하지 않고
    이 모델에서 별도로 관리합니다.
    """

    class EstimatedSex(models.TextChoices):
        MALE = "M", "남성 추정"
        FEMALE = "F", "여성 추정"
        UNKNOWN = "UNKNOWN", "미상"

    class Status(models.TextChoices):
        UNIDENTIFIED = "UNIDENTIFIED", "신원미상"
        RESOLVED = "RESOLVED", "신원 확인 완료"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="임시 신원 UUID",
    )

    temporary_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="임시 환자번호",
        help_text="예: TEMP-20260802-001",
    )

    temporary_name = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="임시 표시 이름",
        help_text="예: 신원미상-001",
    )

    estimated_sex = models.CharField(
        max_length=10,
        choices=EstimatedSex.choices,
        default=EstimatedSex.UNKNOWN,
        verbose_name="추정 성별",
    )

    estimated_age = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(150),
        ],
        verbose_name="추정 나이",
    )

    distinguishing_features = models.TextField(
        blank=True,
        verbose_name="식별 특징",
        help_text="의복, 외형, 소지품 등의 식별 정보를 기록합니다.",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UNIDENTIFIED,
        db_index=True,
        verbose_name="신원 확인 상태",
    )

    resolved_patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="resolved_provisional_identities",
        verbose_name="확인된 정식 환자",
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="신원 확인 일시",
    )

    resolved_by = models.ForeignKey(
        "clinicians.Clinician",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_provisional_identities",
        verbose_name="신원 확인 의료진",
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
        db_table = "provisional_identities"
        ordering = ["-created_at"]
        verbose_name = "신원미상 임시 신원"
        verbose_name_plural = "신원미상 임시 신원"
        indexes = [
            models.Index(
                fields=["status", "created_at"],
                name="provisional_status_created_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        status="UNIDENTIFIED",
                        resolved_patient__isnull=True,
                        resolved_at__isnull=True,
                    )
                    | models.Q(
                        status="RESOLVED",
                        resolved_patient__isnull=False,
                        resolved_at__isnull=False,
                    )
                ),
                name="provisional_resolution_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.temporary_name} ({self.temporary_number})"