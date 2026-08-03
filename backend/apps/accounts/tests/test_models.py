from django.test import TestCase

from apps.accounts.models import User


class UserModelTests(TestCase):
    def test_user_defaults_to_patient_role(self) -> None:
        user = User.objects.create_user(
            username="missing-role",
            password="test-pass",
        )

        self.assertEqual(user.role, User.Role.PATIENT)

    def test_each_role_can_be_created(self) -> None:
        for role in User.Role:
            user = User.objects.create_user(
                username=f"user-{role.value.lower()}",
                password="test-pass",
                role=role,
            )
            self.assertEqual(user.role, role)
