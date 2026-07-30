from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class ExceptionFormatTests(APITestCase):
    def test_protected_endpoint_uses_common_error_shape(self) -> None:
        response = self.client.get(reverse("auth-me"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["error"]["code"],
            "AUTHENTICATION_FAILED",
        )
        self.assertIn("message", response.data["error"])
        self.assertIn("details", response.data["error"])
