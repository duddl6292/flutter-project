from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import (
    NotificationPreferenceSerializer,
    NotificationSerializer,
    NotificationSettingSerializer,
    NotificationSettingsUpdateSerializer,
)
from .services import (
    get_allowed_notification_types,
    get_notification_preference,
    get_notification_setting,
)


def _notification_settings_data(user):
    setting = get_notification_setting(user=user)
    preferences = [
        get_notification_preference(
            user=user,
            notification_type=notification_type,
        )
        for notification_type in get_allowed_notification_types(user)
    ]

    return {
        "global_setting": NotificationSettingSerializer(
            setting,
        ).data,
        "preferences": NotificationPreferenceSerializer(
            preferences,
            many=True,
        ).data,
    }


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(
            recipient=request.user,
        )

        unread_only = (
            request.query_params
            .get("unread_only", "")
            .strip()
            .lower()
        )

        if unread_only in {"1", "true", "yes"}:
            notifications = notifications.filter(
                is_read=False,
            )

        unread_count = (
            Notification.objects
            .filter(
                recipient=request.user,
                is_read=False,
            )
            .count()
        )

        notifications = notifications[:50]

        serializer = NotificationSerializer(
            notifications,
            many=True,
        )

        return Response({
            "data": serializer.data,
            "meta": {
                "unread_count": unread_count,
            },
        })


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, notification_id):
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            recipient=request.user,
        )

        notification.mark_as_read()

        serializer = NotificationSerializer(
            notification,
        )

        return Response({
            "data": serializer.data,
        })


class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        read_at = timezone.now()

        updated_count = (
            Notification.objects
            .filter(
                recipient=request.user,
                is_read=False,
            )
            .update(
                is_read=True,
                read_at=read_at,
                updated_at=read_at,
            )
        )

        return Response({
            "data": {
                "updated_count": updated_count,
            },
        })


class NotificationSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "data": _notification_settings_data(request.user),
        })

    @transaction.atomic
    def patch(self, request):
        input_serializer = NotificationSettingsUpdateSerializer(
            data=request.data,
        )
        input_serializer.is_valid(raise_exception=True)

        user = (
            type(request.user).objects
            .select_for_update()
            .get(id=request.user.id)
        )
        validated_data = input_serializer.validated_data

        global_setting_data = validated_data.get(
            "global_setting",
        )

        if global_setting_data is not None:
            setting = get_notification_setting(user=user)
            setting_serializer = NotificationSettingSerializer(
                setting,
                data=global_setting_data,
                partial=True,
            )
            setting_serializer.is_valid(raise_exception=True)
            setting_serializer.save()

        allowed_types = set(
            get_allowed_notification_types(user)
        )

        for preference_data in validated_data.get(
            "preferences",
            [],
        ):
            notification_type = preference_data[
                "notification_type"
            ]

            if notification_type not in allowed_types:
                raise serializers.ValidationError({
                    "preferences": (
                        "사용자 역할에서 지원하지 않는 "
                        f"알림 유형입니다: {notification_type}"
                    ),
                })

            preference = get_notification_preference(
                user=user,
                notification_type=notification_type,
            )
            preference.push_enabled = preference_data[
                "push_enabled"
            ]
            preference.email_enabled = preference_data[
                "email_enabled"
            ]
            preference.save(
                update_fields=[
                    "push_enabled",
                    "email_enabled",
                    "updated_at",
                ],
            )

        return Response({
            "data": _notification_settings_data(user),
        })
