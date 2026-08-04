from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.clinicians.models import Clinician, Department
from apps.hospitals.models import Hospital


class AccountSettingsApiTests(APITestCase):
    def setUp(self) -> None:
        self.hospital = Hospital.objects.create(
            hospital_code="ACCOUNT-HOSPITAL",
            name="Account Test Hospital",
            is_active=True,
        )
        self.department = Department.objects.create(
            code="ACCOUNT_RADIOLOGY",
            name="Account Radiology",
            is_active=True,
        )
        self.user = User.objects.create_user(
            username="654321",
            password="old-strong-password",
            email="before@example.test",
            role=User.Role.CLINICIAN,
        )
        self.clinician = Clinician.objects.create(
            user=self.user,
            name="Account Clinician",
            license_number="654321",
            hospital=self.hospital,
            department=self.department,
            approval_status=(
                Clinician.ApprovalStatus.APPROVED
            ),
        )
        self.client.force_authenticate(
            user=self.user,
        )

    def test_get_current_account(self) -> None:
        response = self.client.get(
            "/api/v1/auth/me/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["data"]["user"]["email"],
            "before@example.test",
        )
        self.assertEqual(
            response.data["data"]["clinician"][
                "license_number"
            ],
            self.clinician.license_number,
        )
        self.assertNotIn(
            "password",
            response.data["data"]["user"],
        )

    def test_update_current_account_email(self) -> None:
        response = self.client.patch(
            "/api/v1/auth/me/",
            {
                "email": "after@example.test",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.user.refresh_from_db()
        self.assertEqual(
            self.user.email,
            "after@example.test",
        )

    def test_change_password(self) -> None:
        response = self.client.post(
            "/api/v1/auth/password/change/",
            {
                "current_password": (
                    "old-strong-password"
                ),
                "new_password": (
                    "new-strong-password-2026"
                ),
                "new_password_confirm": (
                    "new-strong-password-2026"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.user.refresh_from_db()
        self.assertTrue(
            self.user.check_password(
                "new-strong-password-2026"
            ),
        )

    def test_change_password_rejects_wrong_current_password(
        self,
    ) -> None:
        response = self.client.post(
            "/api/v1/auth/password/change/",
            {
                "current_password": "wrong-password",
                "new_password": (
                    "new-strong-password-2026"
                ),
                "new_password_confirm": (
                    "new-strong-password-2026"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
