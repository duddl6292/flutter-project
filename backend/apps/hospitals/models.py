from __future__ import annotations

import uuid
from decimal import Decimal

from django.core.validators import (MaxValueValidator, MinValueValidator, )
from django.db import models

from apps.core.models import TimeStampedModel

class Hospital(models.Model):
    """의료진이 소속될 병원 정보."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="병원 UUID",
    )

    hospital_code = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        verbose_name="병원 코드",
        help_text="공공데이터 또는 BrainOn 내부 병원 코드",
    )

    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name="병원명",
    )

    address = models.TextField(
        blank=True,
        verbose_name="병원 주소",
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="병원 전화번호",
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("-90")),
            MaxValueValidator(Decimal("90")),
        ],
        verbose_name="위도",
        help_text=(
            "WGS84(EPSG:4326) 기준 위도입니다."
        ),
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("-180")),
            MaxValueValidator(Decimal("180")),
        ],
        verbose_name="경도",
        help_text=(
            "WGS84(EPSG:4326) 기준 경도입니다."
        ),
    )

    external_provider = models.CharField(
        max_length=100,
        blank=True,
        default="",
        db_index=True,
        verbose_name="외부 데이터 제공자",
        help_text=(
            "예: HIRA, KAKAO_LOCAL, NAVER_LOCAL"
        ),
    )

    external_place_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="외부 병원 식별자",
        help_text=(
            "외부 API에서 부여한 병원 또는 장소 ID입니다."
        ),
    )

    external_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="외부 데이터 동기화 일시",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="사용 여부",
        help_text="비활성 병원은 검색과 신규 의료진 가입에서 제외됩니다.",
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
        db_table = "hospitals"
        ordering = ["name"]
        verbose_name = "병원"
        verbose_name_plural = "병원"

        indexes = [
            models.Index(
                fields=["is_active", "name"],
                name="hospital_active_name_idx",
            ),
            models.Index(
                fields=["latitude", "longitude"],
                name="hospital_coordinates_idx",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        latitude__isnull=True,
                        longitude__isnull=True,
                    )
                    | models.Q(
                        latitude__isnull=False,
                        longitude__isnull=False,
                    )
                ),
                name="hospital_coordinates_pair_valid",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(latitude__isnull=True)
                    | (
                        models.Q(
                            latitude__gte=Decimal("-90")
                        )
                        & models.Q(
                            latitude__lte=Decimal("90")
                        )
                    )
                ),
                name="hospital_latitude_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(longitude__isnull=True)
                    | (
                        models.Q(
                            longitude__gte=Decimal("-180")
                        )
                        & models.Q(
                            longitude__lte=Decimal("180")
                        )
                    )
                ),
                name="hospital_longitude_range",
            ),
            models.UniqueConstraint(
                fields=[
                    "external_provider",
                    "external_place_id",
                ],
                condition=(
                    ~models.Q(external_provider="")
                    & ~models.Q(external_place_id="")
                ),
                name="hospital_external_ref_uniq",
            ),
        ]


class PatientFavoriteHospital(TimeStampedModel):
    """환자가 찜한 병원 관계를 관리한다."""

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="favorite_hospital_links",
        verbose_name="환자",
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name="favorited_patient_links",
        verbose_name="찜한 병원",
    )

    class Meta:
        db_table = "patient_favorite_hospitals"
        ordering = ["-created_at"]
        verbose_name = "환자 찜 병원"
        verbose_name_plural = "환자 찜 병원"
        constraints = [
            models.UniqueConstraint(
                fields=["patient", "hospital"],
                name="patient_favorite_hospital_uniq",
            ),
        ]
        indexes = [
            models.Index(
                fields=["patient", "created_at"],
                name="favhospital_patient_date_idx",
            ),
            models.Index(
                fields=["hospital", "created_at"],
                name="favhospital_hospital_date_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.patient.name} - "
            f"{self.hospital.name}"
        )
