from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.appointments.models import Encounter
from apps.clinical_records.models import ClinicalRecord
from apps.clinicians.models import Clinician, Department
from apps.hospitals.models import Hospital

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


class ClinicianPatientMedicalHistoryTests(APITestCase):
    def setUp(self) -> None:
        self.patient = Patient.objects.create(
            medical_record_number="P-HISTORY-001",
            name="History Patient",
            status=Patient.Status.ACTIVE,
        )
        self.department = Department.objects.create(
            code="HISTORY_RADIOLOGY",
            name="History Radiology",
            is_active=True,
        )
        self.hospital = Hospital.objects.create(
            hospital_code="HISTORY-HOSPITAL",
            name="History Hospital",
            is_active=True,
        )
        self.user = User.objects.create_user(
            username="history-clinician",
            password="test-password",
            role="CLINICIAN",
        )
        self.clinician = Clinician.objects.create(
            user=self.user,
            name="History Clinician",
            license_number="661100",
            department=self.department,
            hospital=self.hospital,
            approval_status=(
                Clinician.ApprovalStatus.APPROVED
            ),
        )
        self.encounter = self.create_completed_encounter(
            hospital=self.hospital,
            clinician=self.clinician,
            user=self.user,
            number="E-HISTORY-001",
        )
        ClinicalRecord.objects.create(
            encounter=self.encounter,
            clinician=self.clinician,
            chief_complaint="두통",
            assessment="경과 관찰",
            plan="외래 추적",
            patient_visible_summary="추적 진료가 필요합니다.",
        )
        self.client.force_authenticate(user=self.user)

    def create_completed_encounter(
        self,
        *,
        hospital,
        clinician,
        user,
        number,
    ):
        from django.utils import timezone

        now = timezone.now()

        return Encounter.objects.create(
            encounter_number=number,
            patient=self.patient,
            department=self.department,
            hospital=hospital,
            attending_clinician=clinician,
            registered_by=user,
            encounter_type=Encounter.EncounterType.OUTPATIENT,
            status=Encounter.Status.COMPLETED,
            arrived_at=now,
            started_at=now,
            completed_at=now,
        )

    def test_returns_completed_record_in_same_hospital(
        self,
    ) -> None:
        response = self.client.get(
            reverse(
                "patients:clinician-patient-medical-history",
                kwargs={"patient_id": self.patient.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["meta"]["total_count"],
            1,
        )
        result = response.data["data"][0]
        self.assertEqual(
            result["encounter_id"],
            str(self.encounter.id),
        )
        self.assertEqual(
            result["clinical_record"]["assessment"],
            "경과 관찰",
        )

    def test_excludes_record_from_another_hospital(
        self,
    ) -> None:
        other_hospital = Hospital.objects.create(
            hospital_code="OTHER-HISTORY-HOSPITAL",
            name="Other History Hospital",
            is_active=True,
        )
        other_user = User.objects.create_user(
            username="other-history-clinician",
            password="test-password",
            role="CLINICIAN",
        )
        other_clinician = Clinician.objects.create(
            user=other_user,
            name="Other History Clinician",
            license_number="662200",
            department=self.department,
            hospital=other_hospital,
            approval_status=(
                Clinician.ApprovalStatus.APPROVED
            ),
        )
        other_encounter = self.create_completed_encounter(
            hospital=other_hospital,
            clinician=other_clinician,
            user=other_user,
            number="E-HISTORY-OTHER",
        )
        ClinicalRecord.objects.create(
            encounter=other_encounter,
            clinician=other_clinician,
            assessment="다른 병원 기록",
        )

        response = self.client.get(
            reverse(
                "patients:clinician-patient-medical-history",
                kwargs={"patient_id": self.patient.id},
            )
        )

        self.assertEqual(
            response.data["meta"]["total_count"],
            1,
        )
