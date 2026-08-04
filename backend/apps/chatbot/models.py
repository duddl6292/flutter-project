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


class ChatContextReference(TimeStampedModel):
    """챗봇 답변이 참조한 환자·진료·영상·결과의 명시적 연결."""

    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name="context_references",
    )
    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name="context_references",
        null=True,
        blank=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="chat_context_references",
        null=True,
        blank=True,
    )
    encounter = models.ForeignKey(
        "appointments.Encounter",
        on_delete=models.PROTECT,
        related_name="chat_context_references",
        null=True,
        blank=True,
    )
    imaging_study = models.ForeignKey(
        "imaging.ImagingStudy",
        on_delete=models.PROTECT,
        related_name="chat_context_references",
        null=True,
        blank=True,
    )
    inference_result = models.ForeignKey(
        "ct_analysis.InferenceResult",
        on_delete=models.PROTECT,
        related_name="chat_context_references",
        null=True,
        blank=True,
    )
    test_result = models.ForeignKey(
        "test_results.TestResult",
        on_delete=models.PROTECT,
        related_name="chat_context_references",
        null=True,
        blank=True,
    )
    purpose = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(
                fields=["conversation", "created_at"],
                name="chatctx_conv_date_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(patient__isnull=False)
                    | models.Q(encounter__isnull=False)
                    | models.Q(imaging_study__isnull=False)
                    | models.Q(inference_result__isnull=False)
                    | models.Q(test_result__isnull=False)
                ),
                name="chatctx_reference_required",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.message_id and self.message.conversation_id != self.conversation_id:
            raise ValidationError({"message": "메시지와 컨텍스트의 대화가 일치해야 합니다."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class ChatToolExecution(TimeStampedModel):
    """Genkit/MCP 도구 호출의 입력·결과·오류 감사 기록."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "대기"
        RUNNING = "RUNNING", "실행 중"
        SUCCEEDED = "SUCCEEDED", "성공"
        FAILED = "FAILED", "실패"
        CANCELLED = "CANCELLED", "취소"

    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name="tool_executions",
    )
    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.SET_NULL,
        related_name="tool_executions",
        null=True,
        blank=True,
    )
    tool_name = models.CharField(max_length=150, db_index=True)
    idempotency_key = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    input_arguments = models.JSONField(default=dict, blank=True)
    output_summary = models.JSONField(default=dict, blank=True)
    error_code = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    provider_trace_id = models.CharField(max_length=200, blank=True, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["conversation", "status"],
                name="chattool_conv_status_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["conversation", "idempotency_key"],
                condition=(
                    models.Q(idempotency_key__isnull=False)
                    & ~models.Q(idempotency_key="")
                ),
                name="chattool_conv_idem_uniq",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(started_at__isnull=True)
                    | models.Q(completed_at__isnull=True)
                    | models.Q(completed_at__gte=models.F("started_at"))
                ),
                name="chattool_timestamps_valid",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.message_id and self.message.conversation_id != self.conversation_id:
            raise ValidationError({"message": "도구 실행과 메시지의 대화가 일치해야 합니다."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class ChatFeedback(TimeStampedModel):
    """사용자가 AI 답변에 남긴 평가."""

    class Rating(models.TextChoices):
        HELPFUL = "HELPFUL", "도움 됨"
        NOT_HELPFUL = "NOT_HELPFUL", "도움 안 됨"
        UNSAFE = "UNSAFE", "부적절·위험"

    message = models.OneToOneField(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name="feedback",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="chat_feedback",
    )
    rating = models.CharField(max_length=16, choices=Rating.choices)
    comment = models.TextField(blank=True)


class KnowledgeDocument(TimeStampedModel):
    """RAG에 사용하는 지침·의학 문서의 원본."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "처리 대기"
        INDEXING = "INDEXING", "색인 중"
        READY = "READY", "사용 가능"
        FAILED = "FAILED", "실패"
        ARCHIVED = "ARCHIVED", "보관"

    title = models.CharField(max_length=255)
    stored_object = models.ForeignKey(
        "assets.StoredObject",
        on_delete=models.PROTECT,
        related_name="knowledge_documents",
        null=True,
        blank=True,
    )
    source_uri = models.CharField(max_length=1024, blank=True)
    source_type = models.CharField(max_length=50, blank=True)
    checksum = models.CharField(max_length=64, blank=True, db_index=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_knowledge_documents",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(stored_object__isnull=False)
                    | ~models.Q(source_uri="")
                ),
                name="knowledge_doc_source_req",
            ),
        ]


class KnowledgeChunk(TimeStampedModel):
    """검색을 위해 분할한 지식 문서 텍스트."""

    document = models.ForeignKey(
        KnowledgeDocument,
        on_delete=models.CASCADE,
        related_name="chunks",
    )
    sequence = models.PositiveIntegerField()
    content = models.TextField()
    token_count = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["sequence"]
        constraints = [
            models.UniqueConstraint(
                fields=["document", "sequence"],
                name="knowledge_chunk_seq_uniq",
            ),
        ]


class KnowledgeEmbedding(TimeStampedModel):
    """벡터 확장 도입 전에도 이식 가능한 임베딩 레코드."""

    chunk = models.ForeignKey(
        KnowledgeChunk,
        on_delete=models.CASCADE,
        related_name="embeddings",
    )
    provider = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100)
    dimensions = models.PositiveIntegerField()
    vector = models.JSONField(default=list)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["chunk", "provider", "model_name"],
                name="knowledge_embedding_uniq",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if not isinstance(self.vector, list) or len(self.vector) != self.dimensions:
            raise ValidationError({"vector": "임베딩 차원과 벡터 길이가 일치해야 합니다."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
