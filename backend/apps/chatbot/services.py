from django.db import transaction
from django.db.models import Max

from .models import ChatConversation, ChatMessage


class ChatMessageIdempotencyConflict(Exception):
    """같은 중복 방지 키가 서로 다른 메시지에 사용됨."""


@transaction.atomic
def append_chat_message(
    *,
    conversation_id,
    role: str,
    content: str = "",
    idempotency_key: str | None = None,
    model_name: str = "",
    tool_name: str = "",
    metadata: dict | None = None,
) -> tuple[ChatMessage, bool]:
    """메시지 순서와 중복 방지를 보장하며 대화방에 메시지를 추가한다."""

    conversation = (
        ChatConversation.objects
        .select_for_update()
        .get(id=conversation_id)
    )

    normalized_key = idempotency_key or None

    if normalized_key:
        existing = ChatMessage.objects.filter(
            conversation=conversation,
            idempotency_key=normalized_key,
        ).first()

        if existing is not None:
            if (
                existing.role != role
                or existing.content != content
                or existing.tool_name != tool_name
            ):
                raise ChatMessageIdempotencyConflict(
                    "같은 중복 방지 키가 다른 메시지에 사용되었습니다."
                )

            return existing, False

    last_sequence = (
        ChatMessage.objects
        .filter(conversation=conversation)
        .aggregate(value=Max("sequence"))["value"]
        or 0
    )

    message = ChatMessage.objects.create(
        conversation=conversation,
        role=role,
        sequence=last_sequence + 1,
        idempotency_key=normalized_key,
        content=content,
        model_name=model_name,
        tool_name=tool_name,
        metadata=metadata or {},
    )

    conversation.last_message_at = message.created_at
    conversation.save(
        update_fields=[
            "last_message_at",
            "updated_at",
        ],
    )

    return message, True
