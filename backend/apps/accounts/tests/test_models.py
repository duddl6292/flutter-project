from django.db import IntegrityError
from django.test import TestCase

from apps.accounts.models import User


class UserModelTests(TestCase):
    def test_user_requires_role(self) -> None:
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username="missing-role", password="test-pass")

    def test_each_role_can_be_created(self) -> None:
        for role in User.Role:
            user = User.objects.create_user(
                username=f"user-{role.value.lower()}",
                password="test-pass",
                role=role,
            )
            self.assertEqual(user.role, role)
