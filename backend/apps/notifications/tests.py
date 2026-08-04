from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User

from .models import Device


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
