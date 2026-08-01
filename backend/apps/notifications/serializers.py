from rest_framework import serializers

from .models import Device, Notification


class DeviceSerializer(serializers.ModelSerializer):
    device_id = serializers.UUIDField(source="id", read_only=True)
    class Meta:
        model = Device
        fields = ("notification_id", "patient_id", "type", "title", "body", "data", "is_read", "read_at", "created_at")
        read_only_fields = ("id", "user", "is_active", "registered_at", "last_used_at")


class NotificationSerializer(serializers.ModelSerializer):
    notification_id = serializers.UUIDField(source="id", read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__("apps.patients.models", fromlist=["Patient"]).Patient.objects.all(), write_only=True
    )
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ("is_read", "read_at", "created_at")
