from django.contrib import admin

from .models import ChatConversation, ChatMessage


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "title",
        "status",
        "last_message_at",
    )
    list_filter = ("status",)
    search_fields = ("user__username", "title")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "conversation",
        "sequence",
        "role",
        "model_name",
        "tool_name",
        "created_at",
    )
    list_filter = ("role",)
    search_fields = (
        "conversation__user__username",
        "content",
        "tool_name",
    )
