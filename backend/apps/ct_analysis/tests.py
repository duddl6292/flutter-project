from decimal import Decimal
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.appointments.models import Encounter
from apps.assets.models import StoredObject
from apps.clinicians.models import Clinician, Department
from apps.diagnostics.models import Examination, ExaminationCatalog
from apps.hospitals.models import Hospital
from apps.imaging.models import ImagingAsset, ImagingStudy
from apps.notifications.models import Notification
from apps.patients.models import Patient

from .models import CTCase, InferenceJob, InferenceResult
from .services import CTAnalysisError, UploadedCT, _decimal


class CTAnalysisApiTests(APITestCase):
    def setUp(self) -> None:
        self.hospital = Hospital.objects.create(
            hospital_code="CT-HOSPITAL",
            name="CT Hospital",
            is_active=True,
        )
        self.department = Department.objects.create(
            code="CT-RAD",
            name="Radiology",
            is_active=True,
        )
        self.user = User.objects.create_user(
            username="620001",
            password="test-password",
            role=User.Role.CLINICIAN,
        )
        self.clinician = Clinician.objects.create(
            user=self.user,
            name="CT Doctor",
            license_number="620001",
            hospital=self.hospital,
            department=self.department,
            approval_status=Clinician.ApprovalStatus.APPROVED,
        )
        self.patient = Patient.objects.create(
            medical_record_number="CT-P-001",
            name="CT Patient",
            status=Patient.Status.ACTIVE,
        )
        self.encounter = Encounter.objects.create(
            encounter_number="CT-E-001",
            patient=self.patient,
            department=self.department,
            hospital=self.hospital,
            attending_clinician=self.clinician,
            registered_by=self.user,
            encounter_type=Encounter.EncounterType.OUTPATIENT,
            status=Encounter.Status.IN_PROGRESS,
        )
        self.client.force_authenticate(user=self.user)

    def test_inference_decimal_values_are_rounded_for_database_fields(self) -> None:
        self.assertEqual(_decimal("1.123456789"), Decimal("1.123457"))
        self.assertEqual(
            _decimal("2048.123456", decimal_places=3),
            Decimal("2048.123"),
        )

    @patch("apps.ct_analysis.views.upload_ct_file")
    def test_upload_creates_patient_mapped_case_and_queued_job(self, upload_mock) -> None:
        upload_mock.return_value = UploadedCT(
            uri="gs://brainon_ct-input_patient/uploads/input.nii.gz",
            sha256="a" * 64,
            size=128,
            content_type="application/gzip",
        )
        response = self.client.post(
            "/api/v1/ct-analysis/cases/",
            {
                "patient_id": str(self.patient.id),
                "study_type": "NCCT",
                "ct_file": SimpleUploadedFile(
                    "brain.nii.gz",
                    b"test-nifti",
                    content_type="application/gzip",
                ),
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        case = CTCase.objects.get(id=response.data["data"]["case_id"])
        self.assertEqual(case.encounter.patient, self.patient)
        self.assertEqual(case.status, CTCase.Status.READY)
        self.assertEqual(case.inference_jobs.get().status, InferenceJob.Status.QUEUED)

    def test_sources_returns_nifti_assets_for_selected_patient(self) -> None:
        examination = Examination.objects.create(
            patient=self.patient,
            encounter=self.encounter,
            hospital=self.hospital,
            test_code="BRAIN-CT",
            test_name="Brain CT",
            category=ExaminationCatalog.Category.IMAGING,
            performed_at=timezone.now(),
        )
        study = ImagingStudy.objects.create(
            examination=examination,
            modality=ImagingStudy.Modality.CT,
            study_instance_uid="1.2.840.CT.TEST",
            study_description="NCCT",
            status=ImagingStudy.Status.READY,
            imported_by=self.user,
            imported_at=timezone.now(),
        )
        stored = StoredObject.objects.create(
            provider=StoredObject.Provider.GCS,
            bucket_name="brainon_ct-input_patient",
            object_key="patients/test/input.nii.gz",
            original_filename="input.nii.gz",
            content_type="application/gzip",
            file_format="NIFTI",
            file_size_bytes=1024,
            sha256="b" * 64,
            status=StoredObject.Status.AVAILABLE,
            uploaded_by=self.user,
            available_at=timezone.now(),
        )
        asset = ImagingAsset.objects.create(
            study=study,
            stored_object=stored,
            asset_type=ImagingAsset.AssetType.NIFTI_VOLUME,
            is_primary=True,
            conversion_status=ImagingAsset.ConversionStatus.COMPLETED,
        )
        response = self.client.get(
            f"/api/v1/ct-analysis/sources/?patient_id={self.patient.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"][0]["imaging_asset_id"], str(asset.id))

    def test_uploaded_case_is_reused_as_patient_ct_source(self) -> None:
        source_case = CTCase.objects.create(
            encounter=self.encounter,
            study_type=CTCase.StudyType.NCCT,
            status=CTCase.Status.READY,
            input_uri="gs://brainon_ct-input_patient/uploads/reusable.nii.gz",
            input_sha256="d" * 64,
            file_size_bytes=4096,
            content_type="application/gzip",
            created_by=self.user,
        )
        sources_response = self.client.get(
            f"/api/v1/ct-analysis/sources/?patient_id={self.patient.id}"
        )
        self.assertEqual(sources_response.status_code, status.HTTP_200_OK)
        self.assertEqual(sources_response.data["data"][0]["source_type"], "CT_CASE")
        self.assertEqual(sources_response.data["data"][0]["source_id"], str(source_case.id))

        create_response = self.client.post(
            "/api/v1/ct-analysis/cases/",
            {
                "patient_id": str(self.patient.id),
                "study_type": "NCCT",
                "source_case_id": str(source_case.id),
            },
            format="multipart",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        reused = CTCase.objects.get(id=create_response.data["data"]["case_id"])
        self.assertEqual(reused.input_uri, source_case.input_uri)
        self.assertEqual(reused.encounter.patient, self.patient)

    @patch("apps.ct_analysis.services.call_inference_gateway")
    def test_run_persists_result_and_viewer_urls(self, gateway_mock) -> None:
        case = CTCase.objects.create(
            encounter=self.encounter,
            study_type=CTCase.StudyType.NCCT,
            status=CTCase.Status.READY,
            input_uri="gs://brainon_ct-input_patient/uploads/input.nii.gz",
            input_sha256="c" * 64,
            file_size_bytes=2048,
            content_type="application/gzip",
            created_by=self.user,
        )
        job = InferenceJob.objects.create(
            case=case,
            requested_by=self.user,
            parameters={"gateway_case_id": 123},
        )
        gateway_mock.return_value = {
            "schema_version": "1.0",
            "job_id": str(job.id),
            "case_id": 123,
            "status": "completed",
            "model_version": "1.0.0",
            "input": {"shape": [512, 512, 20], "spacing_mm": [0.5, 0.5, 5.0]},
            "model": {
                "model_id": "brainon-ct-25d",
                "model_version": "1.0.0",
                "checkpoint": "checkpoint_best.pth",
            },
            "artifacts": {
                "mask_uri": f"gs://brainon_ct-ai_results/results/{job.id}/mask.nii.gz",
                "result_json_uri": f"gs://brainon_ct-ai_results/results/{job.id}/result.json",
                "preview_uri": None,
                "probability_uri": None,
                "entropy_uri": None,
                "uncertainty_uri": None,
            },
            "result": {
                "lesion_detected": True,
                "lesion_voxel_count": 100,
                "lesion_volume_ml": 1.25,
                "lesion_slice_count": 2,
                "lesion_slice_indices": [8, 9],
                "lesion_slice_start": 8,
                "lesion_slice_end": 9,
                "max_lesion_slice": 9,
            },
            "performance": {
                "input_download_seconds": 0.5,
                "context_preparation_seconds": 0.5,
                "inference_seconds": 2.0,
                "postprocessing_seconds": 0.5,
                "output_upload_seconds": 0.5,
                "total_seconds": 4.0,
                "gpu_memory_measured": True,
                "gpu_peak_memory_mb": 2048.0,
            },
            "summary": "Lesion detected.",
            "message": "Clinical review required.",
            "error": None,
        }
        response = self.client.post(f"/api/v1/ct-analysis/cases/{case.id}/run/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["status"], CTCase.Status.COMPLETED)
        self.assertTrue(response.data["data"]["result"]["mask_url"].endswith("/mask/"))
        self.assertEqual(response.data["data"]["result"]["lesion_slice_indices"], [8, 9])
        self.assertIsNotNone(response.data["data"]["result"]["end_to_end_seconds"])
        self.assertEqual(InferenceResult.objects.get(job=job).lesion_voxels, 100)
        notification = Notification.objects.get(
            recipient=self.user,
            data__event="CT_ANALYSIS_COMPLETED",
        )
        self.assertEqual(
            notification.data["path"],
            f"/ct-analysis/{case.id}",
        )

    @patch("apps.ct_analysis.services.call_inference_gateway")
    def test_run_failure_creates_notification(self, gateway_mock) -> None:
        case = CTCase.objects.create(
            encounter=self.encounter,
            study_type=CTCase.StudyType.NCCT,
            status=CTCase.Status.READY,
            input_uri="gs://brainon_ct-input_patient/uploads/failure.nii.gz",
            input_sha256="f" * 64,
            file_size_bytes=2048,
            content_type="application/gzip",
            created_by=self.user,
        )
        job = InferenceJob.objects.create(
            case=case,
            requested_by=self.user,
            parameters={"gateway_case_id": 789},
        )
        gateway_mock.side_effect = CTAnalysisError(
            "추론 서비스 오류",
            code="INFERENCE_FAILED",
            retryable=True,
        )

        response = self.client.post(
            f"/api/v1/ct-analysis/cases/{case.id}/run/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_502_BAD_GATEWAY,
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.user,
                data__event="CT_ANALYSIS_FAILED",
                data__job_id=str(job.id),
            ).exists()
        )

    @patch("apps.ct_analysis.views.run_inference")
    def test_retry_creates_new_job_and_result_path_identity(self, run_mock) -> None:
        case = CTCase.objects.create(
            encounter=self.encounter,
            study_type=CTCase.StudyType.NCCT,
            status=CTCase.Status.FAILED,
            input_uri="gs://brainon_ct-input_patient/uploads/input.nii.gz",
            input_sha256="d" * 64,
            file_size_bytes=2048,
            content_type="application/gzip",
            created_by=self.user,
        )
        failed_job = InferenceJob.objects.create(
            case=case,
            requested_by=self.user,
            status=InferenceJob.Status.FAILED,
            progress=100,
            parameters={"gateway_case_id": 456},
            error_code="ARTIFACT_UPLOAD_FAILED",
            error_message="upload failed",
            error_retryable=True,
        )

        response = self.client.post(f"/api/v1/ct-analysis/cases/{case.id}/run/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(case.inference_jobs.count(), 2)
        retry_job = case.inference_jobs.first()
        self.assertNotEqual(retry_job.id, failed_job.id)
        self.assertEqual(retry_job.parameters, failed_job.parameters)
        run_mock.assert_called_once_with(retry_job)
