from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.exceptions import _message


class ExceptionFormatTests(APITestCase):
    def test_nested_validation_message_is_exposed(self) -> None:
        self.assertEqual(
            _message({
                "due_at": [
                    "답변 희망일은 현재보다 이후여야 합니다.",
                ],
            }),
            "답변 희망일은 현재보다 이후여야 합니다.",
        )

    def test_protected_endpoint_uses_common_error_shape(self) -> None:
        response = self.client.get("/api/v1/patients/me/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["error"]["code"],
            "AUTHENTICATION_FAILED",
        )
        self.assertIn("message", response.data["error"])
        self.assertIn("details", response.data["error"])
