from datetime import timedelta
from urllib import response

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.clinicians.models import Clinician, Department
from apps.hospitals.models import Hospital
from apps.notifications.models import Notification
from apps.patients.models import Patient

from .models import Appointment, Encounter


class ClinicianEncounterApiTests(APITestCase):
    def setUp(self) -> None:
        self.hospital = Hospital.objects.create(
            hospital_code="ENCOUNTER-HOSPITAL",
            name="Encounter Hospital",
            is_active=True,
        )
        self.department = Department.objects.create(
            code="ENCOUNTER_RADIOLOGY",
            name="Encounter Radiology",
            is_active=True,
        )
        self.user = User.objects.create_user(
            username="encounter-clinician",
            password="test-password",
            role=User.Role.CLINICIAN,
        )
        self.clinician = Clinician.objects.create(
            user=self.user,
            name="Encounter Clinician",
            license_number="551100",
            hospital=self.hospital,
            department=self.department,
            approval_status=(
                Clinician.ApprovalStatus.APPROVED
            ),
        )
        self.patient = Patient.objects.create(
            medical_record_number="P-ENC-001",
            name="Encounter Patient",
            status=Patient.Status.ACTIVE,
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            clinician=self.clinician,
            department=self.department,
            hospital=self.hospital,
            created_by=self.user,
            scheduled_at=(
                timezone.now() + timedelta(hours=1)
            ),
            status=Appointment.Status.CHECKED_IN,
        )
        self.client.force_authenticate(user=self.user)

    def create_encounter(self):
        return Encounter.objects.create(
            encounter_number=(
                f"E-TEST-{Encounter.objects.count() + 1}"
            ),
            patient=self.patient,
            appointment=self.appointment,
            department=self.department,
            hospital=self.hospital,
            attending_clinician=self.clinician,
            registered_by=self.user,
            encounter_type=Encounter.EncounterType.OUTPATIENT,
            status=Encounter.Status.ARRIVED,
            arrived_at=timezone.now(),
        )

    def test_appointment_create_update_and_cancel_create_notifications(
        self,
    ) -> None:
        scheduled_at = timezone.now() + timedelta(days=2)
        create_response = self.client.post(
            "/api/v1/appointments/",
            {
                "patient_id": str(self.patient.id),
                "scheduled_at": scheduled_at.isoformat(),
                "duration_minutes": 30,
                "location": "Room 1",
                "reason": "Follow-up",
            },
            format="json",
        )

        self.assertEqual(
            create_response.status_code,
            status.HTTP_201_CREATED,
        )
        appointment_id = create_response.data["data"][
            "appointment_id"
        ]
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.user,
                type=Notification.Type.APPOINTMENT,
                data__appointment_id=appointment_id,
                data__event="CREATED",
            ).exists()
        )

        update_response = self.client.patch(
            f"/api/v1/appointments/{appointment_id}/",
            {
                "scheduled_at": (
                    scheduled_at + timedelta(hours=1)
                ).isoformat(),
                "duration_minutes": 30,
                "location": "Room 2",
                "reason": "Changed schedule",
            },
            format="json",
        )
        self.assertEqual(
            update_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.user,
                data__appointment_id=appointment_id,
                data__event="UPDATED",
            ).exists()
        )

        cancel_response = self.client.patch(
            f"/api/v1/appointments/{appointment_id}/",
            {
                "status": Appointment.Status.CANCELLED,
                "reason": "Patient request",
            },
            format="json",
        )
        self.assertEqual(
            cancel_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.user,
                data__appointment_id=appointment_id,
                data__event="STATUS_CANCELLED",
            ).exists()
        )

    def test_appointment_list_filters_by_patient_id(self) -> None:
        another_patient = Patient.objects.create(
            medical_record_number="P-ENC-002",
            name="Another Patient",
            status=Patient.Status.ACTIVE,
        )
        Appointment.objects.create(
            patient=another_patient,
            clinician=self.clinician,
            department=self.department,
            hospital=self.hospital,
            created_by=self.user,
            scheduled_at=timezone.now() + timedelta(hours=2),
            status=Appointment.Status.SCHEDULED,
        )

        response = self.client.get(
            "/api/v1/appointments/",
            {"patient_id": str(self.patient.id)},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["meta"]["total_count"], 1)
        self.assertEqual(
            response.data["data"][0]["patient_id"],
            str(self.patient.id),
        )

    def test_appointment_list_rejects_invalid_patient_id(self) -> None:
        response = self.client.get(
            "/api/v1/appointments/",
            {"patient_id": "not-a-uuid"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_clinician_cannot_register_patient_arrival(
        self,
    ) -> None:
        response = self.client.post(
            "/api/v1/encounters/",
            {"appointment_id": str(self.appointment.id)},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_registers_today_appointment_in_encounter_queue(
        self,
    ) -> None:
        self.appointment.status = Appointment.Status.SCHEDULED
        self.appointment.save(update_fields=["status", "updated_at"])
        url = (
            f"/api/v1/appointments/{self.appointment.id}/encounter/"
        )

        first_response = self.client.post(url, {}, format="json")
        second_response = self.client.post(url, {}, format="json")

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
            first_response.data,
        )
        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
            second_response.data,
        )
        self.assertEqual(Encounter.objects.count(), 1)
        encounter = Encounter.objects.get(
            appointment=self.appointment,
        )
        self.assertEqual(encounter.patient, self.patient)
        self.assertEqual(
            encounter.attending_clinician,
            self.clinician,
        )
        self.assertEqual(encounter.status, Encounter.Status.ARRIVED)
        self.appointment.refresh_from_db()
        self.assertEqual(
            self.appointment.status,
            Appointment.Status.CHECKED_IN,
        )
        self.assertEqual(
            first_response.data["data"]["appointment"]
            ["encounter_id"],
            str(encounter.id),
        )

    def test_cannot_register_future_appointment_in_encounter_queue(
        self,
    ) -> None:
        self.appointment.scheduled_at = (
            timezone.now() + timedelta(days=1)
        )
        self.appointment.save(
            update_fields=["scheduled_at", "updated_at"]
        )

        response = self.client.post(
            f"/api/v1/appointments/{self.appointment.id}/encounter/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(
            Encounter.objects.filter(
                appointment=self.appointment,
            ).exists()
        )

    def test_cancel_checked_in_appointment_cancels_arrived_encounter(
        self,
    ) -> None:
        encounter = self.create_encounter()

        response = self.client.patch(
            f"/api/v1/appointments/{self.appointment.id}/",
            {
                "status": Appointment.Status.CANCELLED,
                "reason": "Patient request",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )
        self.appointment.refresh_from_db()
        encounter.refresh_from_db()
        self.assertEqual(
            self.appointment.status,
            Appointment.Status.CANCELLED,
        )
        self.assertEqual(encounter.status, Encounter.Status.CANCELLED)

    def test_cannot_cancel_appointment_after_encounter_started(
        self,
    ) -> None:
        encounter = self.create_encounter()
        encounter.status = Encounter.Status.IN_PROGRESS
        encounter.started_at = timezone.now()
        encounter.save(update_fields=["status", "started_at", "updated_at"])

        response = self.client.patch(
            f"/api/v1/appointments/{self.appointment.id}/",
            {
                "status": Appointment.Status.CANCELLED,
                "reason": "Patient request",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.appointment.refresh_from_db()
        encounter.refresh_from_db()
        self.assertEqual(
            self.appointment.status,
            Appointment.Status.CHECKED_IN,
        )
        self.assertEqual(encounter.status, Encounter.Status.IN_PROGRESS)

    def test_lists_and_searches_own_encounters(
        self,
    ) -> None:
        self.create_encounter()

        response = self.client.get(
            "/api/v1/encounters/",
            {
                "search": "P-ENC-001",
                "status": "ARRIVED",
            },
        )
        print("\n=== ENCOUNTER COMPLETE RESPONSE ===")
        print("status_code:", response.status_code)
        print("data:", getattr(response, "data", None))
        print(
            "content:",
            response.content.decode("utf-8", errors="replace"),
        )
        print("===================================\n")
        self.assertEqual(
            response.status_code,
            200,
            msg=(
                f"\nstatus_code={response.status_code}"
                f"\ndata={getattr(response, 'data', None)}"
                f"\ncontent={response.content.decode('utf-8', errors='replace')}"
            ),
        )
        self.assertEqual(
            response.data["meta"]["total_count"],
            1,
        )
        self.assertEqual(
            response.data["data"][0]["patient_id"],
            str(self.patient.id),
        )

    def test_saves_record_then_completes_encounter(
        self,
    ) -> None:
        encounter = self.create_encounter()
        encounter_id = encounter.id
        status_url = (
            f"/api/v1/encounters/{encounter_id}/status/"
        )
        record_url = (
            "/api/v1/encounters/"
            f"{encounter_id}/clinical-record/"
        )

        start_response = self.client.patch(
            status_url,
            {"status": "IN_PROGRESS"},
            format="json",
        )
        premature_completion = self.client.patch(
            status_url,
            {"status": "COMPLETED"},
            format="json",
        )
        record_response = self.client.put(
            record_url,
            {
                "chief_complaint": "두통",
                "subjective": "오전부터 두통 발생",
                "objective": "의식 명료",
                "assessment": "추가 관찰 필요",
                "plan": "CT 결과 확인",
                "patient_visible_summary": (
                    "검사 결과를 확인할 예정입니다."
                ),
            },
            format="json",
        )
        completion_response = self.client.patch(
            status_url,
            {"status": "COMPLETED"},
            format="json",
        )
        self.appointment.refresh_from_db()

        self.assertEqual(
            start_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            premature_completion.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            record_response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            completion_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            completion_response.data["data"]["status"],
            Encounter.Status.COMPLETED,
        )
        self.assertEqual(
            self.appointment.status,
            Appointment.Status.COMPLETED,
        )

    def test_cannot_read_another_clinicians_encounter(
        self,
    ) -> None:
        other_user = User.objects.create_user(
            username="other-encounter-clinician",
            password="test-password",
            role=User.Role.CLINICIAN,
        )
        other_clinician = Clinician.objects.create(
            user=other_user,
            name="Other Clinician",
            license_number="552200",
            hospital=self.hospital,
            department=self.department,
            approval_status=(
                Clinician.ApprovalStatus.APPROVED
            ),
        )
        other_encounter = Encounter.objects.create(
            encounter_number="E-OTHER-001",
            patient=self.patient,
            department=self.department,
            hospital=self.hospital,
            attending_clinician=other_clinician,
            registered_by=other_user,
            encounter_type=Encounter.EncounterType.OUTPATIENT,
            status=Encounter.Status.ARRIVED,
            arrived_at=timezone.now(),
        )

        response = self.client.get(
            f"/api/v1/encounters/{other_encounter.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
