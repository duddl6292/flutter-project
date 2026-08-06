from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.appointments.models import Encounter
from apps.clinicians.models import Clinician, Department
from apps.hospitals.models import Hospital
from apps.notifications.models import Notification
from apps.patients.models import Patient

from .models import (
    Consultation,
    ConsultationMessage,
    ConsultationParticipant,
    ConsultationStatusHistory,
    EncounterAccessGrant,
)


class ConsultationApiTests(APITestCase):
    def setUp(self) -> None:
        self.hospital = Hospital.objects.create(
            hospital_code="CONSULT-HOSPITAL",
            name="Consult Hospital",
            is_active=True,
        )
        self.consultant_hospital = Hospital.objects.create(
            hospital_code="CONSULT-REMOTE-HOSPITAL",
            name="Consult Remote Hospital",
            is_active=True,
        )
        self.department = Department.objects.create(
            code="CONSULT-RADIOLOGY",
            name="Consult Radiology",
            is_active=True,
        )
        self.other_department = Department.objects.create(
            code="CONSULT-NEURO",
            name="Consult Neurosurgery",
            is_active=True,
        )
        (
            self.requester_user,
            self.requester,
        ) = self.create_clinician(
            username="510001",
            name="Requester",
            department=self.department,
        )
        (
            self.consultant_user,
            self.consultant,
        ) = self.create_clinician(
            username="510002",
            name="Consultant",
            department=self.other_department,
            hospital=self.consultant_hospital,
        )
        (
            self.outsider_user,
            self.outsider,
        ) = self.create_clinician(
            username="510003",
            name="Outsider",
            department=self.other_department,
            hospital=self.consultant_hospital,
        )
        self.patient = Patient.objects.create(
            medical_record_number="P-CONSULT-001",
            name="Consult Patient",
            status=Patient.Status.ACTIVE,
        )
        self.encounter = Encounter.objects.create(
            encounter_number="E-CONSULT-001",
            patient=self.patient,
            department=self.department,
            hospital=self.hospital,
            attending_clinician=self.requester,
            registered_by=self.requester_user,
            encounter_type=(
                Encounter.EncounterType.OUTPATIENT
            ),
            status=Encounter.Status.IN_PROGRESS,
        )
        self.client.force_authenticate(
            user=self.requester_user
        )

    def create_clinician(
        self,
        *,
        username,
        name,
        department,
        hospital=None,
    ):
        user = User.objects.create_user(
            username=username,
            password="test-password",
            role=User.Role.CLINICIAN,
        )
        clinician = Clinician.objects.create(
            user=user,
            name=name,
            license_number=username,
            hospital=hospital or self.hospital,
            department=department,
            approval_status=(
                Clinician.ApprovalStatus.APPROVED
            ),
        )

        return user, clinician

    def create_payload(self):
        return {
            "encounter_id": str(self.encounter.id),
            "consultant_clinician_id": str(
                self.consultant.id
            ),
            "subject": "Emergency image review",
            "priority": Consultation.Priority.URGENT,
            "question": "Please review this encounter.",
            "due_at": (
                timezone.now() + timedelta(days=2)
            ).isoformat(),
        }

    def create_consultation(self):
        response = self.client.post(
            "/api/v1/consultations/",
            self.create_payload(),
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        return Consultation.objects.get(
            id=response.data["data"][
                "consultation_id"
            ]
        )

    def test_create_builds_workflow_records(
        self,
    ) -> None:
        consultation = self.create_consultation()

        self.assertEqual(
            consultation.requester_clinician,
            self.requester,
        )
        self.assertEqual(
            consultation.consultant_clinician,
            self.consultant,
        )
        self.assertEqual(
            consultation.status,
            Consultation.Status.REQUESTED,
        )
        self.assertEqual(
            ConsultationParticipant.objects.count(),
            2,
        )
        self.assertEqual(
            ConsultationMessage.objects.count(),
            1,
        )
        self.assertEqual(
            ConsultationStatusHistory.objects.count(),
            1,
        )
        self.assertEqual(
            EncounterAccessGrant.objects.count(),
            1,
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.consultant_user,
                type=Notification.Type.CONSULTATION,
            ).exists()
        )

    def test_received_consultation_can_be_completed(
        self,
    ) -> None:
        consultation = self.create_consultation()
        self.client.force_authenticate(
            user=self.consultant_user
        )

        accept_response = self.client.post(
            (
                "/api/v1/consultations/"
                f"{consultation.id}/accept/"
            ),
            {},
            format="json",
        )
        self.assertEqual(
            accept_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            accept_response.data["data"]["status"],
            Consultation.Status.IN_PROGRESS,
        )

        message_response = self.client.post(
            (
                "/api/v1/consultations/"
                f"{consultation.id}/messages/"
            ),
            {"content": "Additional clinical question"},
            format="json",
        )
        self.assertEqual(
            message_response.status_code,
            status.HTTP_201_CREATED,
        )

        complete_response = self.client.post(
            (
                "/api/v1/consultations/"
                f"{consultation.id}/complete/"
            ),
            {"response": "Final consultation opinion"},
            format="json",
        )
        self.assertEqual(
            complete_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            complete_response.data["data"]["status"],
            Consultation.Status.COMPLETED,
        )

        consultation.refresh_from_db()
        self.assertEqual(
            consultation.response,
            "Final consultation opinion",
        )
        self.assertIsNotNone(consultation.completed_at)
        self.assertIsNotNone(
            consultation.access_grants.get().revoked_at
        )

    def test_accepted_consultation_temporarily_shares_patient(self):
        consultation = self.create_consultation()
        self.client.force_authenticate(
            user=self.consultant_user
        )

        before_accept = self.client.get(
            "/api/v1/patients/"
        )
        self.assertEqual(
            before_accept.data["meta"]["total_count"],
            0,
        )
        self.assertEqual(
            self.client.get(
                f"/api/v1/patients/{self.patient.id}/"
            ).status_code,
            status.HTTP_404_NOT_FOUND,
        )

        accept_response = self.client.post(
            f"/api/v1/consultations/{consultation.id}/accept/",
            {},
            format="json",
        )
        self.assertEqual(
            accept_response.status_code,
            status.HTTP_200_OK,
        )

        during_consultation = self.client.get(
            "/api/v1/patients/"
        )
        self.assertEqual(
            during_consultation.data["meta"]["total_count"],
            1,
        )
        shared_patient = during_consultation.data["data"][0]
        self.assertEqual(
            shared_patient["access_scope"],
            "CONSULTATION",
        )
        self.assertEqual(
            shared_patient["shared_consultation_id"],
            str(consultation.id),
        )
        self.assertEqual(
            self.client.get(
                f"/api/v1/patients/{self.patient.id}/"
            ).status_code,
            status.HTTP_200_OK,
        )

        complete_response = self.client.post(
            f"/api/v1/consultations/{consultation.id}/complete/",
            {"response": "Consultation complete"},
            format="json",
        )
        self.assertEqual(
            complete_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            self.client.get(
                f"/api/v1/patients/{self.patient.id}/"
            ).status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_requester_can_cancel_consultation(
        self,
    ) -> None:
        consultation = self.create_consultation()
        response = self.client.post(
            (
                "/api/v1/consultations/"
                f"{consultation.id}/cancel/"
            ),
            {"reason": "No longer needed"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )
        consultation.refresh_from_db()
        self.assertEqual(
            consultation.status,
            Consultation.Status.CANCELLED,
        )
        self.assertEqual(
            consultation.status_history.last().reason,
            "No longer needed",
        )

    def test_outsider_cannot_read_consultation(
        self,
    ) -> None:
        consultation = self.create_consultation()
        self.client.force_authenticate(
            user=self.outsider_user
        )

        response = self.client.get(
            (
                "/api/v1/consultations/"
                f"{consultation.id}/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_list_filters_received_and_sent(
        self,
    ) -> None:
        consultation = self.create_consultation()

        sent_response = self.client.get(
            "/api/v1/consultations/?box=sent"
        )
        self.assertEqual(
            sent_response.data["meta"]["total_count"],
            1,
        )

        self.client.force_authenticate(
            user=self.consultant_user
        )
        received_response = self.client.get(
            "/api/v1/consultations/?box=received"
        )
        self.assertEqual(
            received_response.data["meta"][
                "total_count"
            ],
            1,
        )
        self.assertEqual(
            received_response.data["data"][0][
                "consultation_id"
            ],
            str(consultation.id),
        )

    def test_cannot_request_for_another_encounter(
        self,
    ) -> None:
        self.client.force_authenticate(
            user=self.outsider_user
        )
        response = self.client.post(
            "/api/v1/consultations/",
            self.create_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_dashboard_contains_consultation_summary(
        self,
    ) -> None:
        consultation = self.create_consultation()

        response = self.client.get(
            "/api/v1/clinicians/"
            "clinicians/me/dashboard"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )
        self.assertEqual(
            response.data["data"]["summary"]
            ["consultations"]["total"],
            1,
        )
        self.assertEqual(
            response.data["data"]["consultations"]
            [0]["consultation_id"],
            str(consultation.id),
        )
