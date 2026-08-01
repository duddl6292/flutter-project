from __future__ import annotations

from typing import Any

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.clinicians.models import Clinician, Department
from apps.hospitals.models import Hospital
from apps.patients.models import Patient


User = get_user_model()


def issue_jwt_tokens(user: User) -> dict[str, str]:
    """
    로그인에 성공한 사용자에게 Access Token과 Refresh Token을 발급합니다.
    """

    refresh = RefreshToken.for_user(user)

    # JWT 내부에 역할 정보를 추가합니다.
    refresh["role"] = user.role

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def check_password_policy(
    password: str,
    user: User | None = None,
) -> None:
    """
    settings.py의 AUTH_PASSWORD_VALIDATORS 기준으로
    비밀번호를 검증합니다.
    """

    try:
        validate_password(password, user=user)
    except DjangoValidationError as exc:
        raise serializers.ValidationError(
            list(exc.messages)
        ) from exc


class PatientSignupSerializer(serializers.Serializer):
    """
    환자 회원가입 Serializer
    """

    username = serializers.CharField(
        max_length=150,
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
    )

    password_confirm = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )

    name = serializers.CharField(
        max_length=100,
    )

    birth_date = serializers.DateField()

    sex = serializers.ChoiceField(
        choices=[
            ("M", "남성"),
            ("F", "여성"),
            ("UNKNOWN", "미상"),
        ],
    )

    phone = serializers.CharField(
        max_length=30,
        required=False,
        allow_blank=True,
    )

    def validate_username(self, value: str) -> str:
        username = value.strip()

        if User.objects.filter(
            username=username,
        ).exists():
            raise serializers.ValidationError(
                "이미 사용 중인 아이디입니다."
            )

        # 의료진 면허번호와 충돌하지 않도록 제한합니다.
        if username.isdigit() and len(username) == 6:
            raise serializers.ValidationError(
                "숫자 6자리만으로 된 아이디는 사용할 수 없습니다."
            )

        return username

    def validate_password(self, value: str) -> str:
        check_password_policy(value)
        return value

    def validate(
        self,
        attrs: dict[str, Any],
    ) -> dict[str, Any]:
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({
                "password_confirm": "비밀번호가 일치하지 않습니다."
            })

        return attrs

    @transaction.atomic
    def create(
        self,
        validated_data: dict[str, Any],
    ) -> Patient:
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")

        name = validated_data.pop("name")
        birth_date = validated_data.pop("birth_date")
        sex = validated_data.pop("sex")
        phone = validated_data.pop("phone", "")

        # users 테이블에 계정을 저장합니다.
        user = User.objects.create_user(
            username=validated_data["username"],
            password=password,
            email=validated_data.get("email", ""),
            role=User.Role.PATIENT,
        )

        # patients 테이블에 환자 프로필을 저장합니다.
        patient = Patient.objects.create(
            user=user,
            name=name,
            birth_date=birth_date,
            sex=sex,
            phone=phone,
        )

        return patient


class PatientLoginSerializer(serializers.Serializer):
    """
    환자 로그인 Serializer
    """

    username = serializers.CharField(
        max_length=150,
    )

    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(
        self,
        attrs: dict[str, Any],
    ) -> dict[str, Any]:
        user = authenticate(
            username=attrs["username"],
            password=attrs["password"],
        )

        if user is None:
            raise serializers.ValidationError(
                "아이디 또는 비밀번호가 올바르지 않습니다."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "비활성화된 계정입니다."
            )

        if user.role != User.Role.PATIENT:
            raise serializers.ValidationError(
                "환자 계정이 아닙니다."
            )

        try:
            patient = Patient.objects.get(
                user=user,
            )
        except Patient.DoesNotExist as exc:
            raise serializers.ValidationError(
                "환자 프로필이 존재하지 않습니다."
            ) from exc

        tokens = issue_jwt_tokens(user)

        return {
            **tokens,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
            "patient": {
                "id": str(patient.id),
                "name": patient.name,
                "birth_date": (
                    patient.birth_date.isoformat()
                    if patient.birth_date
                    else None
                ),
                "sex": patient.sex,
                "phone": patient.phone,
            },
        }


