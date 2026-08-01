from .models import Prescription


def visible_prescriptions(user):
    queryset = Prescription.objects.select_related("patient", "clinician", "clinical_record").prefetch_related("items")
    if user.role == "PATIENT":
        return queryset.filter(patient__user=user)
    if user.role == "CLINICIAN":
        return queryset.filter(clinician__user=user)
    if user.role == "ADMIN":
        return queryset
    return queryset.none()
