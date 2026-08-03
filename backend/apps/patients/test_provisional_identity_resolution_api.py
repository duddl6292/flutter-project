from datetime import date
from unittest import skipUnless
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError, connection, transaction
from django.test import TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.appointments.models import Encounter
from apps.clinicians.models import Clinician, Department
from apps.hospitals.models import Hospital

from .models import (
    Patient,
    PatientIdentityResolutionLog,
    ProvisionalIdentity,
)
from .services import resolve_to_new_patient


User = get_user_model()


class IdentityResolutionFixtureMixin:
    PASSWORD = "BrainOn-Test-2026!"

    def create_base_objects(self) -> None:
        self.hospital = Hospital.objects.create(
            hospital_code="RESOLVE-H001",
            name="BrainOn 신원확인 테스트병원",
            address="대전광역시 서구 테스트로 15",
            phone="042-000-1515",
            is_active=True,
        )

        self.department = Department.objects.create(
            code="RESOLVE-ER",
            name="응급의학과",
            is_active=True,
        )

        self.clinician_user = User.objects.create_user(
            username="993001",
            password=self.PASSWORD,
            role=User.Role.CLINICIAN,
            is_active=True,
        )

        self.clinician = Clinician.objects.create(
            user=self.clinician_user,
            name="신원확인의",
            license_number="993001",
            hospital=self.hospital,
            department=self.department,
            approval_status=Clinician.ApprovalStatus.APPROVED,
            approved_at=timezone.now(),
        )

        self.target_patient = Patient.objects.create(
            user=None,
            medical_record_number="RESOLVE-P000001",
            name="기존환자",
            birth_date=date(1965, 2, 10),
            sex=Patient.Sex.MALE,
            phone="010-1111-2222",
            status=Patient.Status.ACTIVE,
        )

    def create_provisional_identity(
        self,
        *,
        suffix: str,
        status_value: str = ProvisionalIdentity.Status.UNIDENTIFIED,
        resolved_patient: Patient | None = None,
        create_encounter: bool = True,
    ) -> tuple[ProvisionalIdentity, Encounter | None]:
        resolved_at = None
        resolved_by = None

        if status_value == ProvisionalIdentity.Status.RESOLVED:
            if resolved_patient is None:
                resolved_patient = self.target_patient

            resolved_at = timezone.now()
            resolved_by = self.clinician

        provisional_identity = ProvisionalIdentity.objects.create(
            temporary_number=f"TEMP-RESOLVE-{suffix}",
            temporary_name=f"신원미상-{suffix}",
            estimated_sex=(
                ProvisionalIdentity.EstimatedSex.MALE
            ),
            estimated_age=60,
            distinguishing_features="검은색 상의 착용",
            status=status_value,
            resolved_patient=resolved_patient,
            resolved_at=resolved_at,
            resolved_by=resolved_by,
        )

        encounter = None

        if create_encounter:
            encounter = Encounter.objects.create(
                encounter_number=f"ENC-RESOLVE-{suffix}",
                patient=None,
                provisional_identity=provisional_identity,
                appointment=None,
                department=self.department,
                hospital=self.hospital,
                attending_clinician=self.clinician,
                registered_by=self.clinician_user,
                encounter_type=(
                    Encounter.EncounterType.EMERGENCY
                ),
                status=Encounter.Status.REGISTERED,
            )

        return provisional_identity, encounter


