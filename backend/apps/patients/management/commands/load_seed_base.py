from __future__ import annotations

import csv
import hashlib
import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from django.apps import apps
from django.conf import settings
from django.contrib.auth.hashers import (
    check_password,
    identify_hasher,
    is_password_usable,
    make_password,
)
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, models, transaction
from django.db.migrations.executor import MigrationExecutor
from django.utils import timezone

TARGET_DATABASE = "medical_cdss"
TARGET_HOST = "34.87.186.176"
TARGET_PORT = 5432
TARGET_USER = "cdssadmin"
TARGET_POSTGRES_MAJOR = 17
EXPECTED_DEV_COMMIT = "220bbb37a3166f7b754aa3e8fb7de5c287328dec"
LOADER_REVISION = "2026-08-04-claim-hashes-preflight-v2"

CLAIM_CODES_FILENAME = "account_claim_codes_secure.csv"
CLAIM_HASH_PLACEHOLDER = "Django make_password(raw_code) 적용 예정"
CLAIM_CODE_HANDLING_RULE = "DB 평문 저장 금지, Django 해시만 저장, Git 커밋 금지"
CLAIM_CODES_HEADER = [
    "claim_id",
    "patient_id",
    "patient_name",
    "hospital_code",
    "hospital_name",
    "raw_claim_code_synthetic",
    "handling_rule",
]

EXPECTED_CURRENT_SHEETS = (
    "HOSPITALS",
    "DEPARTMENTS",
    "USERS",
    "USER_CONSENTS",
    "CLINICIANS",
    "CLINICIAN_AVAILABILITIES",
    "CLINICIAN_TIME_OFFS",
    "PATIENTS",
    "PATIENT_ACCOUNT_CLAIMS",
    "PROVISIONAL_IDENTITIES",
    "PATIENT_IDENTITY_RESOLUTION_LOGS",
    "PATIENT_FAVORITE_HOSPITALS",
    "APPOINTMENTS",
    "APPOINTMENT_STATUS_HISTORY",
    "ENCOUNTERS",
    "CLINICAL_RECORDS",
    "PRESCRIPTIONS",
    "PRESCRIPTION_ITEMS",
    "MEDICATION_SCHEDULES",
    "MEDICATION_RECORDS",
    "STORED_OBJECTS",
    "EXAMINATION_CATALOGS",
    "EXAMINATIONS",
    "EXAMINATION_OBSERVATIONS",
    "EXAMINATION_STATUS_HISTORY",
    "DIAGNOSTIC_REPORTS",
    "DIAGNOSTIC_REPORT_ASSETS",
    "DIAGNOSTIC_REPORT_STATUS_HISTORY",
    "AI_MODEL_VERSIONS",
    "CONSULTATIONS",
    "CONSULTATION_PARTICIPANTS",
    "CONSULTATION_MESSAGES",
    "CONSULTATION_ATTACHMENTS",
    "CONSULTATION_STATUS_HISTORY",
    "ENCOUNTER_ACCESS_GRANTS",
    "DEVICES",
    "NOTIFICATION_PREFERENCES",
    "NOTIFICATION_SETTINGS",
    "NOTIFICATIONS",
    "NOTIFICATION_DELIVERIES",
    "KNOWLEDGE_DOCUMENTS",
    "KNOWLEDGE_CHUNKS",
    "KNOWLEDGE_EMBEDDINGS",
    "CHAT_CONVERSATIONS",
    "CHAT_MESSAGES",
    "CHAT_CONTEXT_REFERENCES",
    "CHAT_TOOL_EXECUTIONS",
    "CHAT_FEEDBACK",
    "AUDIT_EVENTS",
    "DOCUMENTATION_RULES",
    "DOCUMENTATION_DEFICIENCIES",
    "DOCUMENTATION_DEFICIENCY_ITEMS",
    "DOCUMENTATION_REVIEWS",
    "DOCUMENTATION_STATUS_HISTORY",
)

# These columns deliberately document or validate the package, but the pinned
# Django schema does not persist them in the corresponding model.
ALLOWED_NON_MODEL_COLUMNS = {
    "HOSPITALS": {
        "identified_patient_target",
        "provisional_patient_target",
        "total_patient_target",
        "source_url",
    },
    "USERS": {"password_source"},
    "CLINICIANS": {
        "hospital_code",
        "hospital_name",
        "department_code",
        "department_name",
        "affiliation_notice",
    },
    "PATIENTS": {
        "primary_hospital_code",
        "primary_hospital_name",
        "primary_diagnosis_code",
        "primary_diagnosis_name",
        "care_scenario",
    },
    "PATIENT_FAVORITE_HOSPITALS": {"hospital_code", "hospital_name"},
    "APPOINTMENTS": {"department_code", "hospital_code"},
    "ENCOUNTERS": {"department_code", "hospital_code"},
    "MEDICATION_RECORDS": {"prescription_item_id"},
    "EXAMINATIONS": {"hospital_code"},
}

PASSWORD_SOURCE_TO_ENV = {
    "ADMIN_SEED_PASSWORD 환경변수": "ADMIN_SEED_PASSWORD",
    "CLINICIAN_SEED_PASSWORD 환경변수": "CLINICIAN_SEED_PASSWORD",
    "PATIENT_SEED_PASSWORD 환경변수": "PATIENT_SEED_PASSWORD",
}


@dataclass(frozen=True)
class Dataset:
    sequence: int
    sheet: str
    filename: str
    app_label: str
    model_name: str
    expected_rows: int

    @property
    def model_label(self) -> str:
        return f"{self.app_label}.{self.model_name}"


