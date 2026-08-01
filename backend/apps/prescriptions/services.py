from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Prescription, PrescriptionItem


@transaction.atomic
def create_prescription(*, items, **prescription_data):
    prescription = Prescription.objects.create(**prescription_data)
    PrescriptionItem.objects.bulk_create(
        [PrescriptionItem(prescription=prescription, **item) for item in items]
    )
    return prescription


@transaction.atomic
def discontinue_prescription(prescription):
    prescription = Prescription.objects.select_for_update().get(pk=prescription.pk)
    if prescription.status == Prescription.Status.DISCONTINUED:
        raise ValidationError("Prescription is already discontinued.", code="CONFLICT")
    prescription.status = Prescription.Status.DISCONTINUED
    prescription.discontinued_at = timezone.now()
    prescription.save(update_fields=("status", "discontinued_at", "updated_at"))
    return prescription