class ProvisionalIdentityResolveApiTests(
    IdentityResolutionFixtureMixin,
    APITestCase,
):
    def setUp(self):
        self.create_base_objects()
        self.client.force_authenticate(
            user=self.clinician_user,
        )

    def resolve_url(
        self,
        provisional_identity_id,
    ) -> str:
        return reverse(
            (
                "provisional-identities:"
                "provisional-identity-resolve"
            ),
            kwargs={
                "provisional_identity_id": (
                    provisional_identity_id
                ),
            },
        )

    def test_existing_patient_chart_merge_succeeds(self):
        provisional_identity, encounter = (
            self.create_provisional_identity(
                suffix="API-EXISTING",
            )
        )

        response = self.client.post(
            self.resolve_url(provisional_identity.id),
            {
                "resolution_type": (
                    PatientIdentityResolutionLog
                    .ResolutionType.EXISTING_PATIENT
                ),
                "target_patient_id": str(
                    self.target_patient.id
                ),
                "note": "보호자 확인 및 신분증 대조 완료",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        self.assertFalse(
            ProvisionalIdentity.objects.filter(
                id=provisional_identity.id,
            ).exists()
        )

        encounter.refresh_from_db()

        self.assertEqual(
            encounter.patient_id,
            self.target_patient.id,
        )
        self.assertIsNone(
            encounter.provisional_identity_id
        )

        resolution_log = (
            PatientIdentityResolutionLog.objects.get(
                provisional_identity_uuid=(
                    provisional_identity.id
                ),
            )
        )

        self.assertEqual(
            resolution_log.resolution_type,
            (
                PatientIdentityResolutionLog
                .ResolutionType.EXISTING_PATIENT
            ),
        )
        self.assertEqual(
            resolution_log.target_patient_id,
            self.target_patient.id,
        )
        self.assertEqual(
            resolution_log.moved_encounter_count,
            1,
        )
        self.assertEqual(
            resolution_log.moved_encounter_ids,
            [str(encounter.id)],
        )
        self.assertIsNotNone(
            resolution_log.provisional_deleted_at
        )
        self.assertTrue(
            resolution_log.deletion_snapshot
        )

        self.assertEqual(
            response.data["data"][
                "moved_encounter_count"
            ],
            1,
        )
        self.assertTrue(
            response.data["data"][
                "resolution_log"
            ]["deletion_snapshot_saved"]
        )

    def test_new_patient_chart_creation_succeeds(self):
        provisional_identity, encounter = (
            self.create_provisional_identity(
                suffix="API-NEW",
            )
        )

        response = self.client.post(
            self.resolve_url(provisional_identity.id),
            {
                "resolution_type": (
                    PatientIdentityResolutionLog
                    .ResolutionType.NEW_PATIENT
                ),
                "new_patient": {
                    "medical_record_number": (
                        "RESOLVE-P000002"
                    ),
                    "name": "신규확인환자",
                    "birth_date": "1970-07-15",
                    "sex": Patient.Sex.FEMALE,
                    "phone": "010-3333-4444",
                    "emergency_contact": (
                        "010-5555-6666"
                    ),
                    "address": "대전광역시 유성구",
                },
                "note": (
                    "신원확인 완료 후 신규 환자번호 발급"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        new_patient = Patient.objects.get(
            medical_record_number="RESOLVE-P000002",
        )

        self.assertIsNone(new_patient.user_id)
        self.assertEqual(
            new_patient.name,
            "신규확인환자",
        )
        self.assertEqual(
            new_patient.status,
            Patient.Status.ACTIVE,
        )

        encounter.refresh_from_db()

        self.assertEqual(
            encounter.patient_id,
            new_patient.id,
        )
        self.assertIsNone(
            encounter.provisional_identity_id
        )
        self.assertFalse(
            ProvisionalIdentity.objects.filter(
                id=provisional_identity.id,
            ).exists()
        )

        resolution_log = (
            PatientIdentityResolutionLog.objects.get(
                provisional_identity_uuid=(
                    provisional_identity.id
                ),
            )
        )

        self.assertEqual(
            resolution_log.resolution_type,
            (
                PatientIdentityResolutionLog
                .ResolutionType.NEW_PATIENT
            ),
        )
        self.assertEqual(
            resolution_log.target_patient_id,
            new_patient.id,
        )
        self.assertIsNotNone(
            resolution_log.provisional_deleted_at
        )
        self.assertTrue(
            resolution_log.deletion_snapshot
        )


@skipUnless(
    connection.vendor == "postgresql",
    "PostgreSQL 전용 트리거 테스트",
)
class ProvisionalIdentityChartTriggerTests(
    IdentityResolutionFixtureMixin,
    TransactionTestCase,
):
    reset_sequences = True

    def setUp(self):
        self.create_base_objects()

    def raw_delete(self, provisional_identity_id) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                (
                    "DELETE FROM provisional_identities "
                    "WHERE id = %s"
                ),
                [provisional_identity_id],
            )

    def test_trigger_blocks_unresolved_identity_delete(self):
        provisional_identity, _encounter = (
            self.create_provisional_identity(
                suffix="TRIGGER-UNRESOLVED",
                create_encounter=False,
            )
        )

        with self.assertRaises(IntegrityError) as caught:
            with transaction.atomic():
                self.raw_delete(
                    provisional_identity.id
                )

        self.assertIn(
            "신원확인이 완료되지 않은 임시 신원",
            str(caught.exception),
        )
        self.assertTrue(
            ProvisionalIdentity.objects.filter(
                id=provisional_identity.id,
            ).exists()
        )

    def test_trigger_blocks_delete_with_encounter(self):
        provisional_identity, encounter = (
            self.create_provisional_identity(
                suffix="TRIGGER-ENCOUNTER",
                status_value=(
                    ProvisionalIdentity.Status.RESOLVED
                ),
                resolved_patient=self.target_patient,
                create_encounter=True,
            )
        )

        with self.assertRaises(IntegrityError) as caught:
            with transaction.atomic():
                self.raw_delete(
                    provisional_identity.id
                )

        self.assertIn(
            "연결된 진료 건이 남아 있는 임시 신원",
            str(caught.exception),
        )
        self.assertTrue(
            ProvisionalIdentity.objects.filter(
                id=provisional_identity.id,
            ).exists()
        )
        self.assertTrue(
            Encounter.objects.filter(
                id=encounter.id,
                provisional_identity=(
                    provisional_identity
                ),
            ).exists()
        )

    def test_trigger_blocks_delete_without_resolution_log(
        self,
    ):
        provisional_identity, _encounter = (
            self.create_provisional_identity(
                suffix="TRIGGER-NOLOG",
                status_value=(
                    ProvisionalIdentity.Status.RESOLVED
                ),
                resolved_patient=self.target_patient,
                create_encounter=False,
            )
        )

        with self.assertRaises(IntegrityError) as caught:
            with transaction.atomic():
                self.raw_delete(
                    provisional_identity.id
                )

        self.assertIn(
            "신원확인 처리 로그가 없는 임시 신원",
            str(caught.exception),
        )
        self.assertTrue(
            ProvisionalIdentity.objects.filter(
                id=provisional_identity.id,
            ).exists()
        )


class IdentityResolutionRollbackTests(
    IdentityResolutionFixtureMixin,
    TransactionTestCase,
):
    reset_sequences = True

    def setUp(self):
        self.create_base_objects()

    def test_new_patient_resolution_rolls_back_completely(
        self,
    ):
        provisional_identity, encounter = (
            self.create_provisional_identity(
                suffix="ROLLBACK",
            )
        )

        patient_count_before = Patient.objects.count()

        with patch(
            (
                "apps.patients.services."
                "PatientIdentityResolutionLog."
                "objects.create"
            ),
            side_effect=RuntimeError(
                "강제 로그 생성 실패"
            ),
        ):
            with self.assertRaises(RuntimeError):
                resolve_to_new_patient(
                    provisional_identity_id=(
                        provisional_identity.id
                    ),
                    new_patient_data={
                        "medical_record_number": (
                            "RESOLVE-ROLLBACK-001"
                        ),
                        "name": "롤백환자",
                        "birth_date": date(
                            1980,
                            1,
                            1,
                        ),
                        "sex": Patient.Sex.MALE,
                        "phone": "010-7777-8888",
                    },
                    resolved_by=self.clinician,
                    note="전체 롤백 검증",
                )

        self.assertEqual(
            Patient.objects.count(),
            patient_count_before,
        )
        self.assertFalse(
            Patient.objects.filter(
                medical_record_number=(
                    "RESOLVE-ROLLBACK-001"
                ),
            ).exists()
        )

        provisional_identity.refresh_from_db()
        encounter.refresh_from_db()

        self.assertEqual(
            provisional_identity.status,
            ProvisionalIdentity.Status.UNIDENTIFIED,
        )
        self.assertIsNone(
            provisional_identity.resolved_patient_id
        )
        self.assertIsNone(
            provisional_identity.resolved_at
        )
        self.assertIsNone(
            provisional_identity.resolved_by_id
        )

        self.assertIsNone(encounter.patient_id)
        self.assertEqual(
            encounter.provisional_identity_id,
            provisional_identity.id,
        )

        self.assertFalse(
            PatientIdentityResolutionLog.objects.filter(
                provisional_identity_uuid=(
                    provisional_identity.id
                ),
            ).exists()
        )
