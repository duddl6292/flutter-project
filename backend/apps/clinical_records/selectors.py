from .models import ClinicalRecord


def visible_clinical_records(user):
    queryset = ClinicalRecord.objects.select_related("patient", "clinician", "appointment")
    if user.role == "PATIENT":
        return queryset.filter(patient__user=user)
    if user.role == "CLINICIAN":
        return queryset.filter(clinician__user=user)
    if user.role == "ADMIN":
        return queryset
    return queryset.none()
