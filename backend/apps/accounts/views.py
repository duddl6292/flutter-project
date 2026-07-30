from typing import Any

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    ClientTokenRefreshSerializer,
    LoginSerializer,
    LogoutSerializer,
    UserSerializer,
)


def _set_refresh_cookie(response: Response, refresh: str) -> None:
    response.set_cookie(
        settings.JWT_REFRESH_COOKIE_NAME,
        refresh,
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        path="/api/v1/auth/",
    )


def _delete_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        settings.JWT_REFRESH_COOKIE_NAME,
        path="/api/v1/auth/",
        samesite=settings.JWT_COOKIE_SAMESITE,
    )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = data["user"]
        payload: dict[str, Any] = {
            "access": data["access"],
            "user": UserSerializer(user).data,
        }
        response = Response(payload, status=status.HTTP_200_OK)
        if data["client_type"] == LoginSerializer.ClientType.MOBILE:
            payload["refresh"] = data["refresh"]
        else:
            _set_refresh_cookie(response, str(data["refresh"]))
        return response


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        client_type = request.data.get(
            "client_type",
            LoginSerializer.ClientType.WEB
            if settings.JWT_REFRESH_COOKIE_NAME in request.COOKIES
            else LoginSerializer.ClientType.MOBILE,
        )
        refresh = (
            request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
            if client_type == LoginSerializer.ClientType.WEB
            else request.data.get("refresh")
        )
        serializer = ClientTokenRefreshSerializer(
            data={"refresh": refresh, "client_type": client_type}
        )
        try:
            serializer.is_valid(raise_exception=True)
        except (InvalidToken, TokenError) as exc:
            raise AuthenticationFailed("Refresh Token이 유효하지 않습니다.") from exc
        payload = dict(serializer.validated_data)
        payload.pop("client_type", None)
        response = Response(payload, status=status.HTTP_200_OK)
        rotated_refresh = payload.get("refresh")
        if client_type == LoginSerializer.ClientType.WEB:
            payload.pop("refresh", None)
            if rotated_refresh:
                _set_refresh_cookie(response, str(rotated_refresh))
        return response


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = serializer.validated_data.get("refresh") or request.COOKIES.get(
            settings.JWT_REFRESH_COOKIE_NAME
        )
        if refresh:
            try:
                RefreshToken(refresh).blacklist()
            except TokenError:
                pass
        response = Response(status=status.HTTP_204_NO_CONTENT)
        _delete_refresh_cookie(response)
        return response


class MeView(APIView):
    def get(self, request: Request) -> Response:
        return Response(UserSerializer(request.user).data)
