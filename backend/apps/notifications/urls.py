from django.urls import path
from .views import DeviceViewSet, NotificationViewSet

urlpatterns = [
    path("devices", DeviceViewSet.as_view({"post": "create"}), name="device-list"),
    path("devices/<uuid:device_id>", DeviceViewSet.as_view({"delete": "destroy"}), name="device-detail"),
    path("notifications", NotificationViewSet.as_view({"get": "list", "post": "create"}), name="notification-list"),
    path("notifications/read-all", NotificationViewSet.as_view({"patch": "read_all"}), name="notification-read-all"),
    path("notifications/<uuid:notification_id>/read", NotificationViewSet.as_view({"patch": "read"}), name="notification-read"),
]
