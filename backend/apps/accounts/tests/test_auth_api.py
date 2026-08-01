from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User


class AuthApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="patient-user", password="strong-test-password", role=User.Role.PATIENT)

    def _login(self):
        return self.client.post("/api/v1/auth/login", {"username": self.user.username, "password": "strong-test-password"}, format="json")

    def test_login_me_refresh_logout(self):
        response = self._login()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tokens = response.data["data"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access_token']}")
        me = self.client.get("/api/v1/users/me")
        self.assertEqual(me.data["data"]["role"], User.Role.PATIENT)
        refresh = self.client.post("/api/v1/auth/token/refresh", {"refresh_token": tokens["refresh_token"]}, format="json")
        self.assertEqual(refresh.status_code, status.HTTP_200_OK)
        logout = self.client.post("/api/v1/auth/logout", {"refresh_token": tokens["refresh_token"]}, format="json")
        self.assertEqual(logout.status_code, status.HTTP_200_OK)
        reused = self.client.post("/api/v1/auth/token/refresh", {"refresh_token": tokens["refresh_token"]}, format="json")
        self.assertEqual(reused.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_credentials_are_rejected(self):
        response = self.client.post("/api/v1/auth/login", {"username": self.user.username, "password": "wrong"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
