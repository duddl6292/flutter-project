from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.responses import success

from .serializers import (
    LoginSerializer, LogoutSerializer, PasswordResetSerializer,
    RefreshSerializer, UserSerializer,
)


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return success({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "token_type": "Bearer",
            "expires_in": int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
            "user": UserSerializer(user).data,
        })


class RefreshView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        jwt = TokenRefreshSerializer(data={"refresh": serializer.validated_data["refresh_token"]})
        try:
            jwt.is_valid(raise_exception=True)
        except TokenError as exc:
            raise AuthenticationFailed("Invalid refresh token.") from exc
        return success({
            "access_token": jwt.validated_data["access"],
            "token_type": "Bearer",
            "expires_in": int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        })


class LogoutView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data["refresh_token"]).blacklist()
        except TokenError:
            pass
        return success()


class MeView(APIView):
    def get(self, request):
        return success(UserSerializer(request.user).data)


class PasswordResetView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return success({"message": "If the account exists, reset instructions will be sent."})
