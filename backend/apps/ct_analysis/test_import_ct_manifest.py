import csv
import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from apps.accounts.models import User
from apps.assets.models import StoredObject
from apps.clinicians.models import Department
from apps.diagnostics.models import Examination
from apps.hospitals.models import Hospital
from apps.imaging.models import ImagingAsset, ImagingStudy
from apps.patients.models import Patient


class ImportCTManifestCommandTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="manifest-admin",
            password="test-password",
            role=User.Role.ADMIN,
        )
        hospital = Hospital.objects.create(
            hospital_code="MANIFEST-HOSPITAL",
            name="Manifest Hospital",
        )
        Department.objects.create(
            code="MANIFEST-RADIOLOGY",
            name="Manifest Radiology",
        )
        self.patient = Patient.objects.create(
            medical_record_number="MANIFEST-P001",
            name="Manifest Patient",
        )
        self.examination = Examination.objects.create(
            patient=self.patient,
            hospital=hospital,
            test_code="BRAIN_CT",
            test_name="Brain CT",
            category="IMAGING",
            accession_number="MANIFEST-ACC-001",
        )

    def write_manifest(self):
        handle = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            suffix=".csv",
            delete=False,
        )
        with handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "patient_id",
                    "object_role",
                    "bucket_name",
                    "object_key",
                    "original_filename",
                    "file_size_bytes",
                    "sha256",
                    "gcs_content_type",
                    "gcs_updated",
                    "source_case_id",
                ],
            )
            writer.writeheader()
            writer.writerow({
                "patient_id": str(self.patient.id),
                "object_role": "CT",
                "bucket_name": "test-ct-bucket",
                "object_key": f"patients/{self.patient.id}/ct/input-volume.nii.gz",
                "original_filename": "source.nii.gz",
                "file_size_bytes": "1024",
                "sha256": "a" * 64,
                "gcs_content_type": "application/gzip",
                "gcs_updated": "2026-08-05T02:16:04+00:00",
                "source_case_id": "TEST_CASE_001",
            })
        return Path(handle.name)

    def test_import_is_idempotent(self):
        manifest = self.write_manifest()
        self.addCleanup(manifest.unlink, missing_ok=True)

        for _ in range(2):
            call_command(
                "import_ct_manifest",
                manifest_file=str(manifest),
                imported_by=self.admin.username,
            )

        self.assertEqual(StoredObject.objects.count(), 1)
        self.assertEqual(ImagingStudy.objects.count(), 1)
        self.assertEqual(ImagingAsset.objects.count(), 1)
        asset = ImagingAsset.objects.select_related(
            "study__examination",
            "stored_object",
        ).get()
        self.assertEqual(
            asset.study.examination.patient_id,
            self.patient.id,
        )
        self.assertEqual(
            asset.stored_object.status,
            StoredObject.Status.AVAILABLE,
        )

    def test_dry_run_does_not_write(self):
        manifest = self.write_manifest()
        self.addCleanup(manifest.unlink, missing_ok=True)

        call_command(
            "import_ct_manifest",
            manifest_file=str(manifest),
            imported_by=self.admin.username,
            dry_run=True,
        )

        self.assertFalse(StoredObject.objects.exists())
        self.assertFalse(ImagingStudy.objects.exists())
        self.assertFalse(ImagingAsset.objects.exists())
