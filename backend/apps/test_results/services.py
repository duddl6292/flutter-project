from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.notifications.models import Notification
from apps.notifications.services import create_notification

from .models import TestResult


@transaction.atomic
def release_test_result(result, clinician):
    result = TestResult.objects.select_for_update().select_related("patient__user").get(pk=result.pk)
    if result.status != TestResult.Status.FINAL:
        raise ValidationError("Only FINAL test results can be released.")
    if result.is_released_to_patient:
        return result
    result.is_released_to_patient = True
    result.released_at = timezone.now()
    result.released_by = clinician
    result.save(update_fields=("is_released_to_patient", "released_at", "released_by", "updated_at"))
    transaction.on_commit(lambda: create_notification(
        recipient=result.patient.user,
        type=Notification.Type.TEST_RESULT_READY,
        title="Test result ready",
        body=result.title,
        data={"test_result_id": str(result.id)},
        deduplication_key=f"test-result-ready:{result.id}",
    ))
    return result
