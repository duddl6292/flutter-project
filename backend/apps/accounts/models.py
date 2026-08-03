# backend/apps/accounts/models.py

import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    """BrainOn 사용자 계정 생성 관리자."""

    use_in_migrations = True

    def _create_user(
        self,
        username: str,
        password: str | None,
        **extra_fields,
    ):
        if not username:
            raise ValueError("로그인 아이디는 필수입니다.")

        username = self.model.normalize_username(username)

        email = extra_fields.get("email")
        if email:
            extra_fields["email"] = self.normalize_email(email)

        user = self.model(
            username=username,
            **extra_fields,
        )

        # 비밀번호를 평문으로 저장하지 않고 해시 처리
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(
        self,
        username: str,
        password: str | None = None,
        **extra_fields,
    ):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", User.Role.PATIENT)

        return self._create_user(
            username=username,
            password=password,
            **extra_fields,
        )

    def create_superuser(
        self,
        username: str,
        password: str | None = None,
        **extra_fields,
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", User.Role.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "관리자 계정은 is_staff=True여야 합니다."
            )

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "관리자 계정은 is_superuser=True여야 합니다."
            )

        return self._create_user(
            username=username,
            password=password,
            **extra_fields,
        )


class User(AbstractUser):
    """로그인 계정과 사용자 권한을 관리하는 모델."""

    class Role(models.TextChoices):
        PATIENT = "PATIENT", "환자"
        CLINICIAN = "CLINICIAN", "의료진"
        ADMIN = "ADMIN", "관리자"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="사용자 UUID",
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT,
        db_index=True,
        verbose_name="사용자 역할",
    )

    email = models.EmailField(
        blank=True,
        verbose_name="이메일",
    )

    created_at = models.DateTimeField(
    auto_now_add=True,
    verbose_name="생성 일시",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정 일시",
    )

    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = "사용자"
        verbose_name_plural = "사용자"

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"