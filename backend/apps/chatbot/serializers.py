from rest_framework import serializers

from .models import ChatConversation, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    message_id = serializers.UUIDField(source="id", read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            "message_id",
            "role",
            "sequence",
            "content",
            "created_at",
        ]


class ChatConversationSerializer(serializers.ModelSerializer):
    conversation_id = serializers.UUIDField(source="id", read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatConversation
        fields = [
            "conversation_id",
            "title",
            "status",
            "messages",
            "created_at",
            "updated_at",
        ]


class ChatAssistantRequestSerializer(serializers.Serializer):
    message = serializers.CharField(
        min_length=1,
        max_length=2000,
        trim_whitespace=True,
    )
    conversation_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    idempotency_key = serializers.CharField(
        required=False,
        allow_blank=False,
        max_length=80,
    )
