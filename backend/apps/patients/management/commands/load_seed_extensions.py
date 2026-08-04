from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from uuid import UUID

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction


TARGET_DATABASE = "medical_cdss"
TARGET_HOST = "34.87.186.176"

EXPECTED_HEADERS = {
    "patient_hospital_ids.csv": [
        "id",
        "patient_id",
        "hospital_id",
        "hospital_code",
        "hospital_name",
        "hospital_specific_mrn",
        "first_visit_date",
        "is_primary",
        "status",
        "source_system",
        "schema_status",
    ],
    "guardians.csv": [
        "id",
        "patient_id",
        "name",
        "relationship",
        "phone",
        "email",
        "can_view_records",
        "can_book_appointments",
        "can_receive_notifications",
        "consent_status",
        "current_schema_mapping",
        "schema_status",
    ],
    "patient_private.csv": [
        "patient_id",
        "global_patient_number",
        "name",
        "resident_registration_number_synthetic",
        "resident_registration_number_masked",
        "rrn_checksum_valid",
        "phone",
        "email",
        "storage_requirement",
        "schema_status",
    ],
    "drug_master.csv": [
        "drug_master_id",
        "drug_code",
        "product_name",
        "ingredient",
        "strength",
        "route",
        "dose_example",
        "frequency_example",
        "timing_example",
        "stroke_related_use_and_caution",
        "source_url",
        "clinical_disclaimer",
        "schema_status",
    ],
}


