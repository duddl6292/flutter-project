from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.clinicians.models import Clinician, Department
from apps.hospitals.models import Hospital
from apps.patients.models import Patient


class AuthApiTests(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="patient-user",
            password="strong-test-password",
            role=User.Role.PATIENT,
            email="patient@example.test",
        )
        self.patient = Patient.objects.create(
            user=self.user,
            medical_record_number="TEST-PATIENT-001",
            name="Test Patient",
        )

    def _patient_login(
        self,
        password: str = "strong-test-password",
    ):
        return self.client.post(
            "/api/v1/auth/patient/login/",
            {
                "username": self.user.username,
                "password": password,
            },
            format="json",
        )

    def test_patient_login_and_me(self) -> None:
        response = self._patient_login()

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access", response.data["data"])
        self.assertIn("refresh", response.data["data"])
        self.assertEqual(
            response.data["data"]["user"]["role"],
            User.Role.PATIENT,
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {response.data['data']['access']}"
            )
        )
        me_response = self.client.get(
            "/api/v1/patients/me/"
        )

        self.assertEqual(
            me_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            me_response.data["data"]["patient_id"],
            str(self.patient.id),
        )
        self.assertNotIn(
            "password",
            me_response.data["data"],
        )

    def test_wrong_password_is_rejected(self) -> None:
        response = self._patient_login(
            password="wrong-password",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            response.data["error"]["code"],
            "VALIDATION_ERROR",
        )

    def test_inactive_user_is_rejected(self) -> None:
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self._patient_login()

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_refresh_rotates_and_blacklists_old_token(
        self,
    ) -> None:
        login_response = self._patient_login()
        old_refresh = (
            login_response.data["data"]["refresh"]
        )

        response = self.client.post(
            "/api/v1/auth/token/refresh/",
            {"refresh": old_refresh},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("refresh", response.data["data"])

        second_response = self.client.post(
            "/api/v1/auth/token/refresh/",
            {"refresh": old_refresh},
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_clinician_login_uses_current_contract(
        self,
    ) -> None:
        hospital = Hospital.objects.create(
            hospital_code="TEST-HOSPITAL-001",
            name="Test Hospital",
            is_active=True,
        )
        department = Department.objects.create(
            code="RADIOLOGY",
            name="Radiology",
            is_active=True,
        )
        clinician_user = User.objects.create_user(
            username="123456",
            password="clinician-test-password",
            role=User.Role.CLINICIAN,
        )
        clinician = Clinician.objects.create(
            user=clinician_user,
            name="Test Clinician",
            license_number="123456",
            hospital=hospital,
            department=department,
            approval_status=(
                Clinician.ApprovalStatus.APPROVED
            ),
        )

        response = self.client.post(
            "/api/v1/auth/clinician/login/",
            {
                "hospital_id": str(hospital.id),
                "department_code": department.code,
                "license_number": clinician.license_number,
                "password": "clinician-test-password",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access", response.data["data"])
        self.assertEqual(
            response.data["data"]["clinician"]["id"],
            str(clinician.id),
        )
