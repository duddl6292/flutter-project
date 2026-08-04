from rest_framework import serializers

from .models import (
    Device,
    Notification,
    NotificationPreference,
    NotificationSetting,
)


class DeviceSerializer(serializers.ModelSerializer):
    device_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    class Meta:
        model = Device
        fields = [
            "device_id",
            "platform",
            "client_type",
            "device_identifier",
            "device_name",
            "app_version",
            "is_active",
            "registered_at",
            "last_used_at",
        ]
        read_only_fields = fields


class DeviceRegisterSerializer(serializers.Serializer):
    platform = serializers.ChoiceField(
        choices=Device.Platform.choices,
    )
    client_type = serializers.ChoiceField(
        choices=Device.ClientType.choices,
    )
    device_identifier = serializers.CharField(
        max_length=255,
        trim_whitespace=True,
    )
    fcm_token = serializers.CharField(
        max_length=512,
        trim_whitespace=True,
    )
    device_name = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )
    app_version = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )

    def validate(self, attrs):
        platform = attrs["platform"]
        client_type = attrs["client_type"]

        web_client = (
            client_type
            == Device.ClientType.CLINICIAN_WEB
        )
        web_platform = (
            platform == Device.Platform.WEB
        )

        if web_client != web_platform:
            raise serializers.ValidationError({
                "platform": (
                    "의료진 웹은 WEB 플랫폼만, 앱은 "
                    "ANDROID 또는 IOS 플랫폼만 사용할 수 있습니다."
                ),
            })

        request = self.context.get("request")
        user_role = getattr(
            getattr(request, "user", None),
            "role",
            "",
        )

        allowed_client_types = {
            "PATIENT": {
                Device.ClientType.PATIENT_APP,
            },
            "CLINICIAN": {
                Device.ClientType.CLINICIAN_APP,
                Device.ClientType.CLINICIAN_WEB,
            },
        }

        if client_type not in allowed_client_types.get(
            user_role,
            set(),
        ):
            raise serializers.ValidationError({
                "client_type": (
                    "현재 사용자 역할에서 사용할 수 없는 "
                    "클라이언트 유형입니다."
                ),
            })

        return attrs


class DeviceUnregisterSerializer(serializers.Serializer):
    client_type = serializers.ChoiceField(
        choices=Device.ClientType.choices,
    )
    device_identifier = serializers.CharField(
        max_length=255,
        trim_whitespace=True,
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
