from django.conf import settings
from django.db import models

from apps.core.models import UUIDModel


class Device(UUIDModel):
    class Platform(models.TextChoices):
        ANDROID = "ANDROID", "Android"
        IOS = "IOS", "iOS"
        WEB = "WEB", "Web"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="devices")
    platform = models.CharField(max_length=10, choices=Platform.choices)
    fcm_token = models.CharField(max_length=512, unique=True)
    device_name = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)


class Notification(UUIDModel):
    class Type(models.TextChoices):
        APPOINTMENT_REMINDER = "APPOINTMENT_REMINDER", "Appointment reminder"
        APPOINTMENT_CHANGED = "APPOINTMENT_CHANGED", "Appointment changed"
        MEDICATION_REMINDER = "MEDICATION_REMINDER", "Medication reminder"
        PRESCRIPTION_CREATED = "PRESCRIPTION_CREATED", "Prescription created"
        TEST_RESULT_READY = "TEST_RESULT_READY", "Test result ready"
        SYSTEM_NOTICE = "SYSTEM_NOTICE", "System notice"

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=32, choices=Type.choices)
    title = models.CharField(max_length=200)
    body = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    deduplication_key = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
