from django.urls import path
from .views import ConsultationViewSet

urlpatterns = [
    path("consultations", ConsultationViewSet.as_view({"get": "list", "post": "create"}), name="consultation-list"),
    path("consultations/<uuid:consultation_id>", ConsultationViewSet.as_view({"get": "retrieve", "patch": "partial_update"}), name="consultation-detail"),
]
