from django.urls import path
from .views import ClinicalRecordViewSet

urlpatterns = [
    path("clinical-records", ClinicalRecordViewSet.as_view({"get": "list", "post": "create"}), name="clinical-record-list"),
    path("clinical-records/<uuid:clinical_record_id>", ClinicalRecordViewSet.as_view({"get": "retrieve", "patch": "partial_update"}), name="clinical-record-detail"),
]
