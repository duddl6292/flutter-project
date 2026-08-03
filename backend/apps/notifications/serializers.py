from rest_framework import serializers

from .models import (
    Notification,
    NotificationPreference,
    NotificationSetting,
)


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


class NotificationPreferenceSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = NotificationPreference
        fields = [
            "notification_type",
            "push_enabled",
            "email_enabled",
        ]


class NotificationSettingSerializer(
    serializers.ModelSerializer
):
    quiet_hours_start = serializers.TimeField(
        allow_null=True,
        required=False,
        format="%H:%M",
        input_formats=["%H:%M", "%H:%M:%S"],
    )
    quiet_hours_end = serializers.TimeField(
        allow_null=True,
        required=False,
        format="%H:%M",
        input_formats=["%H:%M", "%H:%M:%S"],
    )

    class Meta:
        model = NotificationSetting
        fields = [
            "quiet_hours_enabled",
            "quiet_hours_start",
            "quiet_hours_end",
        ]

    def validate(self, attrs):
        instance = self.instance

        enabled = attrs.get(
            "quiet_hours_enabled",
            getattr(instance, "quiet_hours_enabled", False),
        )
        start = attrs.get(
            "quiet_hours_start",
            getattr(instance, "quiet_hours_start", None),
        )
        end = attrs.get(
            "quiet_hours_end",
            getattr(instance, "quiet_hours_end", None),
        )

        if (start is None) != (end is None):
            raise serializers.ValidationError(
                "방해금지 시작 시간과 종료 시간을 모두 입력해야 합니다."
            )

        if enabled and (start is None or end is None):
            raise serializers.ValidationError(
                "방해금지를 사용하려면 시작 시간과 종료 시간이 필요합니다."
            )

        if start is not None and start == end:
            raise serializers.ValidationError(
                "방해금지 시작 시간과 종료 시간은 달라야 합니다."
            )

        return attrs


class NotificationSettingsUpdateSerializer(
    serializers.Serializer
):
    global_setting = serializers.DictField(
        required=False,
    )
    preferences = NotificationPreferenceSerializer(
        many=True,
        required=False,
    )

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError(
                "변경할 알림 설정이 필요합니다."
            )

        preferences = attrs.get("preferences", [])
        notification_types = [
            item["notification_type"]
            for item in preferences
        ]

        if len(notification_types) != len(set(notification_types)):
            raise serializers.ValidationError({
                "preferences": "같은 알림 유형을 중복해서 보낼 수 없습니다.",
            })

        return attrs
