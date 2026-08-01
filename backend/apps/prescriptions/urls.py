from django.urls import path
from .views import PrescriptionViewSet

urlpatterns = [
    path("prescriptions", PrescriptionViewSet.as_view({"get": "list", "post": "create"}), name="prescription-list"),
    path("prescriptions/<uuid:prescription_id>", PrescriptionViewSet.as_view({"get": "retrieve", "patch": "partial_update"}), name="prescription-detail"),
    path("prescriptions/<uuid:prescription_id>/discontinue", PrescriptionViewSet.as_view({"post": "discontinue"}), name="prescription-discontinue"),
]
