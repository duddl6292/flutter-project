from __future__ import annotations

from typing import Any

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import (ValidationError as DjangoValidationError,)
from django.db import transaction
from django.contrib.auth.hashers import check_password

from apps.notifications.models import Notification


from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.clinicians.models import Clinician, Department
from apps.hospitals.models import Hospital
from apps.patients.models import (Patient, PatientAccountClaim,)


User = get_user_model()

def normalize_phone(value: str) -> str:
    """
    전화번호 비교 시 하이픈·공백 등을 제거하고
    숫자만 반환합니다.
    """
    return "".join(
        character
        for character in value
        if character.isdigit()
    )

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


class AccountEmailUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(
        allow_blank=False,
    )

    def update(self, instance, validated_data):
        instance.email = validated_data["email"]
        instance.save(
            update_fields=[
                "email",
                "updated_at",
            ],
        )

        return instance


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user

        if not user.check_password(
            attrs["current_password"]
        ):
            raise serializers.ValidationError({
                "current_password": (
                    "현재 비밀번호가 올바르지 않습니다."
                ),
            })

        if (
            attrs["new_password"]
            != attrs["new_password_confirm"]
        ):
            raise serializers.ValidationError({
                "new_password_confirm": (
                    "새 비밀번호가 일치하지 않습니다."
                ),
            })

        if user.check_password(
            attrs["new_password"]
        ):
            raise serializers.ValidationError({
                "new_password": (
                    "현재 비밀번호와 다른 비밀번호를 사용해주세요."
                ),
            })

        check_password_policy(
            attrs["new_password"],
            user=user,
        )

        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(
            self.validated_data["new_password"]
        )
        user.save(
            update_fields=[
                "password",
                "updated_at",
            ],
        )

        return user


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

