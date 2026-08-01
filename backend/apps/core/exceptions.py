import logging

from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def _code(exc):
    if isinstance(exc, exceptions.ValidationError):
        return "VALIDATION_ERROR"
    if isinstance(exc, exceptions.NotAuthenticated):
        return "AUTHENTICATION_FAILED"
    if isinstance(exc, exceptions.AuthenticationFailed):
        return "AUTHENTICATION_FAILED"
    if isinstance(exc, exceptions.PermissionDenied):
        return "PERMISSION_DENIED"
    if isinstance(exc, exceptions.NotFound):
        return "NOT_FOUND"
    if isinstance(exc, exceptions.Throttled):
        return "THROTTLED"
    return "API_ERROR"


def _message(data):
    if isinstance(data, dict) and "detail" in data:
        return str(data["detail"])
    if isinstance(data, list) and data:
        return str(data[0])
    if isinstance(data, dict):
        return "Request validation failed."
    return str(data)


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        logger.exception("unhandled_api_exception", exc_info=exc, extra={"view": str(context.get("view"))})
        return Response({"error": {"code": "INTERNAL_ERROR", "message": "An internal server error occurred.", "details": {}}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    details = response.data
    response.data = {"error": {"code": _code(exc), "message": _message(details), "details": details}}
    return response
