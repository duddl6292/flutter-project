from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .ai_client import AIServiceError, request_assistant_reply
from .models import ChatConversation, ChatMessage
from .serializers import (
    ChatAssistantRequestSerializer,
    ChatConversationSerializer,
    ChatMessageSerializer,
)
from .services import ChatMessageIdempotencyConflict, append_chat_message


class ChatbotServiceUnavailable(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "AI 답변을 생성하지 못했습니다. 잠시 후 다시 시도해 주세요."
    default_code = "chatbot_service_unavailable"


def _active_conversations(request):
    return ChatConversation.objects.filter(
        user=request.user,
        status=ChatConversation.Status.ACTIVE,
    )


def _bearer_token(request) -> str | None:
    authorization = request.headers.get("Authorization", "")
    scheme, separator, token = authorization.partition(" ")
    if separator and scheme.lower() == "bearer" and token.strip():
        return token.strip()
    return None


class LatestChatConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversation = (
            _active_conversations(request)
            .prefetch_related("messages")
            .order_by("-last_message_at", "-created_at")
            .first()
        )
        return Response({
            "data": (
                ChatConversationSerializer(conversation).data
                if conversation
                else None
            ),
        })


class ChatAssistantMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChatAssistantRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        conversation_id = data.get("conversation_id")
        if conversation_id:
            conversation = get_object_or_404(
                _active_conversations(request),
                id=conversation_id,
            )
        else:
            message = data["message"]
            conversation = ChatConversation.objects.create(
                user=request.user,
                title=message[:60],
            )

        idempotency_key = data.get("idempotency_key")
        try:
            user_message, user_created = append_chat_message(
                conversation_id=conversation.id,
                role=ChatMessage.Role.USER,
                content=data["message"],
                idempotency_key=idempotency_key,
            )
        except ChatMessageIdempotencyConflict as exc:
            from rest_framework.exceptions import ValidationError

            raise ValidationError({
                "idempotency_key": str(exc),
            }) from exc

        assistant_key = (
            f"ai:{idempotency_key}"
            if idempotency_key
            else None
        )
        if not user_created and assistant_key:
            existing_assistant = conversation.messages.filter(
                idempotency_key=assistant_key,
                role=ChatMessage.Role.ASSISTANT,
            ).first()
            if existing_assistant:
                return Response({
                    "data": {
                        "conversation_id": str(conversation.id),
                        "user_message": ChatMessageSerializer(user_message).data,
                        "assistant_message": ChatMessageSerializer(
                            existing_assistant
                        ).data,
                    },
                })

        try:
            reply = request_assistant_reply(
                message=data["message"],
                user_access_token=_bearer_token(request),
                user_role=request.user.role,
            )
        except AIServiceError as exc:
            raise ChatbotServiceUnavailable(str(exc)) from exc

        assistant_message, _ = append_chat_message(
            conversation_id=conversation.id,
            role=ChatMessage.Role.ASSISTANT,
            content=reply,
            idempotency_key=assistant_key,
            model_name="vertex-ai",
        )

        return Response(
            {
                "data": {
                    "conversation_id": str(conversation.id),
                    "user_message": ChatMessageSerializer(user_message).data,
                    "assistant_message": ChatMessageSerializer(
                        assistant_message
                    ).data,
                },
            },
            status=status.HTTP_201_CREATED,
        )
