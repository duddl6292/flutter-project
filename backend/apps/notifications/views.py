from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


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
