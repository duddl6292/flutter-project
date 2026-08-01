from django.utils import timezone
from rest_framework.decorators import action

from apps.core.permissions import ClinicianOrAdmin
from apps.core.responses import success
from apps.core.viewsets import WrappedModelViewSet

from .models import Device, Notification
from .selectors import visible_notifications
from .serializers import DeviceSerializer, NotificationSerializer
from .services import create_notification


class DeviceViewSet(WrappedModelViewSet):
    serializer_class = DeviceSerializer
    lookup_url_kwarg = "device_id"
    http_method_names = ("post", "delete", "head", "options")

    def get_queryset(self):
        return Device.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        device, _ = Device.objects.update_or_create(
            fcm_token=data["fcm_token"],
            defaults={"user": request.user, "platform": data["platform"], "device_name": data.get("device_name", ""), "is_active": True, "last_used_at": timezone.now()},
        )
        return success(DeviceSerializer(device).data, status=201)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=("is_active",))


class NotificationViewSet(WrappedModelViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.none()
    lookup_url_kwarg = "notification_id"
    http_method_names = ("get", "post", "patch", "head", "options")

    def get_queryset(self):
        return visible_notifications(self.request.user)

    def get_permissions(self):
        if self.action == "create":
            return [ClinicianOrAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        data = dict(serializer.validated_data)
        patient = data.pop("patient_id")
        notification, _ = create_notification(recipient=patient.user, **data)
        serializer.instance = notification

    @action(detail=True, methods=("patch",))
    def read(self, request, notification_id=None):
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=("is_read", "read_at"))
        return success(NotificationSerializer(notification).data)

    @action(detail=False, methods=("patch",), url_path="read-all")
    def read_all(self, request):
        updated = self.get_queryset().filter(is_read=False).update(is_read=True, read_at=timezone.now())
        return success({"updated_count": updated})