class Command(BaseCommand):
    help = (
        "Load BrainOn synthetic base datasets 01-54 into a verified VM "
        "database. The target must be empty unless "
        "--preserve-existing-superuser is used for exactly one verified "
        "Django superuser. Without --commit, every write is rolled back. "
        f"Loader revision: {LOADER_REVISION}."
    )

    def add_arguments(self, parser):
        parser.add_argument("--seed-root", required=True, type=Path)
        parser.add_argument(
            "--commit",
            action="store_true",
            help="Actually commit rows. Without this flag, all writes are rolled back.",
        )
        parser.add_argument(
            "--preserve-existing-superuser",
            action="store_true",
            help=(
                "Preserve exactly one existing active Django staff/superuser. "
                "Every other target model must still be empty, and unique-key "
                "collisions with users.csv are rejected before loading."
            ),
        )

    def handle(self, *args, **options):
        seed_root = options["seed_root"].expanduser().resolve()
        commit = bool(options["commit"])
        preserve_existing_superuser = bool(
            options["preserve_existing_superuser"]
        )

        self._assert_target_database()
        self._assert_migrations_current()
        self.stdout.write(f"LOADER_CONFIRMED revision={LOADER_REVISION}")
        package_root = self._find_package_root(seed_root)
        datasets = self._verify_package(package_root)
        self._assert_password_environment()
        self._user_password_hashes = self._prepare_user_password_hashes(
            package_root,
            datasets,
        )
        self._claim_code_hashes = self._prepare_claim_code_hashes(
            package_root,
            datasets,
        )
        self._assert_models_compatible(package_root, datasets)
        baseline_counts = self._assert_target_state(
            package_root,
            datasets,
            preserve_existing_superuser=preserve_existing_superuser,
        )

        total_expected = sum(dataset.expected_rows for dataset in datasets)
        self.stdout.write(
            "PACKAGE_CONFIRMED "
            f"dev_commit={EXPECTED_DEV_COMMIT} datasets={len(datasets)} "
            f"expected_rows={total_expected}"
        )
        preserved_users = baseline_counts.get("accounts.User", 0)
        self.stdout.write(
            "TARGET_STATE_CONFIRMED "
            f"models={len(datasets)} preserved_existing_users={preserved_users}"
        )

        loaded_counts: dict[str, int] = {}
        current_dataset: Dataset | None = None

        try:
            with transaction.atomic():
                for current_dataset in datasets:
                    count = self._load_dataset(
                        package_root,
                        current_dataset,
                        baseline_count=baseline_counts[current_dataset.model_label],
                    )
                    loaded_counts[current_dataset.sheet] = count
                    self.stdout.write(
                        f"{current_dataset.sequence:02d}/{len(datasets):02d} "
                        f"{current_dataset.sheet} "
                        f"model={current_dataset.model_label} rows={count} "
                        "validated=OK"
                    )

                self._verify_loaded_counts(datasets, baseline_counts)

                if not commit:
                    transaction.set_rollback(True)
        except CommandError:
            raise
        except Exception as exc:
            where = (
                current_dataset.sheet if current_dataset is not None else "PREFLIGHT"
            )
            raise CommandError(
                f"Base seed failed at {where}; the whole transaction was "
                f"rolled back: {type(exc).__name__}: {exc}"
            ) from exc

        total_loaded = sum(loaded_counts.values())
        mode = "COMMITTED" if commit else "DRY_RUN_ROLLED_BACK"
        self.stdout.write(self.style.SUCCESS(f"RESULT={mode}"))
        self.stdout.write(
            f"DATASETS={len(loaded_counts)} TOTAL_ROWS={total_loaded}"
        )

    def _assert_target_database(self) -> None:
        configured_host = str(connection.settings_dict.get("HOST") or "")
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT current_database(), current_user, "
                "inet_server_addr()::text, inet_server_port()"
            )
            database, user, server, port = cursor.fetchone()
            cursor.execute("SHOW server_version_num")
            server_version_num = int(cursor.fetchone()[0])
            cursor.execute(
                "SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()"
            )
            ssl_row = cursor.fetchone()
            ssl_enabled = bool(ssl_row and ssl_row[0])

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
        if user != TARGET_USER:
            raise CommandError(
                f"Refusing to run: connected PostgreSQL user is {user!r}, "
                f"expected {TARGET_USER!r}."
            )
        if port != TARGET_PORT:
            raise CommandError(
                f"Refusing to run: connected PostgreSQL port is {port!r}, "
                f"expected {TARGET_PORT!r}."
            )
        postgres_major = server_version_num // 10000
        if postgres_major != TARGET_POSTGRES_MAJOR:
            raise CommandError(
                f"Refusing to run: PostgreSQL major version is {postgres_major}, "
                f"expected {TARGET_POSTGRES_MAJOR}."
            )
        if not ssl_enabled:
            raise CommandError(
                "Refusing to run: the VM PostgreSQL connection is not using SSL."
            )

        self.stdout.write(
            f"TARGET_CONFIRMED database={database} host={configured_host} "
            f"server={server} port={port} user={user} "
            f"postgres_major={postgres_major} ssl=true"
        )

    def _assert_migrations_current(self) -> None:
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        plan = executor.migration_plan(targets)
        if plan:
            labels = sorted({
                f"{migration.app_label}.{migration.name}"
                for migration, _backwards in plan
            })
            preview = ", ".join(labels[:10])
            suffix = " ..." if len(labels) > 10 else ""
            raise CommandError(
                "Refusing to load seed because unapplied migrations exist: "
                f"{preview}{suffix}. Run and verify migrations first."
            )
        self.stdout.write("MIGRATIONS_CONFIRMED pending=0")

    def _find_package_root(self, seed_root: Path) -> Path:
        if not seed_root.is_dir():
            raise CommandError(f"Seed root does not exist: {seed_root}")

        candidates: list[Path] = []
        if (
            (seed_root / "manifest.json").is_file()
            and (seed_root / "csv" / "load_order.csv").is_file()
        ):
            candidates.append(seed_root)

        candidates.extend(
            path.parent
            for path in seed_root.rglob("manifest.json")
            if path.parent != seed_root
            and (path.parent / "csv" / "load_order.csv").is_file()
        )
        unique = sorted(set(candidates))
        if len(unique) != 1:
            raise CommandError(
                "Expected exactly one BrainOn package below "
                f"{seed_root}; found {len(unique)}."
            )
        return unique[0]

    def _verify_package(self, package_root: Path) -> list[Dataset]:
        manifest = self._read_json(package_root / "manifest.json")
        if not isinstance(manifest, dict):
            raise CommandError("manifest.json must contain one JSON object.")

        if manifest.get("classification") != "SYNTHETIC_MEDICAL_DATA":
            raise CommandError("Package classification is not SYNTHETIC_MEDICAL_DATA.")
        if manifest.get("dev_commit") != EXPECTED_DEV_COMMIT:
            raise CommandError(
                "Package dev_commit does not match the pinned BrainOn seed schema."
            )
        if manifest.get("prepared_model_count") != len(EXPECTED_CURRENT_SHEETS):
            raise CommandError("Package prepared_model_count is not 54.")

        validation = manifest.get("validation") or {}
        if (
            validation.get("total") != len(EXPECTED_CURRENT_SHEETS)
            or validation.get("passed") != len(EXPECTED_CURRENT_SHEETS)
            or validation.get("failed") != 0
        ):
            raise CommandError("Package validation summary is not 54/54 PASS.")

        load_order_path = package_root / "csv" / "load_order.csv"
        coverage_path = package_root / "csv" / "model_coverage.csv"
        load_header, load_rows = self._read_csv(load_order_path)
        coverage_header, coverage_rows = self._read_csv(coverage_path)

        if load_header != ["sequence", "dataset_sheet", "category", "description"]:
            raise CommandError("load_order.csv header does not match the package contract.")
        expected_coverage_header = [
            "app_label",
            "model_name",
            "dataset_sheet",
            "row_count",
            "load_status",
            "reason",
            "dev_commit",
        ]
        if coverage_header != expected_coverage_header:
            raise CommandError(
                "model_coverage.csv header does not match the package contract."
            )

        current_rows = [row for _line, row in load_rows if row["category"] == "CURRENT"]
        actual_sheets = tuple(row["dataset_sheet"] for row in current_rows)
        if actual_sheets != EXPECTED_CURRENT_SHEETS:
            raise CommandError("CURRENT dataset order is not the pinned 01-54 order.")

        for index, row in enumerate(current_rows, start=1):
            if row["sequence"] != f"{index:02d}":
                raise CommandError("CURRENT dataset sequence is not contiguous 01-54.")

        coverage_by_sheet: dict[str, dict[str, str]] = {}
        for _line, row in coverage_rows:
            sheet = row["dataset_sheet"]
            if sheet in coverage_by_sheet:
                raise CommandError(f"Duplicate model coverage entry for {sheet}.")
            coverage_by_sheet[sheet] = row

        counts = manifest.get("counts") or {}
        datasets: list[Dataset] = []
        for index, sheet in enumerate(EXPECTED_CURRENT_SHEETS, start=1):
            coverage = coverage_by_sheet.get(sheet)
            if coverage is None:
                raise CommandError(f"Missing model coverage entry for {sheet}.")
            if coverage["load_status"] != "PREPARED_FOR_ORM_SEED":
                raise CommandError(f"{sheet} is not marked PREPARED_FOR_ORM_SEED.")
            if coverage["dev_commit"] != EXPECTED_DEV_COMMIT:
                raise CommandError(f"{sheet} coverage commit does not match.")

            try:
                coverage_count = int(coverage["row_count"])
                manifest_count = int(counts[sheet])
            except (KeyError, TypeError, ValueError) as exc:
                raise CommandError(f"Invalid expected count for {sheet}.") from exc
            if coverage_count != manifest_count:
                raise CommandError(f"Coverage/manifest row count mismatch for {sheet}.")

            datasets.append(
                Dataset(
                    sequence=index,
                    sheet=sheet,
                    filename=f"{sheet.lower()}.csv",
                    app_label=coverage["app_label"],
                    model_name=coverage["model_name"],
                    expected_rows=manifest_count,
                )
            )

        self._verify_checksums(package_root, datasets)
        return datasets

    def _verify_checksums(
        self, package_root: Path, datasets: list[Dataset]
    ) -> None:
        checksum_document = self._read_json(package_root / "SHA256SUMS.json")

        # The pinned v2 package wraps its checksum records as
        # {"value": [...]}.  A root array is also accepted for compatibility
        # with packages produced by the earlier exporter.
        if isinstance(checksum_document, dict):
            checksum_records = checksum_document.get("value")
            if not isinstance(checksum_records, list):
                raise CommandError(
                    "SHA256SUMS.json must contain a JSON array in the "
                    "root 'value' property."
                )
        elif isinstance(checksum_document, list):
            checksum_records = checksum_document
        else:
            raise CommandError(
                "SHA256SUMS.json must contain either a root JSON array or "
                "an object whose 'value' property is a JSON array."
            )

        checksum_by_file: dict[str, str] = {}
        for record in checksum_records:
            if not isinstance(record, dict):
                raise CommandError("Invalid SHA256SUMS.json record.")
            name = record.get("file")
            digest = record.get("sha256")
            if not isinstance(name, str) or not isinstance(digest, str):
                raise CommandError("Invalid SHA256SUMS.json record fields.")
            name = name.replace("\\", "/").removeprefix("./")
            digest = digest.lower()
            if len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise CommandError(
                    f"Invalid SHA-256 digest for checksum record {name!r}."
                )
            if name in checksum_by_file:
                raise CommandError(f"Duplicate checksum record for {name}.")
            checksum_by_file[name] = digest

        relative_paths = [
            "csv/load_order.csv",
            "csv/model_coverage.csv",
            f"csv/{CLAIM_CODES_FILENAME}",
        ]
        relative_paths.extend(f"csv/{dataset.filename}" for dataset in datasets)
        for relative in relative_paths:
            path = package_root / relative
            if not path.is_file():
                raise CommandError(f"Required package file is missing: {relative}")
            expected = checksum_by_file.get(relative)
            if expected is None:
                raise CommandError(f"Checksum is missing for {relative}.")
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != expected:
                raise CommandError(f"Checksum mismatch for {relative}.")

    def _assert_password_environment(self) -> None:
        missing = [
            env_name
            for env_name in PASSWORD_SOURCE_TO_ENV.values()
            if not os.environ.get(env_name)
        ]
        if missing:
            raise CommandError(
                "Missing required password environment variables: "
                + ", ".join(sorted(missing))
                + ". Values are never read from CSV or printed."
            )

    def _prepare_claim_code_hashes(
        self,
        package_root: Path,
        datasets: list[Dataset],
    ) -> dict[str, str]:
        """Validate the secure claim-code companion file and hash its codes.

        The raw synthetic claim codes are never returned, logged, or written to
        a model field.  Only Django password hashes are retained for insertion.
        """
        try:
            claims_dataset = next(
                dataset
                for dataset in datasets
                if dataset.sheet == "PATIENT_ACCOUNT_CLAIMS"
            )
        except StopIteration as exc:
            raise CommandError(
                "Seed manifest does not contain PATIENT_ACCOUNT_CLAIMS."
            ) from exc

        claims_path = package_root / "csv" / claims_dataset.filename
        claims_header, claims_rows = self._read_csv(claims_path)
        required_claim_columns = {"id", "patient_id", "claim_code_hash"}
        if not required_claim_columns.issubset(claims_header):
            raise CommandError(
                f"{claims_dataset.filename} is missing required claim-code columns."
            )

        secure_path = package_root / "csv" / CLAIM_CODES_FILENAME
        secure_header, secure_rows = self._read_csv(secure_path)
        if secure_header != CLAIM_CODES_HEADER:
            raise CommandError(
                f"{CLAIM_CODES_FILENAME} header does not match the package contract."
            )
        if len(secure_rows) != claims_dataset.expected_rows:
            raise CommandError(
                f"{CLAIM_CODES_FILENAME} row count is {len(secure_rows)}, "
                f"expected {claims_dataset.expected_rows}."
            )

        claims_by_id: dict[str, tuple[int, dict[str, str]]] = {}
        for line_number, row in claims_rows:
            claim_id = row["id"].strip()
            if not claim_id:
                raise CommandError(
                    f"{claims_dataset.filename}:{line_number}: id is empty."
                )
            if claim_id in claims_by_id:
                raise CommandError(
                    f"{claims_dataset.filename}:{line_number}: duplicate claim id."
                )
            if row["claim_code_hash"] != CLAIM_HASH_PLACEHOLDER:
                raise CommandError(
                    f"{claims_dataset.filename}:{line_number}: claim_code_hash "
                    "is neither the pinned package placeholder nor a loader-generated hash."
                )
            claims_by_id[claim_id] = (line_number, row)

        secure_by_id: dict[str, tuple[int, dict[str, str]]] = {}
        seen_raw_codes: set[str] = set()
        for line_number, row in secure_rows:
            claim_id = row["claim_id"].strip()
            patient_id = row["patient_id"].strip()
            raw_code = row["raw_claim_code_synthetic"]
            if not claim_id or not patient_id or not raw_code:
                raise CommandError(
                    f"{CLAIM_CODES_FILENAME}:{line_number}: required value is empty."
                )
            if len(raw_code) != 6 or not raw_code.isdigit():
                raise CommandError(
                    f"{CLAIM_CODES_FILENAME}:{line_number}: synthetic claim code "
                    "must contain exactly six digits."
                )
            if claim_id in secure_by_id:
                raise CommandError(
                    f"{CLAIM_CODES_FILENAME}:{line_number}: duplicate claim_id."
                )
            if raw_code in seen_raw_codes:
                raise CommandError(
                    f"{CLAIM_CODES_FILENAME}:{line_number}: duplicate raw claim code."
                )
            if row["handling_rule"] != CLAIM_CODE_HANDLING_RULE:
                raise CommandError(
                    f"{CLAIM_CODES_FILENAME}:{line_number}: handling_rule does "
                    "not match the package contract."
                )
            secure_by_id[claim_id] = (line_number, row)
            seen_raw_codes.add(raw_code)

        if set(claims_by_id) != set(secure_by_id):
            raise CommandError(
                "Claim ids do not match between patient_account_claims.csv and "
                f"{CLAIM_CODES_FILENAME}."
            )

        hashes: dict[str, str] = {}
        seen_hashes: set[str] = set()
        for claim_id, (_line_number, secure_row) in secure_by_id.items():
            claims_line, claims_row = claims_by_id[claim_id]
            if secure_row["patient_id"] != claims_row["patient_id"]:
                raise CommandError(
                    f"{claims_dataset.filename}:{claims_line}: patient_id does "
                    f"not match {CLAIM_CODES_FILENAME}."
                )

            raw_code = secure_row["raw_claim_code_synthetic"]
            encoded = make_password(raw_code)
            if encoded in seen_hashes or not check_password(raw_code, encoded):
                raise CommandError(
                    "Django failed to create distinct, verifiable claim-code hashes."
                )
            hashes[claim_id] = encoded
            seen_hashes.add(encoded)

        self.stdout.write(
            "CLAIM_CODES_CONFIRMED rows="
            f"{len(hashes)} plaintext_persisted=false hashes=django"
        )
        return hashes

    def _prepare_user_password_hashes(
        self,
        package_root: Path,
        datasets: list[Dataset],
    ) -> dict[str, str]:
        try:
            users_dataset = next(
                dataset for dataset in datasets if dataset.sheet == "USERS"
            )
        except StopIteration as exc:
            raise CommandError("Seed manifest does not contain USERS.") from exc

        path = package_root / "csv" / users_dataset.filename
        header, rows = self._read_csv(path)
        if not {"id", "password_source"}.issubset(header):
            raise CommandError(
                f"{users_dataset.filename} is missing id or password_source."
            )

        hashes: dict[str, str] = {}
        seen_hashes: set[str] = set()
        self.stdout.write(
            f"USER_PASSWORD_HASHING_STARTED rows={len(rows)}"
        )
        for line_number, row in rows:
            user_id = row["id"].strip()
            source = row["password_source"].strip()
            env_name = PASSWORD_SOURCE_TO_ENV.get(source)
            if not user_id or env_name is None:
                raise CommandError(
                    f"{users_dataset.filename}:{line_number}: invalid id or "
                    "password_source."
                )
            if user_id in hashes:
                raise CommandError(
                    f"{users_dataset.filename}:{line_number}: duplicate user id."
                )
            raw_password = os.environ.get(env_name)
            if not raw_password:
                raise CommandError(
                    f"{users_dataset.filename}:{line_number}: {env_name} is not set."
                )
            encoded = make_password(raw_password)
            try:
                identify_hasher(encoded)
            except ValueError as exc:
                raise CommandError(
                    "Django produced an unrecognized user password hash."
                ) from exc
            if encoded in seen_hashes or not is_password_usable(encoded):
                raise CommandError(
                    "Django failed to create distinct, usable user password hashes."
                )
            hashes[user_id] = encoded
            seen_hashes.add(encoded)

        if len(hashes) != users_dataset.expected_rows:
            raise CommandError(
                f"Prepared {len(hashes)} user password hashes; expected "
                f"{users_dataset.expected_rows}."
            )
        self.stdout.write(
            "USER_PASSWORDS_CONFIRMED rows="
            f"{len(hashes)} plaintext_persisted=false hashes=django"
        )
        return hashes

    def _assert_models_compatible(
        self, package_root: Path, datasets: list[Dataset]
    ) -> None:
        seen_tables: dict[str, str] = {}
        prepared_rows: dict[
            str,
            tuple[
                Dataset,
                type[models.Model],
                list[tuple[int, dict[str, Any]]],
            ],
        ] = {}
        for dataset in datasets:
            model = self._get_model(dataset)
            table = model._meta.db_table
            if table in seen_tables:
                raise CommandError(
                    f"Datasets {seen_tables[table]} and {dataset.sheet} both target "
                    f"database table {table}."
                )
            seen_tables[table] = dataset.sheet

            path = package_root / "csv" / dataset.filename
            header, rows = self._read_csv(path)
            if len(rows) != dataset.expected_rows:
                raise CommandError(
                    f"{dataset.filename} row count is {len(rows)}, "
                    f"expected {dataset.expected_rows}."
                )
            field_map = self._column_field_map(dataset, model, header)
            converted_rows = [
                (
                    line_number,
                    self._converted_row_values(
                        dataset,
                        header,
                        row,
                        field_map,
                        line_number=line_number,
                    ),
                )
                for line_number, row in rows
            ]
            self._assert_dataset_unique_values(
                dataset,
                model,
                converted_rows,
            )
            self._assert_dataset_field_and_check_constraints(
                dataset,
                model,
                converted_rows,
            )
            prepared_rows[dataset.model_label] = (
                dataset,
                model,
                converted_rows,
            )

        self._assert_foreign_key_references(datasets, prepared_rows)

        self.stdout.write(
            "PREFLIGHT_CONFIRMED datasets="
            f"{len(datasets)} row_counts=OK fields=OK "
            "unique_constraints=OK foreign_keys=OK check_constraints=OK"
        )

    def _assert_dataset_unique_values(
        self,
        dataset: Dataset,
        model: type[models.Model],
        converted_rows: list[tuple[int, dict[str, Any]]],
    ) -> None:
        specifications: list[
            tuple[str, tuple[models.Field, ...], models.UniqueConstraint | None]
        ] = []

        for field in model._meta.concrete_fields:
            if field.primary_key or field.unique:
                specifications.append((
                    f"field {field.name!r}",
                    (field,),
                    None,
                ))

        for field_names in model._meta.unique_together:
            fields = tuple(model._meta.get_field(name) for name in field_names)
            specifications.append((
                "unique_together " + ",".join(field_names),
                fields,
                None,
            ))

        for constraint in model._meta.constraints:
            if not isinstance(constraint, models.UniqueConstraint):
                continue
            if not constraint.fields:
                raise CommandError(
                    f"{dataset.model_label} has expression-based unique "
                    f"constraint {constraint.name!r}; this loader refuses to "
                    "skip INSERT preflight for it."
                )
            fields = tuple(
                model._meta.get_field(name) for name in constraint.fields
            )
            specifications.append((
                f"constraint {constraint.name!r}",
                fields,
                constraint,
            ))

        for label, fields, constraint in specifications:
            seen: dict[tuple[Any, ...], int] = {}
            for line_number, values in converted_rows:
                if any(field.attname not in values for field in fields):
                    continue

                if constraint is not None and constraint.condition is not None:
                    against: dict[str, Any] = {}
                    for field in model._meta.concrete_fields:
                        value = values.get(
                            field.attname,
                            field.get_default() if field.has_default() else None,
                        )
                        output_field = (
                            field.target_field if field.is_relation else field
                        )
                        # Typed Value expressions are required for NULLs;
                        # otherwise Q.check() cannot infer an output field.
                        against[field.name] = models.Value(
                            value,
                            output_field=output_field,
                        )
                    try:
                        applies = constraint.condition.check(
                            against,
                            using=connection.alias,
                        )
                    except Exception as exc:
                        raise CommandError(
                            f"{dataset.filename}:{line_number}: cannot evaluate "
                            f"conditional unique constraint {constraint.name!r}: "
                            f"{type(exc).__name__}: {exc}"
                        ) from exc
                    if not applies:
                        continue

                key = tuple(
                    self._freeze_unique_value(values[field.attname])
                    for field in fields
                )
                nulls_distinct = (
                    getattr(constraint, "nulls_distinct", None)
                    if constraint is not None
                    else None
                )
                if any(value is None for value in key) and nulls_distinct is not False:
                    continue

                first_line = seen.get(key)
                if first_line is not None:
                    raise CommandError(
                        f"{dataset.filename}:{line_number}: duplicate value for "
                        f"{label}; first seen at line {first_line}. Values are "
                        "not printed."
                    )
                seen[key] = line_number

    def _assert_dataset_field_and_check_constraints(
        self,
        dataset: Dataset,
        model: type[models.Model],
        converted_rows: list[tuple[int, dict[str, Any]]],
    ) -> None:
        check_constraints = [
            constraint
            for constraint in model._meta.constraints
            if isinstance(constraint, models.CheckConstraint)
        ]
        relation_field_names = {
            field.name
            for field in model._meta.concrete_fields
            if field.is_relation
        }
        for line_number, values in converted_rows:
            obj = model(**values)
            try:
                # ForeignKey.clean() queries the target table.  Parent rows are
                # intentionally not inserted during preflight, so relational
                # existence is verified in one package-wide pass below.
                obj.clean_fields(exclude=relation_field_names)
            except ValidationError as exc:
                details = getattr(exc, "message_dict", None) or exc.messages
                raise CommandError(
                    f"{dataset.filename}:{line_number}: field validation failed "
                    f"for {dataset.model_label}: {details}"
                ) from exc

            for constraint in check_constraints:
                try:
                    constraint.validate(
                        model,
                        obj,
                        using=connection.alias,
                    )
                except ValidationError as exc:
                    raise CommandError(
                        f"{dataset.filename}:{line_number}: check constraint "
                        f"{constraint.name!r} failed."
                    ) from exc
                except Exception as exc:
                    raise CommandError(
                        f"{dataset.filename}:{line_number}: cannot evaluate "
                        f"check constraint {constraint.name!r}: "
                        f"{type(exc).__name__}: {exc}"
                    ) from exc

    def _assert_foreign_key_references(
        self,
        datasets: list[Dataset],
        prepared_rows: dict[
            str,
            tuple[
                Dataset,
                type[models.Model],
                list[tuple[int, dict[str, Any]]],
            ],
        ],
    ) -> None:
        sequence_by_label = {
            dataset.model_label: dataset.sequence for dataset in datasets
        }
        package_primary_keys: dict[str, set[Any]] = {}
        for model_label, (_dataset, model, rows) in prepared_rows.items():
            pk_attname = model._meta.pk.attname
            package_primary_keys[model_label] = {
                values[pk_attname]
                for _line_number, values in rows
                if pk_attname in values
            }

        for model_label, (dataset, model, rows) in prepared_rows.items():
            for field in model._meta.concrete_fields:
                if not field.is_relation or not (
                    getattr(field, "many_to_one", False)
                    or getattr(field, "one_to_one", False)
                ):
                    continue

                remote_model = field.remote_field.model
                remote_label = remote_model._meta.label
                first_line_by_value: dict[Any, int] = {}
                for line_number, values in rows:
                    value = values.get(field.attname)
                    if value is not None:
                        first_line_by_value.setdefault(value, line_number)

                if not first_line_by_value:
                    continue

                remote_package_values = package_primary_keys.get(remote_label, set())
                missing = set(first_line_by_value) - remote_package_values

                remote_sequence = sequence_by_label.get(remote_label)
                if (
                    remote_sequence is not None
                    and remote_sequence > dataset.sequence
                    and remote_label != model_label
                    and set(first_line_by_value) & remote_package_values
                ):
                    raise CommandError(
                        f"{dataset.filename}: foreign key {field.name!r} targets "
                        f"later dataset {remote_label}; load order is invalid."
                    )

                if missing:
                    existing = set(
                        remote_model._base_manager.filter(
                            pk__in=missing
                        ).values_list("pk", flat=True)
                    )
                    missing -= existing
                if missing:
                    first_missing = next(iter(missing))
                    raise CommandError(
                        f"{dataset.filename}:{first_line_by_value[first_missing]}: "
                        f"foreign key {field.name!r} has {len(missing)} reference(s) "
                        "missing from both the package and target database. Values "
                        "are not printed."
                    )

    def _freeze_unique_value(self, value: Any) -> Any:
        if isinstance(value, dict):
            return tuple(sorted(
                (key, self._freeze_unique_value(item))
                for key, item in value.items()
            ))
        if isinstance(value, (list, tuple)):
            return tuple(self._freeze_unique_value(item) for item in value)
        if isinstance(value, set):
            return tuple(sorted(self._freeze_unique_value(item) for item in value))
        return value

    def _assert_target_state(
        self,
        package_root: Path,
        datasets: list[Dataset],
        *,
        preserve_existing_superuser: bool,
    ) -> dict[str, int]:
        baseline_counts: dict[str, int] = {}
        nonempty_other: list[str] = []
        users_dataset: Dataset | None = None

        for dataset in datasets:
            model = self._get_model(dataset)
            count = model._base_manager.count()
            baseline_counts[dataset.model_label] = count
            if dataset.sheet == "USERS":
                users_dataset = dataset
            elif count:
                nonempty_other.append(f"{dataset.model_label}={count}")

        if nonempty_other:
            raise CommandError(
                "Refusing to load base seed because non-user target models are "
                "not empty: "
                + ", ".join(nonempty_other)
                + ". No rows were changed."
            )

        if users_dataset is None:
            raise CommandError("Seed manifest does not contain the USERS dataset.")

        user_count = baseline_counts[users_dataset.model_label]
        if user_count == 0:
            return baseline_counts

        if not preserve_existing_superuser:
            raise CommandError(
                "Refusing to load base seed because target models are not empty: "
                f"{users_dataset.model_label}={user_count}. No rows were changed. "
                "Use --preserve-existing-superuser only after confirming that the "
                "existing row is the Django administrator that must be retained."
            )

        if user_count != 1:
            raise CommandError(
                "--preserve-existing-superuser requires exactly one existing "
                f"accounts.User row, found {user_count}. No rows were changed."
            )

        self._assert_preservable_superuser(package_root, users_dataset)
        return baseline_counts

    def _assert_preservable_superuser(
        self,
        package_root: Path,
        dataset: Dataset,
    ) -> None:
        model = self._get_model(dataset)
        existing = model._base_manager.get()

        required_true = ("is_active", "is_staff", "is_superuser")
        missing_flags = [name for name in required_true if not hasattr(existing, name)]
        if missing_flags:
            raise CommandError(
                "Cannot verify the existing accounts.User as a Django "
                "administrator; missing fields: "
                + ", ".join(missing_flags)
                + ". No rows were changed."
            )
        invalid_flags = [name for name in required_true if not getattr(existing, name)]
        if invalid_flags:
            raise CommandError(
                "The existing accounts.User is not an active Django "
                "staff/superuser; false fields: "
                + ", ".join(invalid_flags)
                + ". No rows were changed."
            )

        path = package_root / "csv" / dataset.filename
        header, rows = self._read_csv(path)
        field_map = self._column_field_map(dataset, model, header)

        for column, field in field_map.items():
            if not (field.primary_key or field.unique):
                continue
            existing_value = getattr(existing, field.attname)
            if existing_value in (None, ""):
                continue
            for line_number, row in rows:
                seed_value = self._convert_value(
                    field,
                    row[column],
                    dataset.filename,
                    line_number,
                    column,
                )
                if seed_value == existing_value:
                    raise CommandError(
                        "The existing Django administrator conflicts with "
                        f"{dataset.filename}:{line_number} on unique field "
                        f"{field.name!r}. No rows were changed."
                    )

        self.stdout.write(
            "EXISTING_SUPERUSER_CONFIRMED count=1 active=true "
            "staff=true superuser=true unique_collisions=0"
        )

    def _load_dataset(
        self,
        package_root: Path,
        dataset: Dataset,
        *,
        baseline_count: int,
    ) -> int:
        model = self._get_model(dataset)
        path = package_root / "csv" / dataset.filename
        header, rows = self._read_csv(path)
        field_map = self._column_field_map(dataset, model, header)

        objects: list[models.Model] = []
        line_numbers: list[int] = []
        for line_number, row in rows:
            kwargs = self._converted_row_values(
                dataset,
                header,
                row,
                field_map,
                line_number=line_number,
            )
            assigned_fields = set(kwargs)

            obj = model(**kwargs)
            self._populate_missing_auto_values(
                obj,
                assigned_fields=assigned_fields,
                filename=dataset.filename,
                line_number=line_number,
            )
            if dataset.sheet == "USERS":
                self._set_seed_password(obj, row, dataset.filename, line_number)
            objects.append(obj)
            line_numbers.append(line_number)

        try:
            with self._preserve_csv_auto_timestamps(model):
                model._base_manager.bulk_create(objects, batch_size=200)
        except Exception as exc:
            raise CommandError(
                f"{dataset.filename}: PostgreSQL rejected the dataset insert: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

        for line_number, obj in zip(line_numbers, objects):
            try:
                # Scalar field validators and CheckConstraints were evaluated
                # package-wide before any INSERT.  PostgreSQL has now enforced
                # FK, UNIQUE and CHECK constraints set-wise.  Run only custom
                # model business rules here to avoid repeating thousands of
                # remote validation queries against the VM database.
                obj.clean()
            except ValidationError as exc:
                details = getattr(exc, "message_dict", None) or exc.messages
                raise CommandError(
                    f"{dataset.filename}:{line_number}: model clean failed for "
                    f"{dataset.model_label}: {details}"
                ) from exc

        actual_count = model._base_manager.count()
        expected_count = baseline_count + dataset.expected_rows
        if actual_count != expected_count:
            raise CommandError(
                f"{dataset.model_label} count is {actual_count} after load; "
                f"expected {expected_count} "
                f"({baseline_count} preserved + {dataset.expected_rows} loaded)."
            )
        return len(objects)

    def _verify_loaded_counts(
        self,
        datasets: list[Dataset],
        baseline_counts: dict[str, int],
    ) -> None:
        mismatches: list[str] = []
        for dataset in datasets:
            model = self._get_model(dataset)
            actual = model._base_manager.count()
            expected = baseline_counts[dataset.model_label] + dataset.expected_rows
            if actual != expected:
                mismatches.append(
                    f"{dataset.model_label}={actual}/{expected}"
                )
        if mismatches:
            raise CommandError(
                "Post-load count verification failed: " + ", ".join(mismatches)
            )

    def _column_field_map(
        self,
        dataset: Dataset,
        model: type[models.Model],
        header: list[str],
    ) -> dict[str, models.Field]:
        if not header or len(header) != len(set(header)):
            raise CommandError(
                f"{dataset.filename} has an empty or duplicate CSV header."
            )

        available: dict[str, models.Field] = {}
        for field in model._meta.concrete_fields:
            available[field.name] = field
            available[field.attname] = field

        field_map: dict[str, models.Field] = {}
        extras: set[str] = set()
        for column in header:
            field = available.get(column)
            if field is None:
                extras.add(column)
            else:
                field_map[column] = field

        allowed_extras = ALLOWED_NON_MODEL_COLUMNS.get(dataset.sheet, set())
        unexpected = extras - allowed_extras
        if unexpected:
            raise CommandError(
                f"{dataset.filename} has columns not present in "
                f"{dataset.model_label}: {sorted(unexpected)}"
            )

        provided_attnames = {field.attname for field in field_map.values()}
        missing_required: list[str] = []
        for field in model._meta.concrete_fields:
            if field.attname in provided_attnames:
                continue
            if dataset.sheet == "USERS" and field.name == "password":
                continue
            if (
                field.auto_created
                or field.has_default()
                or field.null
                or field.blank
                or getattr(field, "auto_now", False)
                or getattr(field, "auto_now_add", False)
                or getattr(field, "generated", False)
            ):
                continue
            missing_required.append(field.name)

        if missing_required:
            raise CommandError(
                f"{dataset.filename} is missing required model fields for "
                f"{dataset.model_label}: {sorted(missing_required)}"
            )
        return field_map

    def _converted_row_values(
        self,
        dataset: Dataset,
        header: list[str],
        row: dict[str, str],
        field_map: dict[str, models.Field],
        *,
        line_number: int,
    ) -> dict[str, Any]:
        values: dict[str, Any] = {}
        for column in header:
            field = field_map.get(column)
            if field is None:
                continue
            if field.attname in values:
                raise CommandError(
                    f"{dataset.filename}:{line_number}: multiple CSV columns "
                    f"target field {field.name!r}."
                )
            raw_value = row[column]
            if (
                dataset.sheet == "PATIENT_ACCOUNT_CLAIMS"
                and column == "claim_code_hash"
            ):
                claim_id = (row.get("id") or "").strip()
                try:
                    raw_value = self._claim_code_hashes[claim_id]
                except (AttributeError, KeyError) as exc:
                    raise CommandError(
                        f"{dataset.filename}:{line_number}: no verified Django "
                        "hash is available for this claim id."
                    ) from exc

            values[field.attname] = self._convert_value(
                field,
                raw_value,
                dataset.filename,
                line_number,
                column,
            )

        if dataset.sheet == "USERS":
            user_id = (row.get("id") or "").strip()
            try:
                values["password"] = self._user_password_hashes[user_id]
            except (AttributeError, KeyError) as exc:
                raise CommandError(
                    f"{dataset.filename}:{line_number}: no verified Django "
                    "password hash is available for this user id."
                ) from exc
        return values

    def _convert_value(
        self,
        field: models.Field,
        raw_value: str,
        filename: str,
        line_number: int,
        column: str,
    ) -> Any:
        value = raw_value if raw_value is not None else ""
        if value == "":
            if field.null:
                return None
            if isinstance(field, (models.CharField, models.TextField)):
                return ""
            if field.has_default():
                return field.get_default()
            raise CommandError(
                f"{filename}:{line_number}: non-null field {column!r} is empty."
            )

        try:
            if field.is_relation and (
                getattr(field, "many_to_one", False)
                or getattr(field, "one_to_one", False)
            ):
                return field.target_field.to_python(value)

            if isinstance(field, models.JSONField):
                return json.loads(value)

            if field.get_internal_type() == "ArrayField":
                parsed = json.loads(value)
                if not isinstance(parsed, list):
                    raise ValueError("ArrayField value must be a JSON list")
                return [field.base_field.to_python(item) for item in parsed]

            if isinstance(field, models.BooleanField):
                normalized = value.strip().lower()
                if normalized in {"1", "true", "t", "yes", "y"}:
                    return True
                if normalized in {"0", "false", "f", "no", "n"}:
                    return False
                raise ValueError("invalid boolean")

            converted = field.to_python(value)
            if (
                isinstance(field, models.DateTimeField)
                and converted is not None
                and settings.USE_TZ
                and timezone.is_naive(converted)
            ):
                converted = timezone.make_aware(
                    converted, timezone.get_default_timezone()
                )
            return converted
        except (TypeError, ValueError, ValidationError, json.JSONDecodeError) as exc:
            raise CommandError(
                f"{filename}:{line_number}: cannot convert column {column!r} "
                f"for Django field {field.name!r}."
            ) from exc

    def _set_seed_password(
        self,
        user: models.Model,
        row: dict[str, str],
        filename: str,
        line_number: int,
    ) -> None:
        user_id = (row.get("id") or "").strip()
        if not hasattr(user, "set_password"):
            raise CommandError(
                f"{filename}:{line_number}: accounts.User has no set_password()."
            )
        try:
            user.password = self._user_password_hashes[user_id]
        except (AttributeError, KeyError) as exc:
            raise CommandError(
                f"{filename}:{line_number}: no verified Django password hash "
                "is available for this user id."
            ) from exc

    def _populate_missing_auto_values(
        self,
        obj: models.Model,
        *,
        assigned_fields: set[str],
        filename: str,
        line_number: int,
    ) -> None:
        """Populate auto_now/auto_now_add fields omitted from a CSV row.

        The loader temporarily disables Django's automatic timestamp handling
        during bulk_create so that explicit historical CSV timestamps are not
        overwritten.  Fields omitted from the CSV must therefore be populated
        before that temporary override is applied.
        """
        for field in obj._meta.concrete_fields:
            auto_now = bool(getattr(field, "auto_now", False))
            auto_now_add = bool(getattr(field, "auto_now_add", False))
            if not (auto_now or auto_now_add):
                continue
            if field.attname in assigned_fields:
                continue

            value = field.pre_save(obj, add=True)
            if value is None and not field.null:
                raise CommandError(
                    f"{filename}:{line_number}: automatic field "
                    f"{field.name!r} produced NULL before insert."
                )
            setattr(obj, field.attname, value)
            assigned_fields.add(field.attname)

    @contextmanager
    def _preserve_csv_auto_timestamps(
        self, model: type[models.Model]
    ) -> Iterator[None]:
        states: list[tuple[models.Field, bool, bool]] = []
        for field in model._meta.concrete_fields:
            auto_now = bool(getattr(field, "auto_now", False))
            auto_now_add = bool(getattr(field, "auto_now_add", False))
            if auto_now or auto_now_add:
                states.append((field, auto_now, auto_now_add))
                field.auto_now = False
                field.auto_now_add = False
        try:
            yield
        finally:
            for field, auto_now, auto_now_add in states:
                field.auto_now = auto_now
                field.auto_now_add = auto_now_add

    def _get_model(self, dataset: Dataset) -> type[models.Model]:
        try:
            model = apps.get_model(dataset.app_label, dataset.model_name)
        except LookupError as exc:
            raise CommandError(
                f"Django model {dataset.model_label} is not installed."
            ) from exc
        if model is None:
            raise CommandError(
                f"Django model {dataset.model_label} is not installed."
            )
        return model

    def _read_json(self, path: Path) -> Any:
        if not path.is_file():
            raise CommandError(f"Required package file is missing: {path.name}")
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise CommandError(f"Cannot read valid JSON from {path.name}.") from exc

    def _read_csv(
        self, path: Path
    ) -> tuple[list[str], list[tuple[int, dict[str, str]]]]:
        if not path.is_file():
            raise CommandError(f"Required package file is missing: {path.name}")
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                header = list(reader.fieldnames or [])
                rows: list[tuple[int, dict[str, str]]] = []
                for line_number, raw_row in enumerate(reader, start=2):
                    if None in raw_row:
                        raise CommandError(
                            f"{path.name}:{line_number}: CSV row has extra columns."
                        )
                    row = {
                        key: (value if value is not None else "")
                        for key, value in raw_row.items()
                    }
                    if not any(value != "" for value in row.values()):
                        continue
                    rows.append((line_number, row))
                return header, rows
        except CommandError:
            raise
        except (OSError, UnicodeError, csv.Error) as exc:
            raise CommandError(f"Cannot read valid CSV from {path.name}.") from exc
