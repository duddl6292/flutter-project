import logging
from typing import Any

from django.conf import settings
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler


logger = logging.getLogger("django.request")


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


def _first_message(data: Any) -> str | None:
    if isinstance(data, dict):
        if "detail" in data:
            message = _first_message(data["detail"])
            if message:
                return message
        for value in data.values():
            message = _first_message(value)
            if message:
                return message
        return None
    if isinstance(data, (list, tuple)):
        for value in data:
            message = _first_message(value)
            if message:
                return message
        return None
    if data is None:
        return None
    message = str(data).strip()
    return message or None


def _message(data: Any) -> str:
    return _first_message(data) or "요청 값을 확인해 주세요."


def api_exception_handler(
    exc: Exception,
    context: dict[str, Any],
) -> Response:
    response = exception_handler(exc, context)
    if response is None:
        request = context.get("request")
        logger.error(
            "Unhandled API exception: method=%s path=%s view=%s",
            getattr(request, "method", ""),
            getattr(request, "path", ""),
            context.get("view").__class__.__name__
            if context.get("view") is not None
            else "",
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        details = {}
        if settings.DEBUG:
            details = {
                "exception": type(exc).__name__,
                "message": str(exc),
            }
        return Response(
            {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "서버에서 요청을 처리하지 못했습니다.",
                    "details": details,
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
