from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TransactionTestCase, override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User

from .models import (
    Device,
    Notification,
    NotificationDelivery,
    NotificationPreference,
)
from .services import _push_data


class DeviceRegistrationApiTests(APITestCase):
    register_url = (
        "/api/v1/notifications/devices/register/"
    )
    unregister_url = (
        "/api/v1/notifications/devices/unregister/"
    )

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="device-clinician",
            password="test-password",
            role=User.Role.CLINICIAN,
        )
        self.client.force_authenticate(
            user=self.user,
        )

    def registration_data(
        self,
        *,
        token: str = "web-fcm-token-1",
    ) -> dict[str, str]:
        return {
            "platform": Device.Platform.WEB,
            "client_type": (
                Device.ClientType.CLINICIAN_WEB
            ),
            "device_identifier": (
                "browser-installation-1"
            ),
            "fcm_token": token,
            "device_name": "Chrome on Windows",
            "app_version": "0.1.0",
        }

    def test_registers_web_device(self) -> None:
        response = self.client.post(
            self.register_url,
            self.registration_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        device = Device.objects.get(
            user=self.user,
        )

        self.assertEqual(
            device.client_type,
            Device.ClientType.CLINICIAN_WEB,
        )
        self.assertEqual(
            device.fcm_token,
            "web-fcm-token-1",
        )
        self.assertTrue(device.is_active)
        self.assertNotIn(
            "fcm_token",
            response.data["data"],
        )

    def test_same_installation_updates_rotated_token(
        self,
    ) -> None:
        self.client.post(
            self.register_url,
            self.registration_data(),
            format="json",
        )

        response = self.client.post(
            self.register_url,
            self.registration_data(
                token="web-fcm-token-2",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            Device.objects.count(),
            1,
        )
        self.assertEqual(
            Device.objects.get().fcm_token,
            "web-fcm-token-2",
        )

    def test_rejects_app_client_on_web_platform(
        self,
    ) -> None:
        data = self.registration_data()
        data["client_type"] = (
            Device.ClientType.CLINICIAN_APP
        )

        response = self.client.post(
            self.register_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(
            Device.objects.exists(),
        )

    def test_patient_cannot_register_clinician_client(
        self,
    ) -> None:
        patient = User.objects.create_user(
            username="device-patient",
            password="test-password",
            role=User.Role.PATIENT,
        )
        self.client.force_authenticate(
            user=patient,
        )

        response = self.client.post(
            self.register_url,
            self.registration_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_patient_can_register_patient_android_app(
        self,
    ) -> None:
        patient = User.objects.create_user(
            username="device-patient-app",
            password="test-password",
            role=User.Role.PATIENT,
        )
        self.client.force_authenticate(
            user=patient,
        )

        response = self.client.post(
            self.register_url,
            {
                "platform": Device.Platform.ANDROID,
                "client_type": (
                    Device.ClientType.PATIENT_APP
                ),
                "device_identifier": (
                    "patient-app-installation-1"
                ),
                "fcm_token": "patient-fcm-token-1",
                "device_name": "Pixel Test Device",
                "app_version": "1.0.0",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(
            Device.objects.filter(
                user=patient,
                client_type=(
                    Device.ClientType.PATIENT_APP
                ),
                platform=Device.Platform.ANDROID,
                is_active=True,
            ).exists(),
        )

    def test_unregister_deactivates_current_device(
        self,
    ) -> None:
        self.client.post(
            self.register_url,
            self.registration_data(),
            format="json",
        )

        response = self.client.post(
            self.unregister_url,
            {
                "client_type": (
                    Device.ClientType.CLINICIAN_WEB
                ),
                "device_identifier": (
                    "browser-installation-1"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["data"]["updated_count"],
            1,
        )

        device = Device.objects.get(
            user=self.user,
        )
        self.assertFalse(device.is_active)


@override_settings(FCM_ENABLED=True)
class AutomaticWebPushTests(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="push-clinician",
            password="test-password",
            role=User.Role.CLINICIAN,
        )
        self.device = Device.objects.create(
            user=self.user,
            platform=Device.Platform.WEB,
            client_type=Device.ClientType.CLINICIAN_WEB,
            device_identifier="push-browser-1",
            fcm_token="push-fcm-token-1",
        )

    def create_notification(self) -> Notification:
        with self.captureOnCommitCallbacks(execute=True):
            return Notification.objects.create(
                recipient=self.user,
                type=Notification.Type.TEST_RESULT,
                title="환자 검사 결과가 등록되었습니다.",
                body="민감한 환자 상세 내용",
                data={
                    "path": "/examinations/result-1",
                    "event": "REGISTERED",
                },
            )

    @patch(
        "apps.notifications.services.send_web_push",
        return_value="projects/test/messages/message-1",
    )
    def test_new_notification_is_sent_to_web_device(
        self,
        send_web_push_mock,
    ) -> None:
        notification = self.create_notification()

        delivery = NotificationDelivery.objects.get(
            notification=notification,
            device=self.device,
        )
        self.assertEqual(
            delivery.status,
            NotificationDelivery.Status.SENT,
        )
        self.assertEqual(delivery.attempt_count, 1)

        push_data = send_web_push_mock.call_args.kwargs[
            "data"
        ]
        self.assertEqual(
            push_data["path"],
            "/examinations/result-1",
        )
        self.assertNotIn("민감한", push_data["body"])
        self.assertNotIn("환자", push_data["title"])
        self.assertEqual(push_data["title"], "검사 결과 알림")
        self.assertEqual(
            push_data["body"],
            "새 검사 결과가 등록되었습니다.",
        )

    def test_consultation_message_push_hides_message_content(self) -> None:
        notification = Notification(
            recipient=self.user,
            type=Notification.Type.CONSULTATION,
            title="새 협진 메시지",
            body="강지훈: 민감한 협진 메시지 내용",
            data={
                "path": "/consultations/test",
                "event": "MESSAGE",
                "actor_name": "강지훈",
            },
        )

        push_data = _push_data(notification)

        self.assertEqual(push_data["title"], "협진 알림")
        self.assertEqual(
            push_data["body"],
            "강지훈 의료진이 메시지를 보냈습니다.",
        )
        self.assertNotIn("민감한", push_data["body"])

    @patch("apps.notifications.services.send_web_push")
    def test_disabled_push_preference_is_suppressed(
        self,
        send_web_push_mock,
    ) -> None:
        NotificationPreference.objects.create(
            user=self.user,
            notification_type=Notification.Type.TEST_RESULT,
            push_enabled=False,
        )

        notification = self.create_notification()

        delivery = NotificationDelivery.objects.get(
            notification=notification,
            device=self.device,
        )
        self.assertEqual(
            delivery.status,
            NotificationDelivery.Status.SUPPRESSED,
        )
        send_web_push_mock.assert_not_called()

    @patch("apps.notifications.services.send_web_push")
    def test_invalid_fcm_token_deactivates_device(
        self,
        send_web_push_mock,
    ) -> None:
        UnregisteredError = type(
            "UnregisteredError",
            (Exception,),
            {},
        )
        send_web_push_mock.side_effect = (
            UnregisteredError("expired token")
        )

        notification = self.create_notification()

        self.device.refresh_from_db()
        self.assertFalse(self.device.is_active)
        self.assertEqual(
            NotificationDelivery.objects.get(
                notification=notification,
            ).status,
            NotificationDelivery.Status.FAILED,
        )

    @patch("apps.notifications.services.send_web_push")
    def test_malformed_registration_token_deactivates_device(
        self,
        send_web_push_mock,
    ) -> None:
        InvalidArgumentError = type(
            "InvalidArgumentError",
            (Exception,),
            {},
        )
        send_web_push_mock.side_effect = InvalidArgumentError(
            "The registration token is not a valid FCM registration token"
        )

        self.create_notification()

        self.device.refresh_from_db()
        self.assertFalse(self.device.is_active)


@override_settings(FCM_ENABLED=True)
class SendTestNotificationCommandTests(TransactionTestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="command-clinician",
            password="test-password",
            role=User.Role.CLINICIAN,
        )
        Device.objects.create(
            user=self.user,
            platform=Device.Platform.WEB,
            client_type=Device.ClientType.CLINICIAN_WEB,
            device_identifier="command-browser-1",
            fcm_token="command-fcm-token-1",
        )

    @patch(
        "apps.notifications.services.send_web_push",
        return_value="projects/test/messages/test-command-message",
    )
    def test_sends_notification_to_registered_web_device(
        self,
        send_web_push_mock,
    ) -> None:
        output = StringIO()

        call_command(
            "send_test_notification",
            username=self.user.username,
            type=Notification.Type.CONSULTATION,
            stdout=output,
        )

        self.assertIn("1/1", output.getvalue())
        notification = Notification.objects.get(
            recipient=self.user,
        )
        self.assertEqual(
            notification.type,
            Notification.Type.CONSULTATION,
        )
        self.assertEqual(
            notification.data["path"],
            "/consultations",
        )
        send_web_push_mock.assert_called_once()
