from __future__ import annotations

import uuid

from django.db import models


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
        ]

    def __str__(self) -> str:
        return self.name