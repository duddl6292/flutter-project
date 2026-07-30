from django.contrib.auth import authenticate
from django.db import models
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
        )


class LoginSerializer(serializers.Serializer):
    class ClientType(models.TextChoices):
        MOBILE = "MOBILE", "Mobile"
        WEB = "WEB", "Web"

    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    expected_role = serializers.ChoiceField(choices=User.Role.choices)
    client_type = serializers.ChoiceField(choices=ClientType.choices)

    def validate(self, attrs: dict[str, str]) -> dict[str, object]:
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["username"],
            password=attrs["password"],
        )
        if user is None or not user.is_active:
            raise AuthenticationFailed("사용자명 또는 비밀번호가 올바르지 않습니다.")
        if user.role != attrs["expected_role"]:
            raise AuthenticationFailed("선택한 역할과 계정 역할이 일치하지 않습니다.")

        refresh = RefreshToken.for_user(user)
        return {
            "user": user,
            "client_type": attrs["client_type"],
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=False, allow_blank=False)


class ClientTokenRefreshSerializer(TokenRefreshSerializer):
    client_type = serializers.ChoiceField(
        choices=LoginSerializer.ClientType.choices,
        required=False,
    )
