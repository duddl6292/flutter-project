from django.contrib import admin

from .models import Clinician, Department



@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "is_active",
    )
    search_fields = (
        "code",
        "name",
    )
    list_filter = ("is_active",)
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )


@admin.register(Clinician)
class ClinicianAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "license_number",
        "hospital",
        "department",
        "approval_status",
    )
    search_fields = (
        "name",
        "license_number",
        "hospital__name",
    )
    list_filter = (
        "approval_status",
        "hospital",
        "department",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "approved_at",
    )