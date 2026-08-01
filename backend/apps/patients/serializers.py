from __future__ import annotations

from typing import Any

from django.db import transaction
from rest_framework import serializers

from .models import Patient, ProvisionalIdentity


class PatientSummarySerializer(serializers.ModelSerializer):
    """
    의료진용 환자 목록에서 사용하는 간단한 환자 정보.
    """

    patient_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    class Meta:
        model = Patient
        fields = [
            "patient_id",
            "medical_record_number",
            "name",
            "birth_date",
            "sex",
            "phone",
            "status",
        ]


class PatientDetailSerializer(serializers.ModelSerializer):
    """
    환자 본인 조회 또는 의료진용 환자 상세 조회 Serializer.
    """

    patient_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    user_id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    merged_into_id = serializers.UUIDField(
        source="merged_into.id",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Patient
        fields = [
            "patient_id",
            "user_id",
            "username",
            "email",
            "medical_record_number",
            "name",
            "birth_date",
            "sex",
            "phone",
            "emergency_contact",
            "address",
            "status",
            "merged_into_id",
            "created_at",
            "updated_at",
        ]

    def get_user_id(self, obj: Patient) -> str | None:
        if obj.user_id is None:
            return None

        return str(obj.user_id)

    def get_username(self, obj: Patient) -> str | None:
        if obj.user is None:
            return None

        return obj.user.username

    def get_email(self, obj: Patient) -> str | None:
        if obj.user is None:
            return None

        return obj.user.email


class PatientUpdateSerializer(serializers.Serializer):
    """
    환자가 자신의 마이페이지에서 수정할 수 있는 정보.

    patient_id, user_id, 병원 환자번호, 환자 상태는
    이 API에서 수정하지 않습니다.
    """

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )

    phone = serializers.CharField(
        max_length=30,
        required=False,
        allow_blank=True,
    )

    emergency_contact = serializers.CharField(
        max_length=30,
        required=False,
        allow_blank=True,
    )

    address = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    @transaction.atomic
    def update(
        self,
        instance: Patient,
        validated_data: dict[str, Any],
    ) -> Patient:
        email = validated_data.pop("email", None)

        if email is not None:
            if instance.user is None:
                raise serializers.ValidationError({
                    "email": "연결된 사용자 계정이 없습니다."
                })

            instance.user.email = email
            instance.user.save(
                update_fields=[
                    "email",
                    "updated_at",
                ]
            )

        for field_name, value in validated_data.items():
            setattr(instance, field_name, value)

        if validated_data:
            instance.save(
                update_fields=[
                    *validated_data.keys(),
                    "updated_at",
                ]
            )

        return instance


class ProvisionalIdentitySerializer(
    serializers.ModelSerializer
):
    """
    신원미상 임시 신원 조회용 Serializer.
    """

    provisional_identity_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    resolved_patient_id = serializers.UUIDField(
        source="resolved_patient.id",
        read_only=True,
        allow_null=True,
    )

    resolved_by_id = serializers.UUIDField(
        source="resolved_by.id",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = ProvisionalIdentity
        fields = [
            "provisional_identity_id",
            "temporary_number",
            "temporary_name",
            "estimated_sex",
            "estimated_age",
            "distinguishing_features",
            "status",
            "resolved_patient_id",
            "resolved_at",
            "resolved_by_id",
            "created_at",
            "updated_at",
        ]


class ProvisionalIdentityCreateSerializer(
    serializers.ModelSerializer
):
    """
    신원미상 임시 신원 생성용 Serializer.
    """

    class Meta:
        model = ProvisionalIdentity
        fields = [
            "temporary_number",
            "temporary_name",
            "estimated_sex",
            "estimated_age",
            "distinguishing_features",
        ]

    def validate_temporary_number(
        self,
        value: str,
    ) -> str:
        value = value.strip().upper()

        if ProvisionalIdentity.objects.filter(
            temporary_number=value,
        ).exists():
            raise serializers.ValidationError(
                "이미 사용 중인 임시 환자번호입니다."
            )

        return value