class PatientClaimSignupSerializer(serializers.Serializer):
    """
    병원에 이미 등록된 기존 환자가 모바일 앱에서
    BrainOn 계정을 생성하고 기존 Patient와 연결한다.

    새 Patient를 생성하지 않는다.
    """

    hospital_id = serializers.UUIDField()

    medical_record_number = serializers.CharField(
        max_length=50,
    )

    name = serializers.CharField(
        max_length=100,
    )

    birth_date = serializers.DateField()

    phone = serializers.CharField(
        max_length=30,
    )

    claim_code = serializers.RegexField(
        regex=r"^\d{6}$",
        trim_whitespace=True,
        error_messages={
            "invalid": "연결 코드는 숫자 6자리여야 합니다.",
        },
    )

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

    def validate_username(self, value: str) -> str:
        username = value.strip()

        if User.objects.filter(
            username=username,
        ).exists():
            raise serializers.ValidationError(
                "이미 사용 중인 아이디입니다."
            )

        if username.isdigit() and len(username) == 6:
            raise serializers.ValidationError(
                "숫자 6자리만으로 된 아이디는 사용할 수 없습니다."
            )

        return username

    def validate_medical_record_number(
        self,
        value: str,
    ) -> str:
        return value.strip()

    def validate_name(self, value: str) -> str:
        return value.strip()

    def validate_phone(self, value: str) -> str:
        value = value.strip()

        if not normalize_phone(value):
            raise serializers.ValidationError(
                "전화번호를 입력해 주세요."
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
                "password_confirm": (
                    "비밀번호가 일치하지 않습니다."
                ),
            })

        hospital = Hospital.objects.filter(
            id=attrs["hospital_id"],
            is_active=True,
        ).first()

        if hospital is None:
            raise serializers.ValidationError({
                "hospital_id": (
                    "사용 가능한 병원을 찾을 수 없습니다."
                ),
            })

        patient = (
            Patient.objects
            .select_related("user")
            .filter(
                medical_record_number=(
                    attrs["medical_record_number"]
                ),
            )
            .first()
        )

        if patient is None:
            raise serializers.ValidationError({
                "medical_record_number": (
                    "입력한 정보와 일치하는 기존 환자를 "
                    "찾을 수 없습니다."
                ),
            })

        if patient.status != Patient.Status.ACTIVE:
            raise serializers.ValidationError({
                "medical_record_number": (
                    "현재 계정을 연결할 수 없는 환자입니다."
                ),
            })

        if patient.user_id is not None:
            raise serializers.ValidationError({
                "medical_record_number": (
                    "이미 모바일 계정이 연결된 환자입니다."
                ),
            })

        identity_matches = (
            patient.name.strip() == attrs["name"]
            and patient.birth_date == attrs["birth_date"]
            and normalize_phone(patient.phone)
            == normalize_phone(attrs["phone"])
        )

        if not identity_matches:
            raise serializers.ValidationError({
                "patient_information": (
                    "환자번호, 이름, 생년월일 또는 "
                    "전화번호가 일치하지 않습니다."
                ),
            })

        has_hospital_appointment = (
            patient.appointments.filter(
                hospital=hospital,
            ).exists()
        )

        has_hospital_encounter = (
            patient.encounters.filter(
                hospital=hospital,
            ).exists()
        )

        if (
            not has_hospital_appointment
            and not has_hospital_encounter
        ):
            raise serializers.ValidationError({
                "hospital_id": (
                    "선택한 병원에서 해당 환자의 "
                    "예약 또는 진료이력을 찾을 수 없습니다."
                ),
            })

        claim = (
            PatientAccountClaim.objects
            .select_related("patient")
            .filter(
                patient=patient,
                status=PatientAccountClaim.Status.ISSUED,
            )
            .order_by("-created_at")
            .first()
        )

        if claim is None:
            raise serializers.ValidationError({
                "claim_code": (
                    "사용 가능한 환자 연결 코드가 없습니다."
                ),
            })

        if claim.is_expired:
            claim.mark_as_expired()

            raise serializers.ValidationError({
                "claim_code": (
                    "연결 코드가 만료되었습니다. "
                    "병원에서 다시 발급받아 주세요."
                ),
            })

        if claim.failed_attempts >= 5:
            claim.revoke()

            raise serializers.ValidationError({
                "claim_code": (
                    "인증 시도 횟수를 초과하여 "
                    "연결 코드가 취소되었습니다."
                ),
            })

        if not claim.check_claim_code(
            attrs["claim_code"]
        ):
            claim.refresh_from_db(
                fields=[
                    "failed_attempts",
                    "status",
                    "updated_at",
                ]
            )

            if (
                claim.failed_attempts >= 5
                and claim.status
                == PatientAccountClaim.Status.ISSUED
            ):
                claim.revoke()

                raise serializers.ValidationError({
                    "claim_code": (
                        "인증 시도 횟수를 초과하여 "
                        "연결 코드가 취소되었습니다."
                    ),
                })

            remaining_attempts = max(
                0,
                5 - claim.failed_attempts,
            )

            raise serializers.ValidationError({
                "claim_code": (
                    "연결 코드가 올바르지 않습니다. "
                    f"남은 시도 횟수: {remaining_attempts}회"
                ),
            })

        attrs["patient"] = patient
        attrs["claim"] = claim
        attrs["hospital"] = hospital

        return attrs

    @transaction.atomic
    def create(
        self,
        validated_data: dict[str, Any],
    ) -> dict[str, Any]:
        patient_id = validated_data["patient"].id
        claim_id = validated_data["claim"].id
        hospital = validated_data["hospital"]

        raw_claim_code = validated_data["claim_code"]
        username = validated_data["username"]
        password = validated_data["password"]
        email = validated_data.get("email", "")

        patient = (
            Patient.objects
            .select_for_update()
            .get(id=patient_id)
        )

        claim = (
            PatientAccountClaim.objects
            .select_for_update()
            .select_related("patient")
            .get(id=claim_id)
        )

        if patient.user_id is not None:
            raise serializers.ValidationError({
                "medical_record_number": (
                    "이미 모바일 계정이 연결된 환자입니다."
                ),
            })

        if (
            claim.status
            != PatientAccountClaim.Status.ISSUED
        ):
            raise serializers.ValidationError({
                "claim_code": (
                    "이미 사용되었거나 취소된 연결 코드입니다."
                ),
            })

        if claim.is_expired:
            raise serializers.ValidationError({
                "claim_code": "연결 코드가 만료되었습니다.",
            })

        if not check_password(
            raw_claim_code.strip(),
            claim.claim_code_hash,
        ):
            raise serializers.ValidationError({
                "claim_code": (
                    "연결 코드 검증 상태가 변경되었습니다. "
                    "다시 시도해 주세요."
                ),
            })

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            role=User.Role.PATIENT,
        )

        patient.user = user
        patient.save(
            update_fields=[
                "user",
                "updated_at",
            ]
        )

        # mark_as_used 내부에서 사용하는 patient 객체가
        # 방금 갱신한 객체를 참조하도록 설정
        claim.patient = patient

        try:
            claim.mark_as_used(user)
        except DjangoValidationError as exc:
            if hasattr(exc, "message_dict"):
                error_detail = exc.message_dict
            else:
                error_detail = {
                    "claim_code": exc.messages,
                }

            raise serializers.ValidationError(
                error_detail
            ) from exc

        Notification.objects.create(
            recipient=user,
            type=Notification.Type.SYSTEM,
            title="기존 진료정보 연결 완료",
            body=(
                f"{hospital.name}의 기존 진료정보가 "
                "BrainOn 계정에 연결되었습니다."
            ),
            data={
                "patient_id": str(patient.id),
                "hospital_id": str(hospital.id),
                "claim_id": str(claim.id),
                "route": "/home",
            },
            is_read=False,
            read_at=None,
            deduplication_key=(
                f"patient-claim-complete:{claim.id}"
            ),
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
            "patient": {
                "id": str(patient.id),
                "medical_record_number": (
                    patient.medical_record_number
                ),
                "name": patient.name,
                "birth_date": (
                    patient.birth_date.isoformat()
                    if patient.birth_date
                    else None
                ),
                "sex": patient.sex,
                "phone": patient.phone,
            },
            "hospital": {
                "id": str(hospital.id),
                "name": hospital.name,
            },
            "claim": {
                "id": str(claim.id),
                "status": claim.status,
                "used_at": (
                    claim.used_at.isoformat()
                    if claim.used_at
                    else None
                ),
            },
        }

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
