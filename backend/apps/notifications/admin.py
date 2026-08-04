from django.contrib import admin

from .models import (
    Device,
    Notification,
    NotificationPreference,
    NotificationSetting,
)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "platform",
        "client_type",
        "device_name",
        "app_version",
        "is_active",
        "last_used_at",
    )
    list_filter = (
        "platform",
        "client_type",
        "is_active",
    )
    search_fields = (
        "user__username",
        "device_identifier",
        "device_name",
        "fcm_token",
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "recipient",
        "type",
        "title",
        "is_read",
        "created_at",
    )
    list_filter = ("type", "is_read")
    search_fields = ("recipient__username", "title", "body")


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "notification_type",
        "push_enabled",
        "email_enabled",
    )
    list_filter = (
        "notification_type",
        "push_enabled",
        "email_enabled",
    )
    search_fields = ("user__username",)


@admin.register(NotificationSetting)
class NotificationSettingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "quiet_hours_enabled",
        "quiet_hours_start",
        "quiet_hours_end",
    )
    list_filter = ("quiet_hours_enabled",)
    search_fields = ("user__username",)
