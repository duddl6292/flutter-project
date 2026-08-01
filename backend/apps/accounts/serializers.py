from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from .models import User


class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source="id", read_only=True)
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("user_id", "username", "email", "first_name", "last_name", "name", "role")

    def get_name(self, obj):
        return obj.get_full_name() or obj.username


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        user = authenticate(request=self.context.get("request"), **attrs)
        if user is None or not user.is_active:
            raise AuthenticationFailed("Invalid username or password.")
        attrs["user"] = user
        return attrs


class RefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class LogoutSerializer(RefreshSerializer):
    pass


class PasswordResetSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
