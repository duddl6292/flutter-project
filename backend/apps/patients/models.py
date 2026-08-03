from __future__ import annotations

import uuid

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


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


class PatientAccountClaim(TimeStampedModel):
    """
    기존 병원 환자와 모바일 사용자 계정을 연결하기 위한
    일회용 환자 계정 연결 요청.

    사용 흐름:
    1. 병원에서 기존 Patient를 확인한다.
    2. 의료진 또는 관리자가 연결 코드를 발급한다.
    3. 환자가 모바일에서 환자번호와 연결 코드를 입력한다.
    4. 새 User를 생성한다.
    5. 기존 Patient.user에 새 User를 연결한다.
    6. 이 요청을 USED 상태로 변경한다.
    """

    class Status(models.TextChoices):
        ISSUED = "ISSUED", "발급됨"
        USED = "USED", "사용 완료"
        EXPIRED = "EXPIRED", "만료됨"
        REVOKED = "REVOKED", "취소됨"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name="account_claims",
        verbose_name="연결 대상 환자",
    )

    claim_code_hash = models.CharField(
        max_length=128,
        unique=True,
        verbose_name="연결 코드 해시",
        help_text=(
            "일회용 연결 코드를 평문으로 저장하지 않고 "
            "Django 비밀번호 해시 형식으로 저장합니다."
        ),
    )

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ISSUED,
        db_index=True,
        verbose_name="연결 요청 상태",
    )

    expires_at = models.DateTimeField(
        db_index=True,
        verbose_name="만료 일시",
    )

    used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="사용 완료 일시",
    )

    failed_attempts = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="인증 실패 횟수",
    )

    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="issued_patient_account_claims",
        verbose_name="발급 사용자",
        help_text="연결 코드를 발급한 관리자 또는 의료진 계정입니다.",
    )

    claimed_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="patient_account_claim",
        verbose_name="연결된 모바일 사용자",
    )

    class Meta:
        db_table = "patient_account_claims"
        ordering = ["-created_at"]
        verbose_name = "환자 계정 연결 요청"
        verbose_name_plural = "환자 계정 연결 요청"

        indexes = [
            models.Index(
                fields=[
                    "patient",
                    "status",
                    "expires_at",
                ],
                name="ptclaim_patient_status_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "expires_at",
                ],
                name="ptclaim_status_expire_idx",
            ),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["patient"],
                condition=models.Q(status="ISSUED"),
                name="ptclaim_one_issued_uniq",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        status="ISSUED",
                        used_at__isnull=True,
                        claimed_user__isnull=True,
                    )
                    | models.Q(
                        status="USED",
                        used_at__isnull=False,
                        claimed_user__isnull=False,
                    )
                    | models.Q(
                        status__in=[
                            "EXPIRED",
                            "REVOKED",
                        ],
                        used_at__isnull=True,
                        claimed_user__isnull=True,
                    )
                ),
                name="ptclaim_status_valid_chk",
            ),
        ]

    @property
    def is_expired(self) -> bool:
        """
        현재 시각 기준으로 연결 코드가 만료됐는지 반환한다.
        """
        return timezone.now() >= self.expires_at

    @property
    def is_available(self) -> bool:
        """
        현재 사용할 수 있는 연결 요청인지 반환한다.
        """
        return (
            self.status == self.Status.ISSUED
            and not self.is_expired
            and self.patient.user_id is None
        )

    def set_claim_code(self, raw_code: str) -> None:
        """
        6자리 숫자 연결 코드를 해시하여 저장한다.

        평문 연결 코드는 DB에 저장하지 않는다.
        """
        normalized_code = raw_code.strip()

        if (
            len(normalized_code) != 6
            or not normalized_code.isdigit()
        ):
            raise ValidationError({
                "claim_code_hash": (
                    "환자 연결 코드는 숫자 6자리여야 합니다."
                ),
            })

        self.claim_code_hash = make_password(
            normalized_code
        )

    def check_claim_code(self, raw_code: str) -> bool:
        """
        입력한 연결 코드가 일치하는지 확인한다.

        실패할 경우 failed_attempts를 1 증가시킨다.
        """
        if not self.is_available:
            return False

        is_valid = check_password(
            raw_code.strip(),
            self.claim_code_hash,
        )

        if not is_valid:
            self.failed_attempts += 1
            self.save(
                update_fields=[
                    "failed_attempts",
                    "updated_at",
                ]
            )

        return is_valid

    def mark_as_used(self, user) -> None:
        """
        환자 계정 연결 요청을 사용 완료 상태로 변경한다.

        호출 전에 기존 Patient.user에 새 환자 계정을
        연결하고 저장해야 한다.
        """
        if self.status != self.Status.ISSUED:
            raise ValidationError(
                "발급 상태인 환자 계정 연결 요청만 사용할 수 있습니다."
            )

        if self.is_expired:
            raise ValidationError(
                "만료된 환자 계정 연결 요청입니다."
            )

        if getattr(user, "role", None) != "PATIENT":
            raise ValidationError({
                "claimed_user": (
                    "환자 역할 사용자만 기존 환자와 "
                    "연결할 수 있습니다."
                ),
            })

        if self.patient.user_id != user.id:
            raise ValidationError({
                "claimed_user": (
                    "연결된 사용자와 Patient.user가 "
                    "일치해야 합니다."
                ),
            })

        self.status = self.Status.USED
        self.claimed_user = user
        self.used_at = timezone.now()

        self.save(
            update_fields=[
                "status",
                "claimed_user",
                "used_at",
                "updated_at",
            ]
        )

    def mark_as_expired(self) -> None:
        """
        사용되지 않은 만료 요청을 EXPIRED 상태로 변경한다.
        """
        if self.status != self.Status.ISSUED:
            raise ValidationError(
                "발급 상태인 연결 요청만 만료 처리할 수 있습니다."
            )

        if not self.is_expired:
            raise ValidationError(
                "아직 만료 일시가 지나지 않았습니다."
            )

        self.status = self.Status.EXPIRED
        self.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    def revoke(self) -> None:
        """
        의료진 또는 관리자가 발급한 연결 요청을 취소한다.
        """
        if self.status != self.Status.ISSUED:
            raise ValidationError(
                "발급 상태인 연결 요청만 취소할 수 있습니다."
            )

        self.status = self.Status.REVOKED
        self.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    def clean(self) -> None:
        super().clean()

        # 만료 일시는 생성 일시보다 미래여야 함
        if (
            self.status == self.Status.ISSUED
            and self.expires_at <= timezone.now()
        ):
            raise ValidationError({
                "expires_at": (
                    "발급 상태의 연결 요청은 "
                    "미래의 만료 일시가 필요합니다."
                ),
            })

        # 이미 계정이 연결된 환자에게 새 연결 요청 발급 금지
        if (
            self.status == self.Status.ISSUED
            and self.patient_id
            and self.patient.user_id is not None
        ):
            raise ValidationError({
                "patient": (
                    "이미 모바일 계정이 연결된 환자입니다."
                ),
            })

        if self.status == self.Status.USED:
            if self.used_at is None:
                raise ValidationError({
                    "used_at": (
                        "사용 완료 상태에는 사용 완료 일시가 "
                        "필요합니다."
                    ),
                })

            if self.claimed_user_id is None:
                raise ValidationError({
                    "claimed_user": (
                        "사용 완료 상태에는 연결된 사용자가 "
                        "필요합니다."
                    ),
                })

            if (
                self.patient_id
                and self.patient.user_id
                != self.claimed_user_id
            ):
                raise ValidationError({
                    "claimed_user": (
                        "Patient.user와 연결 완료 사용자가 "
                        "일치해야 합니다."
                    ),
                })

        elif self.used_at is not None:
            raise ValidationError({
                "used_at": (
                    "사용 완료 상태가 아니면 사용 완료 일시를 "
                    "입력할 수 없습니다."
                ),
            })

        if (
            self.status != self.Status.USED
            and self.claimed_user_id is not None
        ):
            raise ValidationError({
                "claimed_user": (
                    "사용 완료 상태가 아니면 연결 사용자를 "
                    "지정할 수 없습니다."
                ),
            })

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{self.patient.name} "
            f"({self.patient.medical_record_number or self.patient.id}) "
            f"- {self.status}"
        )


