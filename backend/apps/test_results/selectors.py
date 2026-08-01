from .models import TestResult


def visible_test_results(user):
    queryset = TestResult.objects.select_related("patient", "case", "created_by", "released_by")
    if user.role == "PATIENT":
        return queryset.filter(patient__user=user, status="FINAL", is_released_to_patient=True)
    if user.role in {"CLINICIAN", "ADMIN"}:
        return queryset
    return queryset.none()
