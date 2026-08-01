# API implementation notes

## 2026-08-01 Django REST API implementation

- `contracts/openapi/public-api.yaml` and `contracts/openapi/inference-api.yaml` are treated as the authoritative contracts.
- The existing `backend/apps` namespace and `apps.core` common package were retained to avoid destructive project restructuring.
- Existing `PatientProfile` and `ClinicianProfile` models were superseded by contract models `Patient` and `Clinician`. The generated migrations preserve the prior migration history instead of deleting team-authored migrations.
- Major resource primary keys are UUID fields and domain states use uppercase `TextChoices` values.
- Public API paths intentionally omit trailing slashes because the contract paths omit them.
- Inference, storage, and notification delivery use selectable adapters. Local defaults are mock adapters; patient, appointment, prescription, and other clinical data always use Django ORM models.

## PostgreSQL verification pending

The current PostgreSQL server is unavailable. Implementation and validation therefore used Django's in-memory SQLite test settings where a database-backed test was useful, and `SimpleTestCase` for database-free checks. PostgreSQL migration success has not been claimed.

When PostgreSQL is available, run exactly:

```powershell
Set-Location backend
$env:DJANGO_SETTINGS_MODULE = "config.settings"
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test
Set-Location ..
python scripts/validate_contracts.py
```

The original migrations used integer primary keys before the UUID requirement was finalized. Migration `accounts.0002`, `patients.0002`, and `clinicians.0002` transition that history. Test these migrations against an empty PostgreSQL database before deployment. If a shared database already contains rows, create and review an explicit data migration rather than applying a blind primary-key conversion.
