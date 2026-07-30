from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class BrainOnUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,
        ("BrainOn", {"fields": ("role", "created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")
    add_fieldsets = (
        *UserAdmin.add_fieldsets,
        ("BrainOn", {"fields": ("role",)}),
    )
