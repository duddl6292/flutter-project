from __future__ import annotations

import csv
import io
from pathlib import Path
from urllib.parse import urlparse
from uuid import UUID

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from google.cloud import storage

from apps.accounts.models import User
from apps.assets.models import StoredObject
from apps.diagnostics.models import Examination
from apps.imaging.models import ImagingAsset, ImagingStudy
from apps.patients.models import Patient


REQUIRED_COLUMNS = {
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
}


def _read_manifest(*, manifest_uri: str, manifest_file: str) -> str:
    if manifest_file:
        return Path(manifest_file).read_text(encoding="utf-8-sig")

    parsed = urlparse(manifest_uri)
    if parsed.scheme != "gs" or not parsed.netloc or not parsed.path.strip("/"):
        raise CommandError("매니페스트 URI는 gs://bucket/object 형식이어야 합니다.")

    try:
        return (
            storage.Client()
            .bucket(parsed.netloc)
            .blob(parsed.path.lstrip("/"))
            .download_as_text(encoding="utf-8")
        )
    except Exception as exc:
        raise CommandError(f"GCS 매니페스트를 읽지 못했습니다: {exc}") from exc


def _ct_rows(csv_text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(csv_text.lstrip("\ufeff")))
    columns = set(reader.fieldnames or [])
    missing = REQUIRED_COLUMNS - columns
    if missing:
        raise CommandError(
            "매니페스트 필수 컬럼이 없습니다: " + ", ".join(sorted(missing))
        )

    rows = [
        {key: (value or "").strip() for key, value in row.items()}
        for row in reader
        if (row.get("object_role") or "").strip().upper() == "CT"
    ]
    if not rows:
        raise CommandError("매니페스트에 object_role=CT 행이 없습니다.")

    patient_ids = [row["patient_id"] for row in rows]
    if len(patient_ids) != len(set(patient_ids)):
        raise CommandError("한 환자에 CT 원본 행이 두 개 이상 존재합니다.")
    return rows


class Command(BaseCommand):
    help = "검증된 GCS CT 매니페스트를 환자 영상검사와 연결합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--manifest-uri",
            default=settings.CT_DATASET_MANIFEST_URI,
            help="gs:// 형식의 검증된 CT 매니페스트 URI",
        )
        parser.add_argument(
            "--manifest-file",
            default="",
            help="테스트 또는 오프라인 실행용 로컬 CSV 경로",
        )
        parser.add_argument(
            "--imported-by",
            default="",
            help="영상 가져오기 감사 기록에 사용할 사용자명",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="매핑만 검증하고 DB에는 저장하지 않습니다.",
        )

    def handle(self, *args, **options):
        rows = _ct_rows(
            _read_manifest(
                manifest_uri=options["manifest_uri"],
                manifest_file=options["manifest_file"],
            )
        )

        fallback_user = self._fallback_user(options["imported_by"])
        mappings = self._validate_mappings(rows)

        if options["dry_run"]:
            self.stdout.write(
                self.style.SUCCESS(
                    f"검증 완료: CT {len(mappings)}건, 환자 {len(mappings)}명, DB 변경 0건"
                )
            )
            return

        with transaction.atomic():
            bucket_names = {row["bucket_name"] for row, _, _ in mappings}
            object_keys = {row["object_key"] for row, _, _ in mappings}
            stored_objects = {
                (item.bucket_name, item.object_key): item
                for item in StoredObject.objects.filter(
                    provider=StoredObject.Provider.GCS,
                    bucket_name__in=bucket_names,
                    object_key__in=object_keys,
                )
            }
            new_stored_objects = []
            for row, _, examination in mappings:
                location = (row["bucket_name"], row["object_key"])
                if location in stored_objects:
                    continue
                actor = (
                    examination.ordered_by.user
                    if examination.ordered_by_id
                    else fallback_user
                )
                stored_object = StoredObject(
                    provider=StoredObject.Provider.GCS,
                    bucket_name=row["bucket_name"],
                    object_key=row["object_key"],
                    original_filename=row["original_filename"],
                    content_type=row["gcs_content_type"] or "application/gzip",
                    file_format="NIFTI_GZ",
                    file_size_bytes=int(row["file_size_bytes"] or 0),
                    sha256=row["sha256"],
                    status=StoredObject.Status.AVAILABLE,
                    uploaded_by=actor,
                    available_at=(
                        parse_datetime(row["gcs_updated"]) or timezone.now()
                    ),
                    metadata={
                        "source": "brainon_ct_verified_manifest",
                        "manifest_patient_id": row["patient_id"],
                        "source_case_id": row["source_case_id"],
                        "gcs_generation": row.get("gcs_generation", ""),
                        "gcs_crc32c": row.get("gcs_crc32c", ""),
                    },
                )
                new_stored_objects.append(stored_object)
                stored_objects[location] = stored_object
            StoredObject.objects.bulk_create(
                new_stored_objects,
                batch_size=200,
            )

            examination_ids = [examination.id for _, _, examination in mappings]
            studies = {
                item.examination_id: item
                for item in ImagingStudy.objects.filter(
                    examination_id__in=examination_ids
                )
            }
            new_studies = []
            for row, _, examination in mappings:
                if examination.id in studies:
                    continue
                actor = (
                    examination.ordered_by.user
                    if examination.ordered_by_id
                    else fallback_user
                )
                study = ImagingStudy(
                    examination=examination,
                    modality=ImagingStudy.Modality.CT,
                    study_instance_uid=f"brainon.dataset.{row['source_case_id']}",
                    study_description="비조영 뇌 CT",
                    body_part="BRAIN",
                    status=ImagingStudy.Status.READY,
                    imported_by=actor,
                    imported_at=(
                        parse_datetime(row["gcs_updated"]) or timezone.now()
                    ),
                    metadata={
                        "source": "brainon_ct_verified_manifest",
                        "manifest_patient_id": row["patient_id"],
                        "source_case_id": row["source_case_id"],
                    },
                )
                new_studies.append(study)
                studies[examination.id] = study
            ImagingStudy.objects.bulk_create(new_studies, batch_size=200)

            stored_object_ids = [item.id for item in stored_objects.values()]
            assets = {
                item.stored_object_id: item
                for item in ImagingAsset.objects.filter(
                    stored_object_id__in=stored_object_ids
                )
            }
            new_assets = []
            for row, _, examination in mappings:
                stored_object = stored_objects[
                    (row["bucket_name"], row["object_key"])
                ]
                if stored_object.id in assets:
                    continue
                asset = ImagingAsset(
                    study=studies[examination.id],
                    stored_object=stored_object,
                    asset_type=ImagingAsset.AssetType.NIFTI_VOLUME,
                    is_primary=True,
                    conversion_status=(
                        ImagingAsset.ConversionStatus.NOT_REQUIRED
                    ),
                    metadata={
                        "source": "brainon_ct_verified_manifest",
                        "manifest_patient_id": row["patient_id"],
                    },
                )
                new_assets.append(asset)
                assets[stored_object.id] = asset
            ImagingAsset.objects.bulk_create(new_assets, batch_size=200)

        self.stdout.write(
            self.style.SUCCESS(
                "CT 매핑 완료: "
                f"환자 {len(mappings)}명, "
                f"StoredObject 생성 {len(new_stored_objects)}, "
                f"Study 생성 {len(new_studies)}, "
                f"Asset 생성 {len(new_assets)}"
            )
        )

    def _fallback_user(self, username: str):
        users = User.objects.filter(is_active=True)
        if username:
            try:
                return users.get(username=username)
            except User.DoesNotExist as exc:
                raise CommandError(f"가져오기 사용자를 찾을 수 없습니다: {username}") from exc

        user = users.filter(role=User.Role.ADMIN).order_by("username").first()
        if user is None:
            raise CommandError("활성 관리자 계정이 없어 --imported-by가 필요합니다.")
        return user

    def _validate_mappings(self, rows):
        errors = []
        parsed_rows = []
        for row in rows:
            try:
                patient_id = UUID(row["patient_id"])
            except (TypeError, ValueError):
                errors.append(f"잘못된 patient_id: {row['patient_id']}")
                continue
            parsed_rows.append((row, patient_id))

        patient_ids = [patient_id for _, patient_id in parsed_rows]
        patients = Patient.objects.in_bulk(patient_ids)
        examinations_by_patient = {}
        for examination in (
            Examination.objects.filter(
                patient_id__in=patient_ids,
                category="IMAGING",
            )
            .select_related("ordered_by__user")
            .order_by("patient_id")
        ):
            examinations_by_patient.setdefault(
                examination.patient_id,
                [],
            ).append(examination)

        mappings = []
        for row, patient_id in parsed_rows:
            patient = patients.get(patient_id)
            if patient is None:
                errors.append(f"DB에 없는 환자: {patient_id}")
                continue
            examinations = examinations_by_patient.get(patient_id, [])
            if len(examinations) != 1:
                errors.append(
                    f"환자 {patient_id}의 영상검사 개수가 1이 아닙니다: {len(examinations)}"
                )
                continue
            mappings.append((row, patient, examinations[0]))

        if errors:
            preview = "\n".join(errors[:20])
            suffix = f"\n... 외 {len(errors) - 20}건" if len(errors) > 20 else ""
            raise CommandError(
                f"CT 매핑 검증 실패 {len(errors)}건:\n{preview}{suffix}"
            )
        return mappings