class PatientIdentityResolutionLog(TimeStampedModel):
    """
    신원미상 환자의 신원이 확인되어 정식 Patient로
    연결된 처리 이력을 보관한다.

    ProvisionalIdentity는 처리 완료 후 삭제되므로
    FK 대신 원본 UUID와 주요 정보를 복사해 보관한다.
    """

    class ResolutionType(models.TextChoices):
        EXISTING_PATIENT = (
            "EXISTING",
            "기존 환자 차트 병합",
        )
        NEW_PATIENT = (
            "NEW",
            "신규 환자 차트 생성",
        )

    provisional_identity_uuid = models.UUIDField(
        unique=True,
        verbose_name="삭제된 임시 신원 UUID",
    )

    temporary_number = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name="임시 환자번호",
    )

    temporary_name = models.CharField(
        max_length=100,
        verbose_name="임시 표시 이름",
    )

    estimated_sex = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="추정 성별 스냅샷",
    )

    estimated_age = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="추정 나이 스냅샷",
    )

    distinguishing_features = models.TextField(
        blank=True,
        verbose_name="식별 특징 스냅샷",
    )

    resolution_type = models.CharField(
        max_length=16,
        choices=ResolutionType.choices,
        db_index=True,
        verbose_name="신원확인 처리 유형",
    )

    target_patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name="identity_resolution_logs",
        verbose_name="연결된 정식 환자",
    )

    resolved_by = models.ForeignKey(
        "clinicians.Clinician",
        on_delete=models.PROTECT,
        related_name="identity_resolution_logs",
        verbose_name="신원확인 처리 의료진",
    )

    resolved_at = models.DateTimeField(
        db_index=True,
        verbose_name="신원확인 처리 일시",
    )

    moved_encounter_ids = models.JSONField(
        default=list,
        blank=True,
        verbose_name="이관된 진료 UUID 목록",
    )

    moved_encounter_count = models.PositiveIntegerField(
        default=0,
        verbose_name="이관된 진료 건수",
    )

    deletion_snapshot = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="삭제 시점 원본 스냅샷",
        help_text=(
            "PostgreSQL Trigger가 ProvisionalIdentity "
            "삭제 직전에 기록합니다."
        ),
    )

    provisional_deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="임시 신원 삭제 일시",
    )

    note = models.TextField(
        blank=True,
        verbose_name="처리 메모",
    )

    class Meta:
        db_table = "patient_identity_resolution_logs"
        ordering = ["-resolved_at", "-created_at"]
        verbose_name = "환자 신원확인 처리 로그"
        verbose_name_plural = "환자 신원확인 처리 로그"

        indexes = [
            models.Index(
                fields=[
                    "target_patient",
                    "resolved_at",
                ],
                name="ptidres_patient_date_idx",
            ),
            models.Index(
                fields=[
                    "resolution_type",
                    "resolved_at",
                ],
                name="ptidres_type_date_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.temporary_number} → "
            f"{self.target_patient} "
            f"({self.resolution_type})"
        )