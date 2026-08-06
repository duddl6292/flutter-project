from datetime import datetime, time, timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.appointments.models import Appointment
from apps.diagnostics.models import Examination, ExaminationCatalog
from apps.hospitals.models import Hospital
from apps.patients.models import Patient

from ..models import Clinician, Department


class ClinicianDashboardApiTests(APITestCase):
    def setUp(self) -> None:
        self.hospital = Hospital.objects.create(
            hospital_code="DASHBOARD-HOSPITAL",
            name="Dashboard Hospital",
            is_active=True,
        )
        self.department = Department.objects.create(
            code="DASHBOARD-NEURO",
            name="Dashboard Neurology",
            is_active=True,
        )
        self.user = User.objects.create_user(
            username="dashboard-clinician",
            password="test-password",
            role=User.Role.CLINICIAN,
        )
        self.clinician = Clinician.objects.create(
            user=self.user,
            name="Dashboard Clinician",
            license_number="770001",
            hospital=self.hospital,
            department=self.department,
            approval_status=Clinician.ApprovalStatus.APPROVED,
        )
        self.other_user = User.objects.create_user(
            username="dashboard-other-clinician",
            password="test-password",
            role=User.Role.CLINICIAN,
        )
        self.other_clinician = Clinician.objects.create(
            user=self.other_user,
            name="Other Clinician",
            license_number="770002",
            hospital=self.hospital,
            department=self.department,
            approval_status=Clinician.ApprovalStatus.APPROVED,
        )
        self.first_patient = Patient.objects.create(
            medical_record_number="DASH-P-001",
            name="First Patient",
            birth_date=timezone.localdate().replace(year=1990),
            sex=Patient.Sex.FEMALE,
        )
        self.second_patient = Patient.objects.create(
            medical_record_number="DASH-P-002",
            name="Second Patient",
            birth_date=timezone.localdate().replace(year=1980),
            sex=Patient.Sex.MALE,
        )
        self.selected_date = timezone.localdate() + timedelta(days=3)
        self.client.force_authenticate(user=self.user)

    def aware_at(self, hour: int):
        return timezone.make_aware(
            datetime.combine(self.selected_date, time(hour=hour)),
            timezone.get_current_timezone(),
        )

    def create_appointment(
        self,
        *,
        patient,
        clinician=None,
        scheduled_at=None,
        appointment_status=Appointment.Status.SCHEDULED,
    ):
        assigned_clinician = clinician or self.clinician
        return Appointment.objects.create(
            patient=patient,
            clinician=assigned_clinician,
            department=self.department,
            hospital=self.hospital,
            created_by=assigned_clinician.user,
            scheduled_at=scheduled_at or self.aware_at(9),
            status=appointment_status,
            location="진료실 1",
        )

    def test_dashboard_uses_selected_date_and_current_clinician(self):
        self.create_appointment(patient=self.first_patient)
        self.create_appointment(
            patient=self.second_patient,
            scheduled_at=self.aware_at(10),
            appointment_status=Appointment.Status.CONFIRMED,
        )
        self.create_appointment(
            patient=self.first_patient,
            scheduled_at=self.aware_at(9) + timedelta(days=1),
        )
        self.create_appointment(
            patient=self.first_patient,
            clinician=self.other_clinician,
            scheduled_at=self.aware_at(11),
        )

        Examination.objects.create(
            patient=self.first_patient,
            hospital=self.hospital,
            ordered_by=self.clinician,
            test_code="DASH-PROCESSING",
            test_name="Processing examination",
            category=ExaminationCatalog.Category.LABORATORY,
            status=Examination.Status.IN_PROGRESS,
            performed_at=self.aware_at(9),
        )
        Examination.objects.create(
            patient=self.second_patient,
            hospital=self.hospital,
            ordered_by=self.clinician,
            test_code="DASH-WAITING",
            test_name="Preliminary examination",
            category=ExaminationCatalog.Category.LABORATORY,
            status=Examination.Status.PRELIMINARY,
            performed_at=self.aware_at(10),
        )

        response = self.client.get(
            "/api/v1/clinicians/clinicians/me/dashboard",
            {"date": self.selected_date.isoformat()},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data["data"]
        self.assertEqual(
            data["summary"]["appointments"],
            {"total": 2, "confirmed": 1, "waiting": 1},
        )
        self.assertEqual(len(data["patients"]), 2)
        self.assertEqual(
            {
                patient["patient_number"]
                for patient in data["patients"]
            },
            {"DASH-P-001", "DASH-P-002"},
        )
        self.assertEqual(len(data["schedules"]), 2)
        self.assertEqual(
            data["summary"]["tests"],
            {"total": 2, "processing": 1, "result_waiting": 1},
        )

        next_date_response = self.client.get(
            "/api/v1/clinicians/clinicians/me/dashboard",
            {"date": (self.selected_date + timedelta(days=1)).isoformat()},
        )
        self.assertEqual(
            next_date_response.data["data"]["summary"]
            ["appointments"]["total"],
            1,
        )

    def test_dashboard_rejects_invalid_date(self):
        response = self.client.get(
            "/api/v1/clinicians/clinicians/me/dashboard",
            {"date": "06-08-2026"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date", response.data["error"]["details"])