class Command(BaseCommand):
    help = "Load synthetic extension CSVs into the verified BrainOn VM database."

    def add_arguments(self, parser):
        parser.add_argument("--seed-root", required=True, type=Path)
        parser.add_argument(
            "--commit",
            action="store_true",
            help="Actually commit rows. Without this flag, all writes are rolled back.",
        )

    def handle(self, *args, **options):
        seed_root = options["seed_root"].expanduser().resolve()
        commit = options["commit"]

        self._assert_target_database()

        if not seed_root.is_dir():
            raise CommandError(f"Seed root does not exist: {seed_root}")

        paths = {
            name: self._find_exactly_one(seed_root, name)
            for name in EXPECTED_HEADERS
        }
        stats = {
            "PatientHospitalIdentifier": [0, 0],
            "Guardian": [0, 0],
            "PatientGuardian": [0, 0],
            "PatientPrivateIdentity": [0, 0],
            "DrugMaster": [0, 0],
        }

        try:
            with transaction.atomic():
                self._load_patient_hospital_ids(
                    paths["patient_hospital_ids.csv"], stats
                )
                self._load_guardians(paths["guardians.csv"], stats)
                self._load_patient_private(paths["patient_private.csv"], stats)
                self._load_drug_master(paths["drug_master.csv"], stats)

                if not commit:
                    transaction.set_rollback(True)
        except CommandError:
            raise
        except Exception as exc:
            raise CommandError(
                f"Seed load failed; the whole transaction was rolled back: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

        mode = "COMMITTED" if commit else "DRY_RUN_ROLLED_BACK"
        self.stdout.write(self.style.SUCCESS(f"RESULT={mode}"))
        for model_name, (created, updated) in stats.items():
            self.stdout.write(
                f"{model_name}: created={created}, updated={updated}, "
                f"total={created + updated}"
            )

    def _assert_target_database(self):
        configured_host = str(connection.settings_dict.get("HOST") or "")
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT current_database(), current_user, "
                "inet_server_addr()::text, inet_server_port()"
            )
            database, user, server, port = cursor.fetchone()

        if database != TARGET_DATABASE:
            raise CommandError(
                f"Refusing to run: connected database is {database!r}, "
                f"expected {TARGET_DATABASE!r}."
            )
        if configured_host != TARGET_HOST:
            raise CommandError(
                f"Refusing to run: configured host is {configured_host!r}, "
                f"expected {TARGET_HOST!r}."
            )

        self.stdout.write(
            f"TARGET_CONFIRMED database={database} host={configured_host} "
            f"server={server} port={port} user={user}"
        )

    def _find_exactly_one(self, seed_root: Path, filename: str) -> Path:
        matches = sorted(path for path in seed_root.rglob(filename) if path.is_file())
        if len(matches) != 1:
            raise CommandError(
                f"Expected exactly one {filename!r} below {seed_root}; "
                f"found {len(matches)}."
            )
        return matches[0]

    def _iter_rows(self, path: Path):
        expected = EXPECTED_HEADERS[path.name]
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            actual = reader.fieldnames or []
            if actual != expected:
                raise CommandError(
                    f"Header mismatch in {path.name}. "
                    f"Expected {expected!r}; got {actual!r}."
                )

            for line_number, raw_row in enumerate(reader, start=2):
                row = {
                    key: (value.strip() if value is not None else "")
                    for key, value in raw_row.items()
                }
                if not any(row.values()):
                    continue
                yield line_number, row

    def _required(self, row, key, filename, line_number):
        value = row.get(key, "").strip()
        if not value:
            raise CommandError(
                f"{filename}:{line_number}: required column {key!r} is empty."
            )
        return value

    def _uuid(self, row, key, filename, line_number):
        value = self._required(row, key, filename, line_number)
        try:
            return UUID(value)
        except ValueError as exc:
            raise CommandError(
                f"{filename}:{line_number}: {key!r} is not a valid UUID."
            ) from exc

    def _boolean(self, row, key, filename, line_number):
        value = self._required(row, key, filename, line_number).lower()
        if value in {"1", "true", "t", "yes", "y"}:
            return True
        if value in {"0", "false", "f", "no", "n"}:
            return False
        raise CommandError(
            f"{filename}:{line_number}: {key!r} must be a boolean value."
        )

    def _optional_date(self, row, key, filename, line_number):
        value = row.get(key, "").strip()
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise CommandError(
                f"{filename}:{line_number}: {key!r} must use YYYY-MM-DD."
            ) from exc

    def _validate_choice(self, model, field_name, value, filename, line_number):
        field = model._meta.get_field(field_name)
        allowed = {str(key) for key, _label in field.flatchoices}
        if allowed and value not in allowed:
            raise CommandError(
                f"{filename}:{line_number}: invalid value for "
                f"{model._meta.label}.{field_name}."
            )

    def _get_required(self, model, pk, filename, line_number, column):
        obj = model.objects.filter(pk=pk).first()
        if obj is None:
            raise CommandError(
                f"{filename}:{line_number}: {column} does not reference an "
                f"existing {model._meta.label}."
            )
        return obj

    @staticmethod
    def _bump(stats, model_name, created):
        stats[model_name][0 if created else 1] += 1

    def _load_patient_hospital_ids(self, path, stats):
        Patient = apps.get_model("patients", "Patient")
        Hospital = apps.get_model("hospitals", "Hospital")
        Identifier = apps.get_model("patients", "PatientHospitalIdentifier")

        for line_number, row in self._iter_rows(path):
            record_id = self._uuid(row, "id", path.name, line_number)
            patient_id = self._uuid(row, "patient_id", path.name, line_number)
            hospital_id = self._uuid(row, "hospital_id", path.name, line_number)
            mrn = self._required(
                row, "hospital_specific_mrn", path.name, line_number
            )
            first_visit_date = self._optional_date(
                row, "first_visit_date", path.name, line_number
            )
            is_primary = self._boolean(
                row, "is_primary", path.name, line_number
            )
            status = self._required(row, "status", path.name, line_number)
            self._validate_choice(
                Identifier, "status", status, path.name, line_number
            )

            self._get_required(
                Patient, patient_id, path.name, line_number, "patient_id"
            )
            hospital = self._get_required(
                Hospital, hospital_id, path.name, line_number, "hospital_id"
            )

            csv_hospital_code = row.get("hospital_code", "")
            if csv_hospital_code and (hospital.hospital_code or "").strip() != csv_hospital_code:
                raise CommandError(
                    f"{path.name}:{line_number}: hospital_code does not match "
                    "the referenced Hospital."
                )
            csv_hospital_name = row.get("hospital_name", "")
            if csv_hospital_name and (hospital.name or "").strip() != csv_hospital_name:
                raise CommandError(
                    f"{path.name}:{line_number}: hospital_name does not match "
                    "the referenced Hospital."
                )

            if (
                Identifier.objects.filter(
                    patient_id=patient_id, hospital_id=hospital_id
                )
                .exclude(pk=record_id)
                .exists()
            ):
                raise CommandError(
                    f"{path.name}:{line_number}: another row already uses the "
                    "same patient and hospital."
                )
            if (
                Identifier.objects.filter(
                    hospital_id=hospital_id, hospital_specific_mrn=mrn
                )
                .exclude(pk=record_id)
                .exists()
            ):
                raise CommandError(
                    f"{path.name}:{line_number}: another row already uses the "
                    "same hospital-specific MRN."
                )
            if (
                is_primary
                and Identifier.objects.filter(
                    patient_id=patient_id, is_primary=True
                )
                .exclude(pk=record_id)
                .exists()
            ):
                raise CommandError(
                    f"{path.name}:{line_number}: patient already has another "
                    "primary hospital."
                )

            _obj, created = Identifier.objects.update_or_create(
                pk=record_id,
                defaults={
                    "patient_id": patient_id,
                    "hospital_id": hospital_id,
                    "hospital_specific_mrn": mrn,
                    "first_visit_date": first_visit_date,
                    "is_primary": is_primary,
                    "status": status,
                    "source_system": row.get("source_system", ""),
                },
            )
            self._bump(stats, "PatientHospitalIdentifier", created)

    def _load_guardians(self, path, stats):
        Patient = apps.get_model("patients", "Patient")
        Guardian = apps.get_model("patients", "Guardian")
        PatientGuardian = apps.get_model("patients", "PatientGuardian")

        for line_number, row in self._iter_rows(path):
            guardian_id = self._uuid(row, "id", path.name, line_number)
            patient_id = self._uuid(row, "patient_id", path.name, line_number)
            self._get_required(
                Patient, patient_id, path.name, line_number, "patient_id"
            )

            relationship = self._required(
                row, "relationship", path.name, line_number
            )
            consent_status = self._required(
                row, "consent_status", path.name, line_number
            )
            self._validate_choice(
                PatientGuardian,
                "relationship",
                relationship,
                path.name,
                line_number,
            )
            self._validate_choice(
                PatientGuardian,
                "consent_status",
                consent_status,
                path.name,
                line_number,
            )

            _guardian, guardian_created = Guardian.objects.update_or_create(
                pk=guardian_id,
                defaults={
                    "name": self._required(
                        row, "name", path.name, line_number
                    ),
                    "phone": row.get("phone", ""),
                    "email": row.get("email", ""),
                },
            )
            self._bump(stats, "Guardian", guardian_created)

            _link, link_created = PatientGuardian.objects.update_or_create(
                patient_id=patient_id,
                guardian_id=guardian_id,
                defaults={
                    "relationship": relationship,
                    "can_view_records": self._boolean(
                        row, "can_view_records", path.name, line_number
                    ),
                    "can_book_appointments": self._boolean(
                        row, "can_book_appointments", path.name, line_number
                    ),
                    "can_receive_notifications": self._boolean(
                        row,
                        "can_receive_notifications",
                        path.name,
                        line_number,
                    ),
                    "consent_status": consent_status,
                },
            )
            self._bump(stats, "PatientGuardian", link_created)

    def _load_patient_private(self, path, stats):
        Patient = apps.get_model("patients", "Patient")
        PrivateIdentity = apps.get_model("patients", "PatientPrivateIdentity")

        for line_number, row in self._iter_rows(path):
            # Never store, log, or include these synthetic raw values in errors.
            row.pop("resident_registration_number_synthetic", None)
            row.pop("phone", None)
            row.pop("email", None)

            patient_id = self._uuid(row, "patient_id", path.name, line_number)
            patient = self._get_required(
                Patient, patient_id, path.name, line_number, "patient_id"
            )
            csv_name = row.get("name", "")
            if csv_name and (patient.name or "").strip() != csv_name:
                raise CommandError(
                    f"{path.name}:{line_number}: name does not match the "
                    "referenced Patient."
                )

            global_number = self._required(
                row, "global_patient_number", path.name, line_number
            )
            if (
                PrivateIdentity.objects.filter(
                    global_patient_number=global_number
                )
                .exclude(patient_id=patient_id)
                .exists()
            ):
                raise CommandError(
                    f"{path.name}:{line_number}: global_patient_number is "
                    "already assigned to another patient."
                )

            _obj, created = PrivateIdentity.objects.update_or_create(
                patient_id=patient_id,
                defaults={
                    "global_patient_number": global_number,
                    "resident_registration_number_encrypted": "",
                    "resident_registration_number_masked": self._required(
                        row,
                        "resident_registration_number_masked",
                        path.name,
                        line_number,
                    ),
                    "rrn_checksum_valid": self._boolean(
                        row, "rrn_checksum_valid", path.name, line_number
                    ),
                    "phone_encrypted": "",
                    "email_encrypted": "",
                    "encryption_key_version": "not_applicable_synthetic",
                },
            )
            self._bump(stats, "PatientPrivateIdentity", created)

    def _load_drug_master(self, path, stats):
        DrugMaster = apps.get_model("prescriptions", "DrugMaster")

        for line_number, row in self._iter_rows(path):
            record_id = self._uuid(
                row, "drug_master_id", path.name, line_number
            )
            drug_code = self._required(
                row, "drug_code", path.name, line_number
            )
            if (
                DrugMaster.objects.filter(drug_code=drug_code)
                .exclude(pk=record_id)
                .exists()
            ):
                raise CommandError(
                    f"{path.name}:{line_number}: drug_code is already assigned "
                    "to another DrugMaster row."
                )

            _obj, created = DrugMaster.objects.update_or_create(
                pk=record_id,
                defaults={
                    "drug_code": drug_code,
                    "product_name": self._required(
                        row, "product_name", path.name, line_number
                    ),
                    "ingredient": self._required(
                        row, "ingredient", path.name, line_number
                    ),
                    "strength": row.get("strength", ""),
                    "route": row.get("route", ""),
                    "dose_example": row.get("dose_example", ""),
                    "frequency_example": row.get("frequency_example", ""),
                    "timing_example": row.get("timing_example", ""),
                    "stroke_related_use_and_caution": row.get(
                        "stroke_related_use_and_caution", ""
                    ),
                    "source_url": row.get("source_url", ""),
                    "clinical_disclaimer": row.get(
                        "clinical_disclaimer", ""
                    ),
                },
            )
            self._bump(stats, "DrugMaster", created)
