import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """UUID 기본키와 생성·수정 일시를 제공하는 공통 추상 모델."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="UUID",
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
        abstract = True