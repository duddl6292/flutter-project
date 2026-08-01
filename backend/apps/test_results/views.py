from rest_framework.decorators import action

from apps.core.permissions import ClinicianOrAdmin
from apps.core.responses import success
from apps.core.viewsets import WrappedModelViewSet

from .models import TestResult
from .selectors import visible_test_results
from .serializers import TestResultSerializer
from .services import release_test_result


class TestResultViewSet(WrappedModelViewSet):
    serializer_class = TestResultSerializer
    queryset = TestResult.objects.none()
    lookup_url_kwarg = "test_result_id"

    def get_queryset(self):
        return visible_test_results(self.request.user)

    def get_permissions(self):
        if self.action in {"create", "partial_update", "release"}:
            return [ClinicianOrAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.clinician)

    @action(detail=True, methods=("post",))
    def release(self, request, test_result_id=None):
        result = release_test_result(self.get_object(), request.user.clinician)
        return success(TestResultSerializer(result).data)
