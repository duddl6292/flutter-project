from django.db.models import Q

from .models import Patient


def visible_patients(user):
    queryset = Patient.objects.select_related("user", "merged_into")
    if user.role == "PATIENT":
        return queryset.filter(user=user)
    if user.role in {"CLINICIAN", "ADMIN"}:
        return queryset
    return queryset.none()


def search_patients(queryset, keyword):
    if not keyword:
        return queryset
    return queryset.filter(
        Q(name__icontains=keyword)
        | Q(medical_record_number__icontains=keyword)
        | Q(phone__icontains=keyword)
    )
