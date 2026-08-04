from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.appointments.models import Encounter
from apps.audit_logs.models import AuditEvent
from apps.clinicians.models import Clinician, Department
from apps.hospitals.models import Hospital
from apps.notifications.models import Notification
from apps.patients.models import Patient

from .models import (
    DiagnosticReport,
    DiagnosticReportStatusHistory,
    Examination,
    ExaminationObservation,
    ExaminationStatusHistory,
)


class ExaminationApiTests(APITestCase):
    def setUp(self) -> None:
        self.hospital = Hospital.objects.create(
            hospital_code="DIAG-HOSPITAL",
            name="Diagnostic Hospital",
            is_active=True,
        )
        self.department = Department.objects.create(
            code="DIAG-NEURO",
            name="Neurology",
            is_active=True,
        )
        self.user, self.clinician = self.create_clinician(
            "610001",
            self.hospital,
        )
        other_hospital = Hospital.objects.create(
            hospital_code="OTHER-DIAG-HOSPITAL",
            name="Other Hospital",
            is_active=True,
        )
        self.outsider_user, self.outsider = self.create_clinician(
            "610002",
            other_hospital,
        )
        patient_user = User.objects.create_user(
            username="diag-patient",
            password="test-password",
            role=User.Role.PATIENT,
        )
        self.patient = Patient.objects.create(
            user=patient_user,
            medical_record_number="P-DIAG-001",
            name="Diagnostic Patient",
            status=Patient.Status.ACTIVE,
        )
        self.encounter = Encounter.objects.create(
            encounter_number="E-DIAG-001",
            patient=self.patient,
            department=self.department,
            hospital=self.hospital,
            attending_clinician=self.clinician,
            registered_by=self.user,
            encounter_type=Encounter.EncounterType.OUTPATIENT,
            status=Encounter.Status.IN_PROGRESS,
        )
        self.client.force_authenticate(user=self.user)

    def create_clinician(self, username, hospital):
        user = User.objects.create_user(
            username=username,
            password="test-password",
            role=User.Role.CLINICIAN,
        )
        clinician = Clinician.objects.create(
            user=user,
            name=f"Doctor {username}",
            license_number=username,
            hospital=hospital,
            department=self.department,
            approval_status=Clinician.ApprovalStatus.APPROVED,
        )
        return user, clinician

    def payload(self):
        return {
            "encounter_id": str(self.encounter.id),
            "test_code": "CBC",
            "test_name": "Complete blood count",
            "category": "LABORATORY",
            "source": "INTERNAL",
            "performed_at": (
                timezone.now() - timedelta(hours=1)
            ).isoformat(),
            "observations": [
                {
                    "code": "PLT",
                    "name": "Platelet",
                    "value_type": "NUMERIC",
                    "numeric_value": "82",
                    "unit": "10^3/uL",
                    "reference_low": "150",
                    "reference_high": "400",
                    "reference_text": "",
                    "interpretation": "LOW",
                },
                {
                    "code": "COMMENT",
                    "name": "Morphology",
                    "value_type": "TEXT",
                    "text_value": "No platelet clumping",
                    "unit": "",
                    "reference_text": "No abnormal findings",
                    "interpretation": "NORMAL",
                },
            ],
            "report_title": "CBC result",
            "report_summary": "Thrombocytopenia",
            "report_conclusion": "Clinical correlation advised.",
        }

    def create_result(self):
        response = self.client.post(
            "/api/v1/examinations/",
            self.payload(),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return Examination.objects.get(
            id=response.data["data"]["examination_id"]
        )

    def test_create_builds_result_report_and_history(self):
        examination = self.create_result()

        self.assertEqual(examination.status, Examination.Status.PRELIMINARY)
        self.assertEqual(examination.observations.count(), 2)
        self.assertEqual(
            examination.reports.get().status,
            DiagnosticReport.Status.DRAFT,
        )
        self.assertEqual(ExaminationStatusHistory.objects.count(), 1)
        self.assertEqual(DiagnosticReportStatusHistory.objects.count(), 1)
        self.assertTrue(
            AuditEvent.objects.filter(
                resource_type="examination",
                action=AuditEvent.Action.CREATED,
            ).exists()
        )

    def test_list_supports_interpretation_and_search_filters(self):
        self.create_result()
        response = self.client.get(
            "/api/v1/examinations/?interpretation=LOW&search=blood"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["meta"]["total_count"], 1)
        self.assertEqual(
            response.data["data"][0]["overall_interpretation"],
            ExaminationObservation.Interpretation.LOW,
        )

    def test_outside_hospital_cannot_open_result(self):
        examination = self.create_result()
        self.client.force_authenticate(user=self.outsider_user)

        response = self.client.get(
            f"/api/v1/examinations/{examination.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_finalize_and_release_result(self):
        examination = self.create_result()
        finalize_response = self.client.post(
            f"/api/v1/examinations/{examination.id}/finalize/",
            {
                "summary": "Final summary",
                "conclusion": "Final conclusion",
            },
            format="json",
        )

        self.assertEqual(finalize_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            finalize_response.data["data"]["status"],
            Examination.Status.FINAL,
        )
        report = DiagnosticReport.objects.get(examination=examination)
        self.assertIsNotNone(report.signed_at)

        release_response = self.client.post(
            f"/api/v1/examinations/{examination.id}/release/",
            {},
            format="json",
        )
        self.assertEqual(release_response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            release_response.data["data"]["report"][
                "is_released_to_patient"
            ]
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.patient.user,
                type=Notification.Type.TEST_RESULT,
                data__examination_id=str(examination.id),
            ).exists()
        )

    def test_preliminary_result_cannot_be_released(self):
        examination = self.create_result()
        response = self.client.post(
            f"/api/v1/examinations/{examination.id}/release/",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
