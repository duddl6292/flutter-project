from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.appointments.models import Appointment, Encounter
from apps.clinical_records.models import ClinicalRecord
from apps.clinicians.models import Clinician, Department
from apps.ct_analysis.models import CTCase, InferenceJob, InferenceResult
from apps.hospitals.models import Hospital, PatientFavoriteHospital
from apps.medications.models import MedicationRecord, MedicationSchedule
from apps.notifications.models import Notification
from apps.prescriptions.models import Prescription, PrescriptionItem
from apps.test_results.models import TestResult

from .models import Patient


User = get_user_model()


class PatientAppApiTests(APITestCase):
    """
    작업 사항16-1~16-4 전체 환자 앱 API 테스트.

    검증 범위:
    - 통합 진료이력
    - 예약
    - 공개 검사결과
    - 처방·처방 항목
    - 복약 일정·복약 기록
    - 환자용 CT 결과
    - 찜 병원 조회·추가·삭제
    - 알림 조회·개별 읽음·전체 읽음
    - 다른 환자 데이터 격리
    - 잘못된 필터 검증
    - 비로그인 접근 차단
    """

    def setUp(self):
        self.now = timezone.now()
        self.today = timezone.localdate()

        self.patient_user = User.objects.create_user(
            username="patient_api_a",
            password="BrainOn-Test-2026!",
            role=User.Role.PATIENT,
            is_active=True,
        )
        self.other_patient_user = User.objects.create_user(
            username="patient_api_b",
            password="BrainOn-Test-2026!",
            role=User.Role.PATIENT,
            is_active=True,
        )
        self.clinician_user = User.objects.create_user(
            username="995001",
            password="BrainOn-Test-2026!",
            role=User.Role.CLINICIAN,
            is_active=True,
        )

        self.hospital = Hospital.objects.create(
            hospital_code="PATIENT-API-H001",
            name="BrainOn 환자 API 병원",
            address="대전광역시 서구 환자로 16",
            phone="042-1600-0001",
            is_active=True,
        )
        self.second_hospital = Hospital.objects.create(
            hospital_code="PATIENT-API-H002",
            name="BrainOn 제2병원",
            address="대전광역시 유성구 환자로 22",
            phone="042-1600-0002",
            is_active=True,
        )
        self.inactive_hospital = Hospital.objects.create(
            hospital_code="PATIENT-API-H003",
            name="BrainOn 운영중지병원",
            address="대전광역시 중구 환자로 33",
            phone="042-1600-0003",
            is_active=False,
        )

        self.department = Department.objects.create(
            code="PATIENT-API-NS",
            name="신경외과",
            is_active=True,
        )
        self.clinician = Clinician.objects.create(
            user=self.clinician_user,
            name="환자API의사",
            license_number="995001",
            hospital=self.hospital,
            department=self.department,
            approval_status=Clinician.ApprovalStatus.APPROVED,
            approved_at=self.now,
        )

        self.patient = Patient.objects.create(
            user=self.patient_user,
            medical_record_number="PATIENT-API-P001",
            name="환자에이",
            birth_date=date(1965, 1, 10),
            sex=Patient.Sex.MALE,
            phone="010-1000-1000",
            status=Patient.Status.ACTIVE,
        )
        self.other_patient = Patient.objects.create(
            user=self.other_patient_user,
            medical_record_number="PATIENT-API-P002",
            name="환자비",
            birth_date=date(1970, 5, 20),
            sex=Patient.Sex.FEMALE,
            phone="010-2000-2000",
            status=Patient.Status.ACTIVE,
        )

        self.appointment = Appointment.objects.create(
            patient=self.patient,
            clinician=self.clinician,
            department=self.department,
            hospital=self.hospital,
            location="본관 2층 신경외과",
            scheduled_at=self.now + timedelta(days=3),
            reason="퇴원 후 경과 확인",
            status=Appointment.Status.SCHEDULED,
        )
        self.other_appointment = Appointment.objects.create(
            patient=self.other_patient,
            clinician=self.clinician,
            department=self.department,
            hospital=self.hospital,
            location="본관 2층 신경외과",
            scheduled_at=self.now + timedelta(days=4),
            reason="다른 환자 예약",
            status=Appointment.Status.CONFIRMED,
        )

        self.encounter = Encounter.objects.create(
            encounter_number="PATIENT-API-ENC001",
            patient=self.patient,
            provisional_identity=None,
            appointment=None,
            department=self.department,
            hospital=self.hospital,
            attending_clinician=self.clinician,
            registered_by=self.clinician_user,
            encounter_type=Encounter.EncounterType.EMERGENCY,
            status=Encounter.Status.COMPLETED,
            arrived_at=self.now - timedelta(hours=3),
            started_at=self.now - timedelta(hours=2),
            completed_at=self.now - timedelta(hours=1),
        )
        self.second_encounter = Encounter.objects.create(
            encounter_number="PATIENT-API-ENC002",
            patient=self.patient,
            provisional_identity=None,
            appointment=None,
            department=self.department,
            hospital=self.hospital,
            attending_clinician=self.clinician,
            registered_by=self.clinician_user,
            encounter_type=Encounter.EncounterType.OUTPATIENT,
            status=Encounter.Status.REGISTERED,
        )
        self.other_encounter = Encounter.objects.create(
            encounter_number="PATIENT-API-ENC003",
            patient=self.other_patient,
            provisional_identity=None,
            appointment=None,
            department=self.department,
            hospital=self.hospital,
            attending_clinician=self.clinician,
            registered_by=self.clinician_user,
            encounter_type=Encounter.EncounterType.EMERGENCY,
            status=Encounter.Status.COMPLETED,
            arrived_at=self.now - timedelta(hours=5),
            started_at=self.now - timedelta(hours=4),
            completed_at=self.now - timedelta(hours=3),
        )

        self.clinical_record = ClinicalRecord.objects.create(
            encounter=self.encounter,
            clinician=self.clinician,
            recorded_at=self.now - timedelta(minutes=50),
            chief_complaint="우측 위약",
            subjective="갑작스러운 우측 위약을 호소함",
            objective="CT 검사 시행",
            assessment="뇌혈관질환 평가 필요",
            plan="약물치료 및 추적관찰",
            patient_visible_summary=(
                "검사 후 약물치료를 시작했습니다."
            ),
        )
        self.other_clinical_record = ClinicalRecord.objects.create(
            encounter=self.other_encounter,
            clinician=self.clinician,
            recorded_at=self.now - timedelta(hours=2),
            patient_visible_summary="다른 환자 진료기록",
        )

        self.prescription = Prescription.objects.create(
            encounter=self.encounter,
            clinical_record=self.clinical_record,
            clinician=self.clinician,
            status=Prescription.Status.ACTIVE,
            notes="식후 복용",
            prescribed_at=self.now - timedelta(minutes=40),
        )
        self.draft_prescription = Prescription.objects.create(
            encounter=self.encounter,
            clinical_record=self.clinical_record,
            clinician=self.clinician,
            status=Prescription.Status.DRAFT,
            notes="환자에게 공개되면 안 되는 작성 중 처방",
            prescribed_at=self.now - timedelta(minutes=30),
        )
        self.other_prescription = Prescription.objects.create(
            encounter=self.other_encounter,
            clinical_record=self.other_clinical_record,
            clinician=self.clinician,
            status=Prescription.Status.ACTIVE,
            notes="다른 환자 처방",
            prescribed_at=self.now - timedelta(hours=2),
        )

        self.prescription_item = PrescriptionItem.objects.create(
            prescription=self.prescription,
            medicine_name="아스피린",
            dosage=Decimal("100.0000"),
            dose_unit="mg",
            frequency="1일 1회",
            route="경구",
            instructions="아침 식후 복용",
            start_date=self.today - timedelta(days=1),
            end_date=self.today + timedelta(days=30),
        )
        self.draft_prescription_item = PrescriptionItem.objects.create(
            prescription=self.draft_prescription,
            medicine_name="작성중약품",
            dosage=Decimal("1.0000"),
            dose_unit="정",
            frequency="1일 1회",
            route="경구",
            instructions="작성 중",
            start_date=self.today,
            end_date=self.today + timedelta(days=7),
        )
        self.other_prescription_item = PrescriptionItem.objects.create(
            prescription=self.other_prescription,
            medicine_name="다른환자약품",
            dosage=Decimal("20.0000"),
            dose_unit="mg",
            frequency="1일 2회",
            route="경구",
            instructions="다른 환자용",
            start_date=self.today - timedelta(days=1),
            end_date=self.today + timedelta(days=30),
        )

        self.medication_schedule = MedicationSchedule.objects.create(
            prescription_item=self.prescription_item,
            dose_time=self.now.time().replace(microsecond=0),
            days_of_week=[],
            start_date=self.today - timedelta(days=1),
            end_date=self.today + timedelta(days=30),
            is_active=True,
        )
        self.other_medication_schedule = (
            MedicationSchedule.objects.create(
                prescription_item=self.other_prescription_item,
                dose_time=self.now.time().replace(microsecond=0),
                days_of_week=[],
                start_date=self.today - timedelta(days=1),
                end_date=self.today + timedelta(days=30),
                is_active=True,
            )
        )

        self.taken_record = MedicationRecord.objects.create(
            schedule=self.medication_schedule,
            prescription_item=self.prescription_item,
            scheduled_at=self.now - timedelta(minutes=20),
            taken_at=self.now - timedelta(minutes=15),
            status=MedicationRecord.Status.TAKEN,
            note="정상 복용",
        )
        self.missed_record = MedicationRecord.objects.create(
            schedule=self.medication_schedule,
            prescription_item=self.prescription_item,
            scheduled_at=self.now - timedelta(days=1),
            taken_at=None,
            status=MedicationRecord.Status.MISSED,
            note="복용하지 않음",
        )
        self.other_medication_record = MedicationRecord.objects.create(
            schedule=self.other_medication_schedule,
            prescription_item=self.other_prescription_item,
            scheduled_at=self.now - timedelta(minutes=10),
            taken_at=None,
            status=MedicationRecord.Status.MISSED,
            note="다른 환자 복약 기록",
        )

        self.ct_case = CTCase.objects.create(
            encounter=self.encounter,
            study_type=CTCase.StudyType.NCCT,
            description="비조영 뇌 CT",
            status=CTCase.Status.COMPLETED,
            input_uri="gs://private-bucket/patient-a-input.nii.gz",
            input_sha256="a" * 64,
            file_size_bytes=1024,
            content_type="application/gzip",
            performed_at=self.now - timedelta(hours=2),
            created_by=self.clinician_user,
        )
        self.other_ct_case = CTCase.objects.create(
            encounter=self.other_encounter,
            study_type=CTCase.StudyType.NCCT,
            description="다른 환자 CT",
            status=CTCase.Status.COMPLETED,
            input_uri="gs://private-bucket/patient-b-input.nii.gz",
            input_sha256="b" * 64,
            file_size_bytes=2048,
            content_type="application/gzip",
            performed_at=self.now - timedelta(hours=4),
            created_by=self.clinician_user,
        )

        self.inference_job = InferenceJob.objects.create(
            case=self.ct_case,
            status=InferenceJob.Status.SUCCEEDED,
            progress=100,
            requested_by=self.clinician_user,
            parameters={"threshold": 0.5},
            started_at=self.now - timedelta(minutes=10),
            completed_at=self.now - timedelta(minutes=5),
        )
        self.inference_result = InferenceResult.objects.create(
            case=self.ct_case,
            job=self.inference_job,
            model_id="stroke-bhsd-nnunet-25d-exp05",
            model_version="1.0.0",
            checkpoint="checkpoint_best.pth",
            threshold=Decimal("0.50000"),
            mask_uri="gs://private-bucket/mask.nii.gz",
            preview_uri="gs://private-bucket/preview.png",
            probability_uri=(
                "gs://private-bucket/probability.nii.gz"
            ),
            entropy_uri="gs://private-bucket/entropy.nii.gz",
            uncertainty_uri=(
                "gs://private-bucket/uncertainty.nii.gz"
            ),
            xai_uri="gs://private-bucket/xai.png",
            lesion_voxels=1200,
            lesion_volume_ml=Decimal("12.500000"),
            lesion_slice_count=8,
            lesion_slice_start=10,
            lesion_slice_end=17,
            max_lesion_slice=14,
            shape=[512, 512, 40],
            spacing=[0.5, 0.5, 5.0],
            preprocessing_seconds=Decimal("1.200000"),
            inference_seconds=Decimal("2.300000"),
            postprocessing_seconds=Decimal("0.800000"),
            total_seconds=Decimal("4.300000"),
            gpu_memory_peak_mb=Decimal("2048.000"),
            raw_result={"internal_probability": 0.9876},
        )

        self.released_test_result = TestResult.objects.create(
            encounter=self.encounter,
            case=self.ct_case,
            test_type="BRAIN_CT",
            title="뇌 CT 검사 결과",
            performed_at=self.now - timedelta(hours=2),
            status=TestResult.Status.FINAL,
            summary="의료진 검토가 완료된 환자 공개 요약",
            clinician_comment="외래 추적 관찰이 필요합니다.",
            result_file_uri="gs://private-bucket/report-a.pdf",
            is_released_to_patient=True,
            released_at=self.now - timedelta(minutes=5),
            released_by=self.clinician_user,
            created_by=self.clinician_user,
        )
        self.corrected_test_result = TestResult.objects.create(
            encounter=self.encounter,
            case=self.ct_case,
            test_type="BRAIN_CT",
            title="뇌 CT 검사 결과 정정",
            performed_at=self.now - timedelta(hours=1),
            status=TestResult.Status.CORRECTED,
            summary="정정된 환자 공개 요약",
            clinician_comment="정정 사유를 확인했습니다.",
            result_file_uri=(
                "gs://private-bucket/report-a-corrected.pdf"
            ),
            is_released_to_patient=True,
            released_at=self.now - timedelta(minutes=3),
            released_by=self.clinician_user,
            created_by=self.clinician_user,
        )
        self.unreleased_test_result = TestResult.objects.create(
            encounter=self.encounter,
            case=self.ct_case,
            test_type="BRAIN_CT",
            title="아직 공개되지 않은 검사 결과",
            performed_at=self.now - timedelta(minutes=30),
            status=TestResult.Status.FINAL,
            summary="환자에게 노출되면 안 됨",
            clinician_comment="",
            result_file_uri="gs://private-bucket/unreleased.pdf",
            is_released_to_patient=False,
            released_at=None,
            released_by=None,
            created_by=self.clinician_user,
        )
        self.other_test_result = TestResult.objects.create(
            encounter=self.other_encounter,
            case=self.other_ct_case,
            test_type="BRAIN_CT",
            title="다른 환자 검사 결과",
            performed_at=self.now - timedelta(hours=4),
            status=TestResult.Status.FINAL,
            summary="다른 환자의 결과",
            clinician_comment="",
            result_file_uri="gs://private-bucket/report-b.pdf",
            is_released_to_patient=True,
            released_at=self.now - timedelta(hours=3),
            released_by=self.clinician_user,
            created_by=self.clinician_user,
        )

        self.favorite_hospital = PatientFavoriteHospital.objects.create(
            patient=self.patient,
            hospital=self.hospital,
        )
        self.other_favorite_hospital = (
            PatientFavoriteHospital.objects.create(
                patient=self.other_patient,
                hospital=self.second_hospital,
            )
        )

        self.unread_notification = Notification.objects.create(
            recipient=self.patient_user,
            type=Notification.Type.APPOINTMENT,
            title="진료 예약 안내",
            body="3일 후 예약이 있습니다.",
            data={
                "appointment_id": str(self.appointment.id),
                "route": "/appointments",
            },
            is_read=False,
            read_at=None,
            deduplication_key="patient-api-a-appointment",
        )
        self.read_notification = Notification.objects.create(
            recipient=self.patient_user,
            type=Notification.Type.TEST_RESULT,
            title="검사 결과 공개",
            body="검사 결과가 공개되었습니다.",
            data={
                "test_result_id": str(
                    self.released_test_result.id
                ),
                "route": "/test-results",
            },
            is_read=True,
            read_at=self.now - timedelta(minutes=2),
            deduplication_key="patient-api-a-test-result",
        )
        self.other_notification = Notification.objects.create(
            recipient=self.other_patient_user,
            type=Notification.Type.SYSTEM,
            title="다른 환자 알림",
            body="다른 환자에게만 보여야 합니다.",
            data={},
            is_read=False,
            read_at=None,
            deduplication_key="patient-api-b-system",
        )

        self.client.force_authenticate(user=self.patient_user)

    def list_ids(self, response, field_name):
        return {
            item[field_name]
            for item in response.data["data"]
        }

    def test_unauthenticated_patient_api_access_is_blocked(self):
        self.client.force_authenticate(user=None)

        urls = [
            reverse("patients:patient-medical-history"),
            reverse("patients:patient-appointment-list"),
            reverse("patients:patient-test-result-list"),
            reverse("patients:patient-prescription-list"),
            reverse(
                "patients:patient-medication-schedule-list"
            ),
            reverse("patients:patient-medication-record-list"),
            reverse("patients:patient-ct-result-list"),
            reverse(
                "patients:"
                "patient-favorite-hospital-list-create"
            ),
            reverse("patients:patient-notification-list"),
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertIn(
                response.status_code,
                {
                    status.HTTP_401_UNAUTHORIZED,
                    status.HTTP_403_FORBIDDEN,
                },
                response.data,
            )

    def test_medical_history_returns_only_login_patient(self):
        response = self.client.get(
            reverse("patients:patient-medical-history")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )
        encounter_ids = self.list_ids(response, "encounter_id")
        self.assertEqual(
            encounter_ids,
            {
                str(self.encounter.id),
                str(self.second_encounter.id),
            },
        )
        self.assertNotIn(
            str(self.other_encounter.id),
            encounter_ids,
        )

    def test_medical_history_filters_type_and_status(self):
        response = self.client.get(
            reverse("patients:patient-medical-history"),
            {
                "encounter_type": (
                    Encounter.EncounterType.EMERGENCY
                ),
                "status": Encounter.Status.COMPLETED,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )
        self.assertEqual(
            self.list_ids(response, "encounter_id"),
            {str(self.encounter.id)},
        )

    def test_appointments_return_only_login_patient(self):
        response = self.client.get(
            reverse("patients:patient-appointment-list"),
            {"status": Appointment.Status.SCHEDULED},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )
        self.assertEqual(
            self.list_ids(response, "appointment_id"),
            {str(self.appointment.id)},
        )
        self.assertNotIn(
            str(self.other_appointment.id),
            self.list_ids(response, "appointment_id"),
        )

    def test_released_test_results_exclude_hidden_data(self):
        response = self.client.get(
            reverse("patients:patient-test-result-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )
        result_ids = self.list_ids(response, "test_result_id")
        self.assertEqual(
            result_ids,
            {
                str(self.released_test_result.id),
                str(self.corrected_test_result.id),
            },
        )
        self.assertNotIn(
            str(self.unreleased_test_result.id),
            result_ids,
        )
        self.assertNotIn(
            str(self.other_test_result.id),
            result_ids,
        )

    def test_prescriptions_exclude_draft_and_other_patient(self):
        response = self.client.get(
            reverse("patients:patient-prescription-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )
        prescription_ids = self.list_ids(
            response,
            "prescription_id",
        )
        self.assertEqual(
            prescription_ids,
            {str(self.prescription.id)},
        )
        self.assertNotIn(
            str(self.draft_prescription.id),
            prescription_ids,
        )
        self.assertNotIn(
            str(self.other_prescription.id),
            prescription_ids,
        )

        item_ids = {
            item["prescription_item_id"]
            for item in response.data["data"][0]["items"]
        }
        self.assertEqual(
            item_ids,
            {str(self.prescription_item.id)},
        )

    def test_medication_schedules_return_only_login_patient(self):
        response = self.client.get(
            reverse(
                "patients:patient-medication-schedule-list"
            ),
            {"active": "true"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )
        self.assertEqual(
            self.list_ids(response, "schedule_id"),
            {str(self.medication_schedule.id)},
        )
        self.assertNotIn(
            str(self.other_medication_schedule.id),
            self.list_ids(response, "schedule_id"),
        )

    def test_medication_records_filter_status_and_owner(self):
        response = self.client.get(
            reverse("patients:patient-medication-record-list"),
            {"status": MedicationRecord.Status.TAKEN},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )
        self.assertEqual(
            self.list_ids(response, "medication_record_id"),
            {str(self.taken_record.id)},
        )
        self.assertNotIn(
            str(self.missed_record.id),
            self.list_ids(response, "medication_record_id"),
        )
        self.assertNotIn(
            str(self.other_medication_record.id),
            self.list_ids(response, "medication_record_id"),
        )

    def test_ct_results_only_expose_patient_safe_fields(self):
        response = self.client.get(
            reverse("patients:patient-ct-result-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )
        result_ids = self.list_ids(response, "test_result_id")
        self.assertEqual(
            result_ids,
            {
                str(self.released_test_result.id),
                str(self.corrected_test_result.id),
            },
        )

        forbidden_fields = {
            "input_uri",
            "input_sha256",
            "result_file_uri",
            "mask_uri",
            "preview_uri",
            "probability_uri",
            "entropy_uri",
            "uncertainty_uri",
            "xai_uri",
            "raw_result",
            "model_id",
            "model_version",
            "gpu_memory_peak_mb",
        }

        for item in response.data["data"]:
            self.assertTrue(
                forbidden_fields.isdisjoint(item.keys())
            )

    def test_invalid_query_filters_return_400(self):
        checks = [
            (
                reverse("patients:patient-medical-history"),
                {"encounter_type": "INVALID"},
            ),
            (
                reverse("patients:patient-appointment-list"),
                {"status": "INVALID"},
            ),
            (
                reverse(
                    "patients:patient-medication-schedule-list"
                ),
                {"active": "yes"},
            ),
            (
                reverse(
                    "patients:patient-medication-record-list"
                ),
                {"status": "INVALID"},
            ),
            (
                reverse("patients:patient-notification-list"),
                {"read": "yes"},
            ),
            (
                reverse("patients:patient-notification-list"),
                {"type": "INVALID"},
            ),
        ]

        for url, query in checks:
            response = self.client.get(url, query)
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                response.data,
            )

    def test_favorite_hospital_list_returns_only_login_patient(
        self,
    ):
        response = self.client.get(
            reverse(
                "patients:"
                "patient-favorite-hospital-list-create"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )
        self.assertEqual(
            self.list_ids(response, "hospital_id"),
            {str(self.hospital.id)},
        )
        self.assertNotIn(
            str(self.second_hospital.id),
            self.list_ids(response, "hospital_id"),
        )

    def test_favorite_hospital_add_succeeds(self):
        response = self.client.post(
            reverse(
                "patients:"
                "patient-favorite-hospital-list-create"
            ),
            {"hospital_id": str(self.second_hospital.id)},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )
        self.assertTrue(
            PatientFavoriteHospital.objects.filter(
                patient=self.patient,
                hospital=self.second_hospital,
            ).exists()
        )

    def test_favorite_hospital_duplicate_and_inactive_blocked(
        self,
    ):
        duplicate_response = self.client.post(
            reverse(
                "patients:"
                "patient-favorite-hospital-list-create"
            ),
            {"hospital_id": str(self.hospital.id)},
            format="json",
        )
        self.assertEqual(
            duplicate_response.status_code,
            status.HTTP_400_BAD_REQUEST,
            duplicate_response.data,
        )

        inactive_response = self.client.post(
            reverse(
                "patients:"
                "patient-favorite-hospital-list-create"
            ),
            {"hospital_id": str(self.inactive_hospital.id)},
            format="json",
        )
        self.assertEqual(
            inactive_response.status_code,
            status.HTTP_400_BAD_REQUEST,
            inactive_response.data,
        )

    def test_favorite_hospital_delete_removes_only_relation(self):
        response = self.client.delete(
            reverse(
                "patients:patient-favorite-hospital-delete",
                kwargs={"hospital_id": self.hospital.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            PatientFavoriteHospital.objects.filter(
                patient=self.patient,
                hospital=self.hospital,
            ).exists()
        )
        self.assertTrue(
            Hospital.objects.filter(id=self.hospital.id).exists()
        )

    def test_cannot_delete_other_patient_favorite_relation(self):
        response = self.client.delete(
            reverse(
                "patients:patient-favorite-hospital-delete",
                kwargs={
                    "hospital_id": self.second_hospital.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            response.data,
        )
        self.assertTrue(
            PatientFavoriteHospital.objects.filter(
                patient=self.other_patient,
                hospital=self.second_hospital,
            ).exists()
        )

    def test_notification_list_owner_filter_and_unread_count(self):
        response = self.client.get(
            reverse("patients:patient-notification-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )
        notification_ids = self.list_ids(
            response,
            "notification_id",
        )
        self.assertEqual(
            notification_ids,
            {
                str(self.unread_notification.id),
                str(self.read_notification.id),
            },
        )
        self.assertNotIn(
            str(self.other_notification.id),
            notification_ids,
        )
        self.assertEqual(
            response.data["meta"]["unread_count"],
            1,
        )

        unread_response = self.client.get(
            reverse("patients:patient-notification-list"),
            {
                "read": "false",
                "type": Notification.Type.APPOINTMENT,
            },
        )
        self.assertEqual(
            unread_response.status_code,
            status.HTTP_200_OK,
            unread_response.data,
        )
        self.assertEqual(
            self.list_ids(unread_response, "notification_id"),
            {str(self.unread_notification.id)},
        )

    def test_notification_read_one_is_idempotent(self):
        url = reverse(
            "patients:patient-notification-read",
            kwargs={
                "notification_id": self.unread_notification.id,
            },
        )

        first_response = self.client.patch(
            url,
            data={},
            format="json",
        )
        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
            first_response.data,
        )

        self.unread_notification.refresh_from_db()
        first_read_at = self.unread_notification.read_at
        self.assertTrue(self.unread_notification.is_read)
        self.assertIsNotNone(first_read_at)

        second_response = self.client.patch(
            url,
            data={},
            format="json",
        )
        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
            second_response.data,
        )

        self.unread_notification.refresh_from_db()
        self.assertEqual(
            self.unread_notification.read_at,
            first_read_at,
        )

    def test_notification_read_other_patient_is_404(self):
        response = self.client.patch(
            reverse(
                "patients:patient-notification-read",
                kwargs={
                    "notification_id": self.other_notification.id,
                },
            ),
            data={},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            response.data,
        )
        self.other_notification.refresh_from_db()
        self.assertFalse(self.other_notification.is_read)

    def test_notification_read_all_updates_only_login_patient(self):
        second_unread = Notification.objects.create(
            recipient=self.patient_user,
            type=Notification.Type.MEDICATION,
            title="복약 알림",
            body="복약 시간입니다.",
            data={},
            is_read=False,
            read_at=None,
            deduplication_key="patient-api-a-medication",
        )

        response = self.client.patch(
            reverse("patients:patient-notification-read-all"),
            data={},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )
        self.assertEqual(
            response.data["data"]["updated_count"],
            2,
        )
        self.assertEqual(
            response.data["data"]["unread_count"],
            0,
        )

        self.unread_notification.refresh_from_db()
        second_unread.refresh_from_db()
        self.other_notification.refresh_from_db()

        self.assertTrue(self.unread_notification.is_read)
        self.assertTrue(second_unread.is_read)
        self.assertFalse(self.other_notification.is_read)
