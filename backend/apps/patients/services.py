import uuid

from django.db import transaction

from apps.accounts.models import User

from .models import Patient


@transaction.atomic
def create_patient(**data):
    suffix = uuid.uuid4().hex[:12]
    user = User.objects.create_user(
        username=f"patient-{suffix}", role=User.Role.PATIENT, is_active=False
    )
    return Patient.objects.create(
        user=user, medical_record_number=f"MRN-{suffix.upper()}", **data
    )
