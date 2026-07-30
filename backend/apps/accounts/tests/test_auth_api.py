from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User


class AuthApiTests(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="patient-user",
            password="strong-test-password",
            role=User.Role.PATIENT,
            email="patient@example.test",
        )

    def _login(self, client_type: str = "MOBILE"):
        return self.client.post(
            "/api/v1/auth/login/",
            {
                "username": self.user.username,
                "password": "strong-test-password",
                "expected_role": User.Role.PATIENT,
                "client_type": client_type,
            },
            format="json",
        )

    def test_mobile_login_and_me(self) -> None:
        response = self._login()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )
        me_response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["role"], User.Role.PATIENT)
        self.assertNotIn("password", me_response.data)

    def test_wrong_expected_role_is_rejected(self) -> None:
        response = self.client.post(
            "/api/v1/auth/login/",
            {
                "username": self.user.username,
                "password": "strong-test-password",
                "expected_role": User.Role.CLINICIAN,
                "client_type": "MOBILE",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inactive_user_is_rejected(self) -> None:
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        response = self._login()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mobile_refresh_rotates_and_blacklists_old_token(self) -> None:
        login_response = self._login()
        old_refresh = login_response.data["refresh"]
        response = self.client.post(
            "/api/v1/auth/refresh/",
            {"refresh": old_refresh, "client_type": "MOBILE"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        second_response = self.client.post(
            "/api/v1/auth/refresh/",
            {"refresh": old_refresh, "client_type": "MOBILE"},
            format="json",
        )
        self.assertEqual(second_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_web_login_refresh_and_logout_use_cookie(self) -> None:
        login_response = self._login("WEB")
        self.assertNotIn("refresh", login_response.data)
        self.assertIn(settings.JWT_REFRESH_COOKIE_NAME, login_response.cookies)

        refresh_response = self.client.post(
            "/api/v1/auth/refresh/",
            {"client_type": "WEB"},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertNotIn("refresh", refresh_response.data)
        self.assertIn(settings.JWT_REFRESH_COOKIE_NAME, refresh_response.cookies)

        access = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        logout_response = self.client.post(
            "/api/v1/auth/logout/",
            {},
            format="json",
        )
        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_mobile_logout_blacklists_refresh(self) -> None:
        refresh = str(RefreshToken.for_user(self.user))
        response = self.client.post(
            "/api/v1/auth/logout/",
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        refresh_response = self.client.post(
            "/api/v1/auth/refresh/",
            {"refresh": refresh, "client_type": "MOBILE"},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
