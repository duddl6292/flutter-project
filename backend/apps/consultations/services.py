from django.db import transaction
from django.utils import timezone

from .models import Consultation


@transaction.atomic
def update_consultation(instance, validated_data):
    consultation = Consultation.objects.select_for_update().get(pk=instance.pk)
    for key, value in validated_data.items():
        setattr(consultation, key, value)
    if validated_data.get("status") == Consultation.Status.COMPLETED and not consultation.completed_at:
        consultation.completed_at = timezone.now()
    consultation.full_clean()
    consultation.save()
    return consultation
