from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.appointments.models import Appointment, Encounter
from apps.clinical_records.models import ClinicalRecord
from apps.clinicians.models import Clinician, Department
from apps.ct_analysis.models import CTCase, InferenceJob
from apps.hospitals.models import Hospital
from apps.patients.models import Patient
from apps.prescriptions.models import (
    Prescription,
    PrescriptionItem,
)


class ClinicianSummaryReportApiTests(APITestCase):
    def setUp(self) -> None:
        self.now = timezone.now()
        self.hospital = Hospital.objects.create(
            hospital_code="REPORT-HOSPITAL",
            name="Report Hospital",
            is_active=True,
        )
        self.department = Department.objects.create(
            code="REPORT_RADIOLOGY",
            name="Report Radiology",
            is_active=True,
        )
        self.user = User.objects.create_user(
            username="112233",
            password="test-password",
            role=User.Role.CLINICIAN,
        )
        self.clinician = Clinician.objects.create(
            user=self.user,
            name="Report Clinician",
            license_number="112233",
            hospital=self.hospital,
            department=self.department,
            approval_status=(
                Clinician.ApprovalStatus.APPROVED
            ),
        )
        self.patient = Patient.objects.create(
            medical_record_number="P-REPORT-001",
            name="Report Patient",
            status=Patient.Status.ACTIVE,
        )
        self.completed_appointment = (
            Appointment.objects.create(
                patient=self.patient,
                clinician=self.clinician,
                department=self.department,
                hospital=self.hospital,
                scheduled_at=self.now,
                status=Appointment.Status.COMPLETED,
            )
        )
        Appointment.objects.create(
            patient=self.patient,
            clinician=self.clinician,
            department=self.department,
            hospital=self.hospital,
            scheduled_at=self.now,
            status=Appointment.Status.SCHEDULED,
        )
        self.encounter = Encounter.objects.create(
            encounter_number="E-REPORT-001",
            patient=self.patient,
            appointment=self.completed_appointment,
            department=self.department,
            hospital=self.hospital,
            attending_clinician=self.clinician,
            registered_by=self.user,
            encounter_type=(
                Encounter.EncounterType.OUTPATIENT
            ),
            status=Encounter.Status.COMPLETED,
            completed_at=self.now,
        )
        clinical_record = ClinicalRecord.objects.create(
            encounter=self.encounter,
            clinician=self.clinician,
        )
        prescription = Prescription.objects.create(
            encounter=self.encounter,
            clinical_record=clinical_record,
            clinician=self.clinician,
            status=Prescription.Status.ACTIVE,
            prescribed_at=self.now,
        )
        PrescriptionItem.objects.create(
            prescription=prescription,
            medicine_name="Aspirin",
            dosage="100.0000",
            dose_unit="mg",
            frequency="하루 1회",
            start_date=self.now.date(),
        )
        ct_case = CTCase.objects.create(
            encounter=self.encounter,
            input_uri="gs://bucket/report-case.dcm",
            input_sha256="a" * 64,
            file_size_bytes=1024,
            created_by=self.user,
        )
        InferenceJob.objects.create(
            case=ct_case,
            requested_by=self.user,
        )
        self.client.force_authenticate(user=self.user)

    def report_url(self) -> str:
        start_date = (
            self.now.date() - timedelta(days=1)
        )
        end_date = (
            self.now.date() + timedelta(days=1)
        )

        return (
            "/api/v1/reports/clinician-summary/"
            f"?start_date={start_date}"
            f"&end_date={end_date}"
        )

    def detail_url(
        self,
        detail_type: str,
        extra: str = "",
    ) -> str:
        start_date = (
            self.now.date() - timedelta(days=1)
        )
        end_date = (
            self.now.date() + timedelta(days=1)
        )

        return (
            "/api/v1/reports/clinician-details/"
            f"?type={detail_type}"
            f"&start_date={start_date}"
            f"&end_date={end_date}"
            f"{extra}"
        )

    def test_returns_logged_in_clinician_summary(
        self,
    ) -> None:
        response = self.client.get(
            self.report_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        data = response.data["data"]
        self.assertEqual(
            data["clinician"]["clinician_id"],
            str(self.clinician.id),
        )
        self.assertEqual(
            data["summary"]["patient_count"],
            1,
        )
        self.assertEqual(
            data["summary"][
                "appointment_completion_rate"
            ],
            50.0,
        )
        self.assertEqual(
            data["summary"]["prescription_count"],
            1,
        )
        self.assertEqual(
            data["summary"]["ct_analysis_count"],
            1,
        )
        self.assertEqual(
            data["top_medicines"][0],
            {
                "medicine_name": "Aspirin",
                "count": 1,
            },
        )

    def test_excludes_other_clinicians_data(self) -> None:
        other_user = User.objects.create_user(
            username="445566",
            password="test-password",
            role=User.Role.CLINICIAN,
        )
        other_clinician = Clinician.objects.create(
            user=other_user,
            name="Other Report Clinician",
            license_number="445566",
            hospital=self.hospital,
            department=self.department,
            approval_status=(
                Clinician.ApprovalStatus.APPROVED
            ),
        )
        Appointment.objects.create(
            patient=self.patient,
            clinician=other_clinician,
            department=self.department,
            hospital=self.hospital,
            scheduled_at=self.now,
            status=Appointment.Status.COMPLETED,
        )

        response = self.client.get(
            self.report_url(),
        )

        appointment_statuses = {
            item["status"]: item["count"]
            for item in response.data["data"][
                "appointment_statuses"
            ]
        }
        self.assertEqual(
            appointment_statuses[
                Appointment.Status.COMPLETED
            ],
            1,
        )

    def test_rejects_period_longer_than_one_year(
        self,
    ) -> None:
        response = self.client.get(
            (
                "/api/v1/reports/clinician-summary/"
                "?start_date=2025-01-01"
                "&end_date=2026-12-31"
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_returns_each_detail_type(self) -> None:
        expected = {
            "encounters": (
                str(self.encounter.id),
                "E-REPORT-001",
            ),
            "appointments": (
                str(self.completed_appointment.id),
                None,
            ),
            "prescriptions": (
                str(
                    Prescription.objects.get().id
                ),
                "E-REPORT-001",
            ),
            "ct_analyses": (
                str(CTCase.objects.get().id),
                None,
            ),
        }

        for detail_type, (
            record_id,
            reference,
        ) in expected.items():
            with self.subTest(detail_type=detail_type):
                response = self.client.get(
                    self.detail_url(detail_type),
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                )
                self.assertGreaterEqual(
                    response.data["meta"][
                        "total_count"
                    ],
                    1,
                )
                item = next(
                    row
                    for row in response.data["data"]
                    if row["record_id"] == record_id
                )
                self.assertEqual(
                    item["patient_id"],
                    str(self.patient.id),
                )
                if reference:
                    self.assertEqual(
                        item["reference"],
                        reference,
                    )

    def test_detail_filters_status_and_medicine(
        self,
    ) -> None:
        appointment_response = self.client.get(
            self.detail_url(
                "appointments",
                "&status=COMPLETED",
            ),
        )
        prescription_response = self.client.get(
            self.detail_url(
                "prescriptions",
                "&medicine=Aspirin",
            ),
        )

        self.assertEqual(
            appointment_response.data["meta"][
                "total_count"
            ],
            1,
        )
        self.assertEqual(
            prescription_response.data["meta"][
                "total_count"
            ],
            1,
        )
        self.assertEqual(
            prescription_response.data["data"][0]
            ["details"]["items"][0]
            ["medicine_name"],
            "Aspirin",
        )

    def test_ct_retry_is_one_detail_row(self) -> None:
        InferenceJob.objects.create(
            case=CTCase.objects.get(),
            requested_by=self.user,
        )

        response = self.client.get(
            self.detail_url("ct_analyses"),
        )

        self.assertEqual(
            response.data["meta"]["total_count"],
            1,
        )
