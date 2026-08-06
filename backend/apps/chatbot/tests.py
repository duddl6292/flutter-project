from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User

from .models import ChatConversation, ChatMessage


class ChatbotApiTests(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="chat-clinician",
            password="test-password",
            role=User.Role.CLINICIAN,
        )
        self.client.force_authenticate(user=self.user)

    def test_latest_conversation_is_null_when_history_is_empty(self) -> None:
        response = self.client.get(
            "/api/v1/chatbot/conversations/latest/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["data"])

    @patch("apps.chatbot.views.request_assistant_reply")
    def test_message_creates_conversation_and_persists_reply(
        self,
        request_reply,
    ) -> None:
        request_reply.return_value = "서울 지역 병원을 확인했습니다."

        response = self.client.post(
            "/api/v1/chatbot/messages/",
            {
                "message": "서울 병원을 알려줘.",
                "idempotency_key": "request-1",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        conversation = ChatConversation.objects.get(user=self.user)
        self.assertEqual(conversation.messages.count(), 2)
        self.assertEqual(
            list(conversation.messages.values_list("role", flat=True)),
            [ChatMessage.Role.USER, ChatMessage.Role.ASSISTANT],
        )

        latest = self.client.get(
            "/api/v1/chatbot/conversations/latest/"
        )
        self.assertEqual(latest.status_code, status.HTTP_200_OK)
        self.assertEqual(len(latest.data["data"]["messages"]), 2)

    @patch("apps.chatbot.views.request_assistant_reply")
    def test_message_forwards_bearer_token_to_ai_service(
        self,
        request_reply,
    ) -> None:
        request_reply.return_value = "General response"
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer synthetic-access-token"
        )

        response = self.client.post(
            "/api/v1/chatbot/messages/",
            {"message": "General medical knowledge question"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        request_reply.assert_called_once_with(
            message="General medical knowledge question",
            user_access_token="synthetic-access-token",
            user_role=User.Role.CLINICIAN,
        )

    @patch("apps.chatbot.views.request_assistant_reply")
    def test_retried_idempotent_message_reuses_existing_reply(
        self,
        request_reply,
    ) -> None:
        request_reply.return_value = "동일한 답변"
        first = self.client.post(
            "/api/v1/chatbot/messages/",
            {
                "message": "상태를 알려줘.",
                "idempotency_key": "same-request",
            },
            format="json",
        )
        conversation_id = first.data["data"]["conversation_id"]

        second = self.client.post(
            "/api/v1/chatbot/messages/",
            {
                "conversation_id": conversation_id,
                "message": "상태를 알려줘.",
                "idempotency_key": "same-request",
            },
            format="json",
        )

        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(
            ChatConversation.objects.get(id=conversation_id).messages.count(),
            2,
        )
        request_reply.assert_called_once()

    def test_user_cannot_append_to_another_users_conversation(self) -> None:
        another_user = User.objects.create_user(
            username="another-clinician",
            password="test-password",
            role=User.Role.CLINICIAN,
        )
        conversation = ChatConversation.objects.create(user=another_user)

        response = self.client.post(
            "/api/v1/chatbot/messages/",
            {
                "conversation_id": str(conversation.id),
                "message": "접근 시도",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patient_role_can_open_own_chatbot_history(self) -> None:
        patient = User.objects.create_user(
            username="chat-patient",
            password="test-password",
            role=User.Role.PATIENT,
        )
        self.client.force_authenticate(user=patient)

        response = self.client.get(
            "/api/v1/chatbot/conversations/latest/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["data"])

    @patch("apps.chatbot.views.request_assistant_reply")
    def test_patient_role_is_forwarded_to_ai_service(self, request_reply) -> None:
        patient = User.objects.create_user(
            username="chat-patient-message",
            password="test-password",
            role=User.Role.PATIENT,
        )
        request_reply.return_value = "Patient-safe response"
        self.client.force_authenticate(user=patient)
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer synthetic-patient-token"
        )

        response = self.client.post(
            "/api/v1/chatbot/messages/",
            {"message": "오늘 복용할 약 알려줘"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        request_reply.assert_called_once_with(
            message="오늘 복용할 약 알려줘",
            user_access_token="synthetic-patient-token",
            user_role=User.Role.PATIENT,
        )
