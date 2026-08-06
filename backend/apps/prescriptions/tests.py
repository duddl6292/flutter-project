from datetime import date
from uuid import uuid4

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.appointments.models import Encounter
from apps.clinical_records.models import ClinicalRecord
from apps.clinicians.models import Clinician, Department
from apps.hospitals.models import Hospital
from apps.patients.models import Patient

from .models import Prescription


class ClinicianPrescriptionApiTests(APITestCase):
    def setUp(self) -> None:
        self.hospital = Hospital.objects.create(
            hospital_code="PRESCRIPTION-HOSPITAL",
            name="Prescription Hospital",
            is_active=True,
        )
        self.department = Department.objects.create(
            code="PRESCRIPTION_RADIOLOGY",
            name="Prescription Radiology",
            is_active=True,
        )
        self.user = User.objects.create_user(
            username="135790",
            password="test-password",
            role=User.Role.CLINICIAN,
        )
        self.clinician = Clinician.objects.create(
            user=self.user,
            name="Prescription Clinician",
            license_number="135790",
            hospital=self.hospital,
            department=self.department,
            approval_status=(
                Clinician.ApprovalStatus.APPROVED
            ),
        )
        self.patient = Patient.objects.create(
            medical_record_number="P-PRESCRIPTION-001",
            name="Prescription Patient",
            status=Patient.Status.ACTIVE,
        )
        self.encounter = Encounter.objects.create(
            encounter_number="E-PRESCRIPTION-001",
            patient=self.patient,
            department=self.department,
            hospital=self.hospital,
            attending_clinician=self.clinician,
            registered_by=self.user,
            encounter_type=(
                Encounter.EncounterType.OUTPATIENT
            ),
            status=Encounter.Status.IN_PROGRESS,
        )
        self.clinical_record = (
            ClinicalRecord.objects.create(
                encounter=self.encounter,
                clinician=self.clinician,
                assessment="Test assessment",
                plan="Test plan",
            )
        )
        self.client.force_authenticate(
            user=self.user,
        )

    def create_data(self):
        return {
            "clinical_record_id": str(
                self.clinical_record.id
            ),
            "status": Prescription.Status.ACTIVE,
            "notes": "Take after meals",
            "items": [
                {
                    "medicine_name": "Aspirin",
                    "dosage": "100.0000",
                    "dose_unit": "mg",
                    "frequency": "하루 1회",
                    "route": "경구",
                    "instructions": "아침 식후 복용",
                    "start_date": str(date.today()),
                    "end_date": None,
                },
            ],
        }

    def test_lists_prescription_contexts(self) -> None:
        response = self.client.get(
            "/api/v1/prescriptions/contexts/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["data"][0][
                "clinical_record_id"
            ],
            str(self.clinical_record.id),
        )

    def test_creates_prescription_with_items(self) -> None:
        response = self.client.post(
            "/api/v1/prescriptions/",
            self.create_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        prescription = Prescription.objects.get()
        self.assertEqual(
            prescription.clinician,
            self.clinician,
        )
        self.assertEqual(
            prescription.encounter,
            self.encounter,
        )
        self.assertEqual(
            prescription.items.count(),
            1,
        )
        self.assertEqual(
            response.data["data"]["patient_name"],
            self.patient.name,
        )

    def test_lists_only_current_clinician_prescriptions(
        self,
    ) -> None:
        create_response = self.client.post(
            "/api/v1/prescriptions/",
            self.create_data(),
            format="json",
        )

        response = self.client.get(
            "/api/v1/prescriptions/?search=Prescription",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["meta"]["total_count"],
            1,
        )
        self.assertEqual(
            response.data["data"][0][
                "prescription_id"
            ],
            create_response.data["data"][
                "prescription_id"
            ],
        )

    def test_list_filters_by_patient_id(self) -> None:
        self.client.post(
            "/api/v1/prescriptions/",
            self.create_data(),
            format="json",
        )

        own_response = self.client.get(
            "/api/v1/prescriptions/",
            {"patient_id": str(self.patient.id)},
        )
        other_response = self.client.get(
            "/api/v1/prescriptions/",
            {"patient_id": str(uuid4())},
        )

        self.assertEqual(own_response.data["meta"]["total_count"], 1)
        self.assertEqual(other_response.data["meta"]["total_count"], 0)

    def test_discontinues_active_prescription(self) -> None:
        create_response = self.client.post(
            "/api/v1/prescriptions/",
            self.create_data(),
            format="json",
        )
        prescription_id = (
            create_response.data["data"][
                "prescription_id"
            ]
        )

        response = self.client.patch(
            (
                f"/api/v1/prescriptions/"
                f"{prescription_id}/status/"
            ),
            {
                "status": (
                    Prescription.Status.DISCONTINUED
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        prescription = Prescription.objects.get(
            id=prescription_id,
        )
        self.assertEqual(
            prescription.status,
            Prescription.Status.DISCONTINUED,
        )
        self.assertIsNotNone(
            prescription.discontinued_at,
        )

    def test_rejects_another_clinicians_record(self) -> None:
        other_user = User.objects.create_user(
            username="246801",
            password="test-password",
            role=User.Role.CLINICIAN,
        )
        other_clinician = Clinician.objects.create(
            user=other_user,
            name="Other Clinician",
            license_number="246801",
            hospital=self.hospital,
            department=self.department,
            approval_status=(
                Clinician.ApprovalStatus.APPROVED
            ),
        )
        other_encounter = Encounter.objects.create(
            encounter_number="E-PRESCRIPTION-002",
            patient=self.patient,
            department=self.department,
            hospital=self.hospital,
            attending_clinician=other_clinician,
            registered_by=other_user,
            encounter_type=(
                Encounter.EncounterType.OUTPATIENT
            ),
            status=Encounter.Status.IN_PROGRESS,
        )
        other_record = ClinicalRecord.objects.create(
            encounter=other_encounter,
            clinician=other_clinician,
        )
        data = self.create_data()
        data["clinical_record_id"] = str(
            other_record.id
        )

        response = self.client.post(
            "/api/v1/prescriptions/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
