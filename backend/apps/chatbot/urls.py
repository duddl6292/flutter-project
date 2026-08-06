from django.urls import path

from .views import ChatAssistantMessageView, LatestChatConversationView


app_name = "chatbot"


urlpatterns = [
    path(
        "conversations/latest/",
        LatestChatConversationView.as_view(),
        name="latest-conversation",
    ),
    path(
        "messages/",
        ChatAssistantMessageView.as_view(),
        name="assistant-message",
    ),
]
