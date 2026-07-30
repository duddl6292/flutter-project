from typing import Any

from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def _error_code(exc: Exception) -> str:
    if isinstance(exc, exceptions.ValidationError):
        return "VALIDATION_ERROR"
    if isinstance(
        exc,
        (exceptions.AuthenticationFailed, exceptions.NotAuthenticated),
    ):
        return "AUTHENTICATION_FAILED"
    if isinstance(exc, exceptions.PermissionDenied):
        return "PERMISSION_DENIED"
    if isinstance(exc, exceptions.NotFound):
        return "NOT_FOUND"
    if isinstance(exc, exceptions.Throttled):
        return "THROTTLED"
    return "API_ERROR"


def _message(data: Any) -> str:
    if isinstance(data, dict):
        detail = data.get("detail")
        if detail is not None:
            return str(detail)
        return "요청 값을 확인해 주세요."
    if isinstance(data, list) and data:
        return str(data[0])
    return str(data)


def api_exception_handler(
    exc: Exception,
    context: dict[str, Any],
) -> Response:
    response = exception_handler(exc, context)
    if response is None:
        return Response(
            {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "서버에서 요청을 처리하지 못했습니다.",
                    "details": {},
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    original_data = response.data
    response.data = {
        "error": {
            "code": _error_code(exc),
            "message": _message(original_data),
            "details": original_data,
        }
    }
    return response
