from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.appointments.models import Appointment
from apps.clinicians.models import Clinician, Department
from apps.hospitals.models import Hospital
from apps.notifications.models import Notification
from apps.patients.models import Patient, PatientAccountClaim


User = get_user_model()


class PatientClaimSignupApiTests(APITestCase):
    CLAIM_CODE = "482913"
    PASSWORD = "BrainOn-Test-2026!"

    def setUp(self):
        self.hospital_a = Hospital.objects.create(
            hospital_code="TEST-H001",
            name="테스트 중앙병원",
            address="대전광역시 서구 테스트로 1",
            phone="042-000-0001",
            is_active=True,
        )
        self.hospital_b = Hospital.objects.create(
            hospital_code="TEST-H002",
            name="테스트 타병원",
            address="대전광역시 유성구 테스트로 2",
            phone="042-000-0002",
            is_active=True,
        )

        self.department = Department.objects.create(
            code="TEST-NS",
            name="신경외과",
            is_active=True,
        )

        self.clinician_user = User.objects.create_user(
            username="991001",
            password=self.PASSWORD,
            role=User.Role.CLINICIAN,
        )
        self.clinician = Clinician.objects.create(
            user=self.clinician_user,
            name="박의사",
            license_number="991001",
            hospital=self.hospital_a,
            department=self.department,
            approval_status=Clinician.ApprovalStatus.APPROVED,
            approved_at=timezone.now(),
        )

        self.patient = Patient.objects.create(
            user=None,
            medical_record_number="H001-P000001",
            name="김민준",
            birth_date=date(1963, 4, 12),
            sex=Patient.Sex.MALE,
            phone="010-1234-5678",
            emergency_contact="010-9999-9999",
            address="대전광역시 서구",
            status=Patient.Status.ACTIVE,
        )

        Appointment.objects.create(
            patient=self.patient,
            clinician=self.clinician,
            department=self.department,
            hospital=self.hospital_a,
            scheduled_at=timezone.now() + timedelta(days=3),
            location="본관 3층 신경외과",
            reason="뇌출혈 외래 추적",
            status=Appointment.Status.CONFIRMED,
        )

        self.url = reverse(
            "accounts:patient-claim-signup"
        )

    def create_claim(
        self,
        *,
        raw_code: str | None = None,
        expires_at=None,
    ) -> PatientAccountClaim:
        claim = PatientAccountClaim(
            patient=self.patient,
            issued_by=self.clinician_user,
            expires_at=(
                expires_at
                or timezone.now() + timedelta(minutes=30)
            ),
        )
        claim.set_claim_code(
            raw_code or self.CLAIM_CODE
        )
        claim.save()
        return claim

    def make_payload(self, **overrides):
        payload = {
            "hospital_id": str(self.hospital_a.id),
            "medical_record_number": (
                self.patient.medical_record_number
            ),
            "name": self.patient.name,
            "birth_date": (
                self.patient.birth_date.isoformat()
            ),
            "phone": self.patient.phone,
            "claim_code": self.CLAIM_CODE,
            "username": "minjun63",
            "password": self.PASSWORD,
            "password_confirm": self.PASSWORD,
            "email": "minjun63@example.com",
        }
        payload.update(overrides)
        return payload

    def test_existing_patient_signup_succeeds(self):
        claim = self.create_claim()

        response = self.client.post(
            self.url,
            self.make_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        self.patient.refresh_from_db()
        claim.refresh_from_db()

        new_user = User.objects.get(
            username="minjun63"
        )

        self.assertEqual(
            self.patient.user_id,
            new_user.id,
        )
        self.assertEqual(
            new_user.role,
            User.Role.PATIENT,
        )
        self.assertEqual(
            claim.status,
            PatientAccountClaim.Status.USED,
        )
        self.assertEqual(
            claim.claimed_user_id,
            new_user.id,
        )
        self.assertIsNotNone(claim.used_at)

        self.assertIn(
            "access",
            response.data["data"],
        )
        self.assertIn(
            "refresh",
            response.data["data"],
        )

        self.assertTrue(
            Notification.objects.filter(
                recipient=new_user,
                type=Notification.Type.SYSTEM,
                deduplication_key=(
                    f"patient-claim-complete:{claim.id}"
                ),
            ).exists()
        )

    def test_wrong_claim_code_increases_failed_attempts(self):
        claim = self.create_claim()

        response = self.client.post(
            self.url,
            self.make_payload(
                claim_code="000000",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data,
        )

        claim.refresh_from_db()
        self.patient.refresh_from_db()

        self.assertEqual(
            claim.failed_attempts,
            1,
        )
        self.assertEqual(
            claim.status,
            PatientAccountClaim.Status.ISSUED,
        )
        self.assertIsNone(self.patient.user_id)
        self.assertFalse(
            User.objects.filter(
                username="minjun63"
            ).exists()
        )

    def test_expired_claim_code_is_rejected(self):
        claim = self.create_claim()

        PatientAccountClaim.objects.filter(
            id=claim.id
        ).update(
            expires_at=(
                timezone.now() - timedelta(minutes=1)
            )
        )

        response = self.client.post(
            self.url,
            self.make_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data,
        )

        claim.refresh_from_db()
        self.patient.refresh_from_db()

        self.assertEqual(
            claim.status,
            PatientAccountClaim.Status.EXPIRED,
        )
        self.assertIsNone(self.patient.user_id)
        self.assertFalse(
            User.objects.filter(
                username="minjun63"
            ).exists()
        )

    def test_patient_with_existing_account_cannot_link_again(self):
        claim = self.create_claim()

        existing_user = User.objects.create_user(
            username="already-linked",
            password=self.PASSWORD,
            role=User.Role.PATIENT,
        )
        self.patient.user = existing_user
        self.patient.save(
            update_fields=[
                "user",
                "updated_at",
            ]
        )

        response = self.client.post(
            self.url,
            self.make_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data,
        )

        claim.refresh_from_db()
        self.patient.refresh_from_db()

        self.assertEqual(
            self.patient.user_id,
            existing_user.id,
        )
        self.assertEqual(
            claim.status,
            PatientAccountClaim.Status.ISSUED,
        )
        self.assertFalse(
            User.objects.filter(
                username="minjun63"
            ).exists()
        )

    def test_other_hospital_without_history_is_rejected(self):
        claim = self.create_claim()

        response = self.client.post(
            self.url,
            self.make_payload(
                hospital_id=str(self.hospital_b.id),
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data,
        )

        claim.refresh_from_db()
        self.patient.refresh_from_db()

        self.assertEqual(
            claim.status,
            PatientAccountClaim.Status.ISSUED,
        )
        self.assertIsNone(self.patient.user_id)
        self.assertFalse(
            User.objects.filter(
                username="minjun63"
            ).exists()
        )

    def test_five_wrong_attempts_revoke_claim(self):
        claim = self.create_claim()

        for _ in range(5):
            response = self.client.post(
                self.url,
                self.make_payload(
                    claim_code="000000",
                ),
                format="json",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data,
        )

        claim.refresh_from_db()

        self.assertEqual(
            claim.failed_attempts,
            5,
        )
        self.assertEqual(
            claim.status,
            PatientAccountClaim.Status.REVOKED,
        )
