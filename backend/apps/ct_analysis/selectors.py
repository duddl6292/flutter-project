from .models import CTCase, InferenceJob


def visible_cases(user):
    queryset = CTCase.objects.select_related("patient", "created_by")
    if user.role == "PATIENT":
        return queryset.none()
    if user.role in {"CLINICIAN", "ADMIN"}:
        return queryset
    return queryset.none()


def visible_jobs(user):
    queryset = InferenceJob.objects.select_related("case", "case__patient", "requested_by")
    if user.role in {"CLINICIAN", "ADMIN"}:
        return queryset
    return queryset.none()
