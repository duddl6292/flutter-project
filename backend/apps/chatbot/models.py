from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedModel


class ChatConversation(TimeStampedModel):
    """사용자와 AI 챗봇 사이의 대화방."""

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "진행 중"
        ARCHIVED = "ARCHIVED", "보관"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="chat_conversations",
        verbose_name="사용자",
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="대화 제목",
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        verbose_name="상태",
    )
    last_message_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="마지막 메시지 일시",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="추가 정보",
        help_text="모델 설정이나 대화 컨텍스트 식별자를 저장합니다.",
    )

    class Meta:
        ordering = ["-last_message_at", "-created_at"]
        indexes = [
            models.Index(
                fields=["user", "status", "updated_at"],
                name="chat_conv_user_status_idx",
            ),
        ]
        verbose_name = "챗봇 대화"
        verbose_name_plural = "챗봇 대화"

    def __str__(self) -> str:
        return self.title or f"Conversation {self.id}"


class ChatMessage(TimeStampedModel):
    """사용자·AI·도구가 대화방에서 주고받은 메시지."""

    class Role(models.TextChoices):
        USER = "USER", "사용자"
        ASSISTANT = "ASSISTANT", "AI"
        SYSTEM = "SYSTEM", "시스템"
        TOOL = "TOOL", "도구"

    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="대화",
    )
    role = models.CharField(
        max_length=16,
        choices=Role.choices,
        db_index=True,
        verbose_name="발신 역할",
    )
    sequence = models.PositiveIntegerField(
        verbose_name="메시지 순서",
    )
    idempotency_key = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="중복 방지 키",
        help_text="클라이언트 또는 Genkit 요청의 고유 키를 저장합니다.",
    )
    content = models.TextField(
        blank=True,
        verbose_name="메시지 내용",
    )
    model_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="AI 모델명",
    )
    tool_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="도구명",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="추가 정보",
        help_text="도구 호출 인자, 결과 요약, 토큰 사용량 등을 저장합니다.",
    )

    class Meta:
        ordering = ["sequence"]
        indexes = [
            models.Index(
                fields=["conversation", "sequence"],
                name="chat_msg_conv_seq_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["conversation", "sequence"],
                name="chat_msg_conv_seq_unique",
            ),
            models.UniqueConstraint(
                fields=["conversation", "idempotency_key"],
                condition=(
                    models.Q(idempotency_key__isnull=False)
                    & ~models.Q(idempotency_key="")
                ),
                name="chat_msg_idempotency_unique",
            ),
            models.CheckConstraint(
                condition=models.Q(sequence__gte=1),
                name="chat_msg_sequence_positive",
            ),
            models.CheckConstraint(
                condition=(
                    ~models.Q(role="USER")
                    | ~models.Q(content="")
                ),
                name="chat_user_content_required",
            ),
            models.CheckConstraint(
                condition=(
                    ~models.Q(role="TOOL")
                    | ~models.Q(tool_name="")
                ),
                name="chat_tool_name_required",
            ),
        ]
        verbose_name = "챗봇 메시지"
        verbose_name_plural = "챗봇 메시지"

    def clean(self) -> None:
        super().clean()

        if self.idempotency_key == "":
            self.idempotency_key = None

        if self.role == self.Role.USER and not self.content.strip():
            raise ValidationError({
                "content": "사용자 메시지 내용은 비워둘 수 없습니다.",
            })

        if self.role == self.Role.TOOL and not self.tool_name.strip():
            raise ValidationError({
                "tool_name": "도구 메시지에는 도구명이 필요합니다.",
            })

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{self.conversation_id} - "
            f"#{self.sequence} {self.role}"
        )
