from .models import Appointment


def visible_appointments(user):
    queryset = Appointment.objects.select_related("patient", "clinician", "department")
    if user.role == "PATIENT":
        return queryset.filter(patient__user=user)
    if user.role == "CLINICIAN":
        return queryset.filter(clinician__user=user)
    if user.role == "ADMIN":
        return queryset
    return queryset.none()
