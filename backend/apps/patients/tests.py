from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Patient


User = get_user_model()


class PatientApiTests(APITestCase):
    def setUp(self):
        self.patient_user = User.objects.create_user(
            username="patient01",
            password="Test1234!",
            email="patient01@example.com",
            role="PATIENT",
        )

        self.patient = Patient.objects.create(
            user=self.patient_user,
            medical_record_number="P20260001",
            name="김환자",
            birth_date="1980-05-10",
            sex=Patient.Sex.MALE,
            phone="010-1234-5678",
            emergency_contact="010-9999-9999",
            address="대전광역시 서구",
        )

        self.clinician_user = User.objects.create_user(
            username="123456",
            password="Test1234!",
            role="CLINICIAN",
        )

    def test_patient_can_get_own_profile(self):
        self.client.force_authenticate(
            user=self.patient_user,
        )

        response = self.client.get(
            reverse("patients:patient-me")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["data"]["name"],
            "김환자",
        )

    def test_patient_can_update_own_profile(self):
        self.client.force_authenticate(
            user=self.patient_user,
        )

        response = self.client.patch(
            reverse("patients:patient-me"),
            {
                "phone": "010-5555-5555",
                "address": "대전광역시 유성구",
                "email": "new-patient@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.patient.refresh_from_db()
        self.patient_user.refresh_from_db()

        self.assertEqual(
            self.patient.phone,
            "010-5555-5555",
        )
        self.assertEqual(
            self.patient_user.email,
            "new-patient@example.com",
        )

    def test_patient_cannot_access_patient_list(self):
        self.client.force_authenticate(
            user=self.patient_user,
        )

        response = self.client.get(
            reverse("patients:patient-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_clinician_can_access_patient_list(self):
        self.client.force_authenticate(
            user=self.clinician_user,
        )

        response = self.client.get(
            reverse("patients:patient-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["meta"]["total_count"],
            1,
        )

    def test_clinician_can_access_patient_detail(self):
        self.client.force_authenticate(
            user=self.clinician_user,
        )

        response = self.client.get(
            reverse(
                "patients:patient-detail",
                kwargs={
                    "patient_id": self.patient.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["data"]["patient_id"],
            str(self.patient.id),
        )