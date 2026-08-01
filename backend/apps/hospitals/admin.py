from django.contrib import admin

from .models import Hospital


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "hospital_code",
        "phone",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "hospital_code",
        "address",
        "phone",
    )

    list_filter = (
        "is_active",
    )

    ordering = (
        "name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )