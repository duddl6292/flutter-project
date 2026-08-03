from django.contrib import admin

from .models import Patient, ProvisionalIdentity


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "medical_record_number",
        "birth_date",
        "sex",
        "phone",
        "status",
        "created_at",
    )

    search_fields = (
        "name",
        "medical_record_number",
        "phone",
        "user__username",
        "user__email",
    )

    list_filter = (
        "status",
        "sex",
        "created_at",
    )

    ordering = (
        "name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "user",
        "merged_into",
    )


@admin.register(ProvisionalIdentity)
class ProvisionalIdentityAdmin(admin.ModelAdmin):
    list_display = (
        "temporary_number",
        "temporary_name",
        "estimated_sex",
        "estimated_age",
        "status",
        "resolved_patient",
        "created_at",
    )

    search_fields = (
        "temporary_number",
        "temporary_name",
        "distinguishing_features",
        "resolved_patient__name",
        "resolved_patient__medical_record_number",
    )

    list_filter = (
        "status",
        "estimated_sex",
        "created_at",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "resolved_patient",
        "resolved_by",
    )