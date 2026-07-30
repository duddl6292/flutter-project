from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin, IsClinician, IsPatient


class RolePermissionTests(TestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.view = APIView()

    def test_role_permissions_use_user_role(self) -> None:
        cases = (
            (User.Role.PATIENT, IsPatient, True),
            (User.Role.PATIENT, IsClinician, False),
            (User.Role.CLINICIAN, IsClinician, True),
            (User.Role.ADMIN, IsAdmin, True),
        )
        for index, (role, permission_class, expected) in enumerate(cases):
            user = User.objects.create_user(
                username=f"permission-{index}",
                password="test-pass",
                role=role,
            )
            request = self.factory.get("/")
            force_authenticate(request, user=user)
            drf_request = self.view.initialize_request(request)
            self.assertEqual(
                permission_class().has_permission(drf_request, self.view),
                expected,
            )
