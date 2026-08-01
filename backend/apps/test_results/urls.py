from django.urls import path
from .views import TestResultViewSet

urlpatterns = [
    path("test-results", TestResultViewSet.as_view({"get": "list", "post": "create"}), name="test-result-list"),
    path("test-results/<uuid:test_result_id>", TestResultViewSet.as_view({"get": "retrieve", "patch": "partial_update"}), name="test-result-detail"),
    path("test-results/<uuid:test_result_id>/release", TestResultViewSet.as_view({"post": "release"}), name="test-result-release"),
]