class ClinicianSignupSerializer(serializers.Serializer):
    """
    의료진 회원가입 Serializer

    의료진은 다음 정보를 입력합니다.

    - 병원
    - 진료과
    - 면허번호 6자리
    - 비밀번호
    """

    name = serializers.CharField(
        max_length=100,
    )

    hospital_id = serializers.UUIDField()

    department_code = serializers.CharField(
        max_length=30,
    )

    license_number = serializers.RegexField(
        regex=r"^\d{6}$",
        error_messages={
            "invalid": "면허번호는 숫자 6자리여야 합니다."
        },
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
    )

    password_confirm = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )

    def validate_department_code(
        self,
        value: str,
    ) -> str:
        return value.strip().upper()

    def validate_license_number(
        self,
        value: str,
    ) -> str:
        if Clinician.objects.filter(
            license_number=value,
        ).exists():
            raise serializers.ValidationError(
                "이미 등록된 면허번호입니다."
            )

        if User.objects.filter(
            username=value,
        ).exists():
            raise serializers.ValidationError(
                "이미 등록된 의료진 계정입니다."
            )

        return value

    def validate_password(self, value: str) -> str:
        check_password_policy(value)
        return value

    def validate(
        self,
        attrs: dict[str, Any],
    ) -> dict[str, Any]:
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({
                "password_confirm": "비밀번호가 일치하지 않습니다."
            })

        hospital_exists = Hospital.objects.filter(
            id=attrs["hospital_id"],
            is_active=True,
        ).exists()

        if not hospital_exists:
            raise serializers.ValidationError({
                "hospital_id": "사용 가능한 병원을 찾을 수 없습니다."
            })

        department_exists = Department.objects.filter(
            code=attrs["department_code"],
            is_active=True,
        ).exists()

        if not department_exists:
            raise serializers.ValidationError({
                "department_code": "사용 가능한 진료과를 찾을 수 없습니다."
            })

        return attrs

    @transaction.atomic
    def create(
        self,
        validated_data: dict[str, Any],
    ) -> Clinician:
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")

        hospital_id = validated_data.pop("hospital_id")
        department_code = validated_data.pop(
            "department_code"
        )

        name = validated_data.pop("name")
        license_number = validated_data.pop(
            "license_number"
        )
        email = validated_data.pop("email", "")

        hospital = Hospital.objects.get(
            id=hospital_id,
            is_active=True,
        )

        department = Department.objects.get(
            code=department_code,
            is_active=True,
        )

        # 의료진은 면허번호를 로그인 ID로 사용합니다.
        user = User.objects.create_user(
            username=license_number,
            password=password,
            email=email,
            role=User.Role.CLINICIAN,
        )

        clinician = Clinician.objects.create(
            user=user,
            name=name,
            license_number=license_number,
            hospital=hospital,
            department=department,
            approval_status=(
                Clinician.ApprovalStatus.PENDING
            ),
        )

        return clinician


class ClinicianLoginSerializer(serializers.Serializer):
    """
    의료진 로그인 Serializer

    로그인 조건:
    - 병원
    - 진료과
    - 면허번호
    - 비밀번호
    """

    hospital_id = serializers.UUIDField()

    department_code = serializers.CharField(
        max_length=30,
    )

    license_number = serializers.RegexField(
        regex=r"^\d{6}$",
        error_messages={
            "invalid": "면허번호는 숫자 6자리여야 합니다."
        },
    )

    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate_department_code(
        self,
        value: str,
    ) -> str:
        return value.strip().upper()

    def validate(
        self,
        attrs: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            clinician = Clinician.objects.select_related(
                "user",
                "hospital",
                "department",
            ).get(
                hospital_id=attrs["hospital_id"],
                department__code=attrs["department_code"],
                license_number=attrs["license_number"],
            )
        except Clinician.DoesNotExist as exc:
            raise serializers.ValidationError(
                "병원, 진료과 또는 면허번호가 올바르지 않습니다."
            ) from exc

        user = authenticate(
            username=clinician.user.username,
            password=attrs["password"],
        )

        if user is None:
            raise serializers.ValidationError(
                "비밀번호가 올바르지 않습니다."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "비활성화된 계정입니다."
            )

        if user.role != User.Role.CLINICIAN:
            raise serializers.ValidationError(
                "의료진 계정이 아닙니다."
            )

        if (
            clinician.approval_status
            != Clinician.ApprovalStatus.APPROVED
        ):
            raise serializers.ValidationError(
                "아직 승인되지 않은 의료진 계정입니다."
            )

        tokens = issue_jwt_tokens(user)

        return {
            **tokens,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
            "clinician": {
                "id": str(clinician.id),
                "name": clinician.name,
                "license_number": (
                    clinician.license_number
                ),
                "approval_status": (
                    clinician.approval_status
                ),
                "hospital_id": str(
                    clinician.hospital_id
                ),
                "hospital_name": (
                    clinician.hospital.name
                ),
                "department_id": str(
                    clinician.department_id
                ),
                "department_code": (
                    clinician.department.code
                ),
                "department_name": (
                    clinician.department.name
                ),
            },
        }