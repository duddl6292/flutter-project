from rest_framework import serializers

from .models import Notification


class NotificationSerializer(
    serializers.ModelSerializer
):
    notification_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    class Meta:
        model = Notification
        fields = [
            "notification_id",
            "type",
            "title",
            "body",
            "data",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = fields
