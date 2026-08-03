from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.appointments.models import Appointment
from apps.clinicians.models import Clinician, Department
from apps.hospitals.models import Hospital
from apps.patients.models import Patient, PatientAccountClaim


User = get_user_model()


class PatientAccountClaimIssueApiTests(APITestCase):
    PASSWORD = "BrainOn-Test-2026!"

    def setUp(self):
        self.hospital_a = Hospital.objects.create(
            hospital_code="ISSUE-H001",
            name="발급 테스트병원",
            address="대전광역시 서구 발급로 1",
            phone="042-000-1001",
            is_active=True,
        )
        self.hospital_b = Hospital.objects.create(
            hospital_code="ISSUE-H002",
            name="다른 테스트병원",
            address="대전광역시 유성구 발급로 2",
            phone="042-000-1002",
            is_active=True,
        )

        self.department = Department.objects.create(
            code="ISSUE-NS",
            name="신경외과",
            is_active=True,
        )

        self.clinician_user = User.objects.create_user(
            username="992001",
            password=self.PASSWORD,
            role=User.Role.CLINICIAN,
        )
        self.clinician = Clinician.objects.create(
            user=self.clinician_user,
            name="김의사",
            license_number="992001",
            hospital=self.hospital_a,
            department=self.department,
            approval_status=Clinician.ApprovalStatus.APPROVED,
            approved_at=timezone.now(),
        )

        self.patient = Patient.objects.create(
            user=None,
            medical_record_number="ISSUE-P000001",
            name="이환자",
            birth_date=date(1970, 1, 20),
            sex=Patient.Sex.FEMALE,
            phone="010-2222-3333",
            status=Patient.Status.ACTIVE,
        )

        Appointment.objects.create(
            patient=self.patient,
            clinician=self.clinician,
            department=self.department,
            hospital=self.hospital_a,
            scheduled_at=timezone.now() + timedelta(days=5),
            location="본관 신경외과",
            reason="진료 예약",
            status=Appointment.Status.CONFIRMED,
        )

        self.url = reverse(
            "patients:patient-account-claim-issue",
            kwargs={
                "patient_id": self.patient.id,
            },
        )

        self.client.force_authenticate(
            user=self.clinician_user,
        )

    def test_clinician_can_issue_claim_for_own_hospital(self):
        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        raw_code = response.data["data"]["claim_code"]

        self.assertEqual(len(raw_code), 6)
        self.assertTrue(raw_code.isdigit())

        claim = PatientAccountClaim.objects.get(
            id=response.data["data"]["claim_id"]
        )

        self.assertEqual(
            claim.patient_id,
            self.patient.id,
        )
        self.assertEqual(
            claim.issued_by_id,
            self.clinician_user.id,
        )
        self.assertEqual(
            claim.status,
            PatientAccountClaim.Status.ISSUED,
        )
        self.assertNotEqual(
            claim.claim_code_hash,
            raw_code,
        )
        self.assertTrue(
            claim.check_claim_code(raw_code)
        )

    def test_clinician_cannot_issue_for_other_hospital(self):
        response = self.client.post(
            self.url,
            {
                "hospital_id": str(self.hospital_b.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data,
        )
        self.assertFalse(
            PatientAccountClaim.objects.exists()
        )
