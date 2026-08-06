import secrets
from datetime import timedelta
from typing import Any

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.hospitals.models import (Hospital, PatientFavoriteHospital,)
from apps.notifications.models import Notification
from .models import (Patient, PatientAccountClaim, PatientIdentityResolutionLog, ProvisionalIdentity, )
from apps.appointments.models import Appointment, Encounter
from apps.medications.models import (
    MedicationRecord,
    MedicationSchedule,
)
from apps.prescriptions.models import (
    Prescription,
    PrescriptionItem,
)
from apps.test_results.models import TestResult

from .access import patient_access_scope


def _serialized_access_scope(serializer, patient):
    request = serializer.context.get("request")
    if request is not None and request.user.role == "ADMIN":
        return "ADMIN"
    return patient_access_scope(patient)


def _serialized_consultation_id(patient):
    value = getattr(patient, "_shared_consultation_id", None)
    return str(value) if value else None

class PatientSummarySerializer(serializers.ModelSerializer):
    """
    의료진용 환자 목록에서 사용하는 간단한 환자 정보.
    """

    patient_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )
    access_scope = serializers.SerializerMethodField()
    shared_consultation_id = serializers.SerializerMethodField()
    access_expires_at = serializers.SerializerMethodField()

    def get_access_scope(self, obj):
        return _serialized_access_scope(self, obj)

    def get_shared_consultation_id(self, obj):
        return _serialized_consultation_id(obj)

    def get_access_expires_at(self, obj):
        return getattr(obj, "_shared_access_expires_at", None)

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
            "access_scope",
            "shared_consultation_id",
            "access_expires_at",
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
    access_scope = serializers.SerializerMethodField()
    shared_consultation_id = serializers.SerializerMethodField()
    access_expires_at = serializers.SerializerMethodField()

    def get_access_scope(self, obj):
        return _serialized_access_scope(self, obj)

    def get_shared_consultation_id(self, obj):
        return _serialized_consultation_id(obj)

    def get_access_expires_at(self, obj):
        return getattr(obj, "_shared_access_expires_at", None)

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
            "access_scope",
            "shared_consultation_id",
            "access_expires_at",
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

class PatientMedicalHistorySerializer(
    serializers.ModelSerializer
):
    """
    로그인 환자에게 제공하는 통합 진료이력 요약.

    신원미상 상태에서 발생했더라도 신원확인 후
    Encounter.patient이 정식 환자로 변경된 진료는
    동일한 목록에 포함된다.
    """

    encounter_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    encounter_type_label = serializers.CharField(
        source="get_encounter_type_display",
        read_only=True,
    )

    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    hospital_id = serializers.UUIDField(
        source="hospital.id",
        read_only=True,
        allow_null=True,
    )

    hospital_name = serializers.CharField(
        source="hospital.name",
        read_only=True,
        allow_null=True,
    )

    department_id = serializers.UUIDField(
        source="department.id",
        read_only=True,
    )

    department_code = serializers.CharField(
        source="department.code",
        read_only=True,
    )

    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )

    clinician_id = serializers.UUIDField(
        source="attending_clinician.id",
        read_only=True,
    )

    clinician_name = serializers.CharField(
        source="attending_clinician.name",
        read_only=True,
    )

    appointment_id = serializers.UUIDField(
        source="appointment.id",
        read_only=True,
        allow_null=True,
    )

    event_at = serializers.SerializerMethodField()

    class Meta:
        model = Encounter
        fields = [
            "encounter_id",
            "encounter_number",
            "encounter_type",
            "encounter_type_label",
            "status",
            "status_label",
            "hospital_id",
            "hospital_name",
            "department_id",
            "department_code",
            "department_name",
            "clinician_id",
            "clinician_name",
            "appointment_id",
            "arrived_at",
            "started_at",
            "completed_at",
            "event_at",
            "created_at",
        ]

    def get_event_at(
        self,
        obj: Encounter,
    ) -> str:
        """
        화면의 진료 타임라인 정렬·표시에 사용할 대표 일시.
        """
        event_at = (
            obj.completed_at
            or obj.started_at
            or obj.arrived_at
            or obj.created_at
        )

        return event_at.isoformat()

class PatientAppointmentSerializer(
    serializers.ModelSerializer
):
    """
    로그인 환자용 예약 조회 Serializer.
    """

    appointment_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    hospital_id = serializers.UUIDField(
        source="hospital.id",
        read_only=True,
        allow_null=True,
    )

    hospital_name = serializers.CharField(
        source="hospital.name",
        read_only=True,
        allow_null=True,
    )

    department_id = serializers.UUIDField(
        source="department.id",
        read_only=True,
    )

    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )

    clinician_id = serializers.UUIDField(
        source="clinician.id",
        read_only=True,
    )

    clinician_name = serializers.CharField(
        source="clinician.name",
        read_only=True,
    )

    class Meta:
        model = Appointment
        fields = [
            "appointment_id",
            "hospital_id",
            "hospital_name",
            "department_id",
            "department_name",
            "clinician_id",
            "clinician_name",
            "scheduled_at",
            "location",
            "reason",
            "status",
            "status_label",
            "cancelled_at",
            "cancellation_reason",
            "created_at",
        ]


class PatientReleasedTestResultSerializer(
    serializers.ModelSerializer
):
    """
    의료진이 환자에게 공개한 공식 검사결과.
    """

    test_result_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    encounter_id = serializers.UUIDField(
        source="encounter.id",
        read_only=True,
    )

    hospital_id = serializers.UUIDField(
        source="encounter.hospital.id",
        read_only=True,
        allow_null=True,
    )

    hospital_name = serializers.CharField(
        source="encounter.hospital.name",
        read_only=True,
        allow_null=True,
    )

    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    has_result_file = serializers.SerializerMethodField()

    class Meta:
        model = TestResult
        fields = [
            "test_result_id",
            "encounter_id",
            "hospital_id",
            "hospital_name",
            "test_type",
            "title",
            "performed_at",
            "status",
            "status_label",
            "summary",
            "clinician_comment",
            "released_at",
            "has_result_file",
        ]

    def get_has_result_file(
        self,
        obj: TestResult,
    ) -> bool:
        return bool(obj.result_file_uri)


class PatientPrescriptionItemSerializer(
    serializers.ModelSerializer
):
    """
    환자에게 제공하는 처방 약품 정보.
    """

    prescription_item_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    class Meta:
        model = PrescriptionItem
        fields = [
            "prescription_item_id",
            "medicine_name",
            "dosage",
            "dose_unit",
            "frequency",
            "route",
            "instructions",
            "start_date",
            "end_date",
        ]


class PatientPrescriptionSerializer(
    serializers.ModelSerializer
):
    """
    로그인 환자용 처방전 조회 Serializer.
    """

    prescription_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    encounter_id = serializers.UUIDField(
        source="encounter.id",
        read_only=True,
    )

    hospital_id = serializers.UUIDField(
        source="encounter.hospital.id",
        read_only=True,
        allow_null=True,
    )

    hospital_name = serializers.CharField(
        source="encounter.hospital.name",
        read_only=True,
        allow_null=True,
    )

    clinician_id = serializers.UUIDField(
        source="clinician.id",
        read_only=True,
    )

    clinician_name = serializers.CharField(
        source="clinician.name",
        read_only=True,
    )

    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    items = PatientPrescriptionItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Prescription
        fields = [
            "prescription_id",
            "encounter_id",
            "hospital_id",
            "hospital_name",
            "clinician_id",
            "clinician_name",
            "status",
            "status_label",
            "notes",
            "prescribed_at",
            "discontinued_at",
            "items",
        ]


class PatientMedicationScheduleSerializer(
    serializers.ModelSerializer
):
    """
    환자의 복약 예정 시간과 반복 요일.
    """

    schedule_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    prescription_id = serializers.UUIDField(
        source="prescription_item.prescription.id",
        read_only=True,
    )

    prescription_item_id = serializers.UUIDField(
        source="prescription_item.id",
        read_only=True,
    )

    medicine_name = serializers.CharField(
        source="prescription_item.medicine_name",
        read_only=True,
    )

    dosage = serializers.DecimalField(
        source="prescription_item.dosage",
        max_digits=12,
        decimal_places=4,
        read_only=True,
    )

    dose_unit = serializers.CharField(
        source="prescription_item.dose_unit",
        read_only=True,
    )

    frequency = serializers.CharField(
        source="prescription_item.frequency",
        read_only=True,
    )

    instructions = serializers.CharField(
        source="prescription_item.instructions",
        read_only=True,
    )

    hospital_id = serializers.UUIDField(
        source=(
            "prescription_item.prescription."
            "encounter.hospital.id"
        ),
        read_only=True,
        allow_null=True,
    )

    hospital_name = serializers.CharField(
        source=(
            "prescription_item.prescription."
            "encounter.hospital.name"
        ),
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = MedicationSchedule
        fields = [
            "schedule_id",
            "prescription_id",
            "prescription_item_id",
            "hospital_id",
            "hospital_name",
            "medicine_name",
            "dosage",
            "dose_unit",
            "frequency",
            "instructions",
            "dose_time",
            "days_of_week",
            "start_date",
            "end_date",
            "is_active",
        ]


class PatientMedicationRecordSerializer(
    serializers.ModelSerializer
):
    """
    환자의 실제 복약 완료·미복용 기록.
    """

    medication_record_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    schedule_id = serializers.UUIDField(
        source="schedule.id",
        read_only=True,
    )

    prescription_item_id = serializers.UUIDField(
        source="prescription_item.id",
        read_only=True,
    )

    medicine_name = serializers.CharField(
        source="prescription_item.medicine_name",
        read_only=True,
    )

    dose_unit = serializers.CharField(
        source="prescription_item.dose_unit",
        read_only=True,
    )

    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = MedicationRecord
        fields = [
            "medication_record_id",
            "schedule_id",
            "prescription_item_id",
            "medicine_name",
            "dose_unit",
            "scheduled_at",
            "taken_at",
            "status",
            "status_label",
            "note",
        ]

class PatientFavoriteHospitalSerializer(
    serializers.ModelSerializer
):
    """
    로그인 환자의 찜 병원 조회 응답.
    """

    favorite_hospital_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    hospital_id = serializers.UUIDField(
        source="hospital.id",
        read_only=True,
    )

    hospital_code = serializers.CharField(
        source="hospital.hospital_code",
        read_only=True,
        allow_null=True,
    )

    hospital_name = serializers.CharField(
        source="hospital.name",
        read_only=True,
    )

    address = serializers.CharField(
        source="hospital.address",
        read_only=True,
    )

    phone = serializers.CharField(
        source="hospital.phone",
        read_only=True,
    )

    is_active = serializers.BooleanField(
        source="hospital.is_active",
        read_only=True,
    )

    favorited_at = serializers.DateTimeField(
        source="created_at",
        read_only=True,
    )

    class Meta:
        model = PatientFavoriteHospital
        fields = [
            "favorite_hospital_id",
            "hospital_id",
            "hospital_code",
            "hospital_name",
            "address",
            "phone",
            "is_active",
            "favorited_at",
        ]


class PatientFavoriteHospitalCreateSerializer(
    serializers.Serializer
):
    """
    로그인 환자가 활성 병원을 찜 목록에 추가한다.
    """

    hospital_id = serializers.UUIDField()

    def validate(
        self,
        attrs: dict[str, Any],
    ) -> dict[str, Any]:
        patient: Patient = self.context["patient"]

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

        if PatientFavoriteHospital.objects.filter(
            patient=patient,
            hospital=hospital,
        ).exists():
            raise serializers.ValidationError({
                "hospital_id": (
                    "이미 찜한 병원입니다."
                ),
            })

        attrs["hospital"] = hospital

        return attrs

    def create(
        self,
        validated_data: dict[str, Any],
    ) -> PatientFavoriteHospital:
        patient: Patient = self.context["patient"]
        hospital: Hospital = validated_data["hospital"]

        favorite_hospital, created = (
            PatientFavoriteHospital.objects.get_or_create(
                patient=patient,
                hospital=hospital,
            )
        )

        # 동시에 동일 병원 찜 요청이 들어온 경우에도
        # DB UniqueConstraint 기준으로 중복 생성을 차단한다.
        if not created:
            raise serializers.ValidationError({
                "hospital_id": (
                    "이미 찜한 병원입니다."
                ),
            })

        return favorite_hospital

class PatientNotificationSerializer(
    serializers.ModelSerializer
):
    """
    로그인 환자의 앱 알림 조회 응답.

    내부 중복 방지 키는 환자에게 반환하지 않는다.
    """

    notification_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    type_label = serializers.CharField(
        source="get_type_display",
        read_only=True,
    )

    class Meta:
        model = Notification
        fields = [
            "notification_id",
            "type",
            "type_label",
            "title",
            "body",
            "data",
            "is_read",
            "read_at",
            "created_at",
        ]


class PatientCTResultSerializer(
    serializers.ModelSerializer
):
    """
    의료진 검토 후 공개된 환자용 CT 결과.

    AI 원본 파일 URI와 기술 지표는 반환하지 않는다.
    """

    test_result_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    case_id = serializers.UUIDField(
        source="case.id",
        read_only=True,
    )

    encounter_id = serializers.UUIDField(
        source="encounter.id",
        read_only=True,
    )

    hospital_id = serializers.UUIDField(
        source="encounter.hospital.id",
        read_only=True,
        allow_null=True,
    )

    hospital_name = serializers.CharField(
        source="encounter.hospital.name",
        read_only=True,
        allow_null=True,
    )

    study_type = serializers.CharField(
        source="case.study_type",
        read_only=True,
    )

    study_type_label = serializers.CharField(
        source="case.get_study_type_display",
        read_only=True,
    )

    analysis_status = serializers.CharField(
        source="case.status",
        read_only=True,
    )

    analysis_status_label = serializers.CharField(
        source="case.get_status_display",
        read_only=True,
    )

    has_report_file = serializers.SerializerMethodField()

    class Meta:
        model = TestResult
        fields = [
            "test_result_id",
            "case_id",
            "encounter_id",
            "hospital_id",
            "hospital_name",
            "study_type",
            "study_type_label",
            "analysis_status",
            "analysis_status_label",
            "title",
            "performed_at",
            "summary",
            "clinician_comment",
            "released_at",
            "has_report_file",
        ]

    def get_has_report_file(
        self,
        obj: TestResult,
    ) -> bool:
        return bool(obj.result_file_uri)


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

class NewPatientChartSerializer(serializers.Serializer):
    """
    신원미상 환자의 신원확인 후
    신규 Patient 차트를 생성할 때 사용하는 정보.
    """

    medical_record_number = serializers.CharField(
        max_length=50,
    )

    name = serializers.CharField(
        max_length=100,
    )

    birth_date = serializers.DateField()

    sex = serializers.ChoiceField(
        choices=Patient.Sex.choices,
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

    def validate_medical_record_number(
        self,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "환자번호를 입력해 주세요."
            )

        if Patient.objects.filter(
            medical_record_number=value,
        ).exists():
            raise serializers.ValidationError(
                "이미 사용 중인 환자번호입니다."
            )

        return value

    def validate_name(self, value: str) -> str:
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "환자 이름을 입력해 주세요."
            )

        return value


class ProvisionalIdentityResolveSerializer(
    serializers.Serializer
):
    """
    신원미상 환자를 기존 Patient에 병합하거나
    신규 Patient로 생성하기 위한 요청 Serializer.
    """

    resolution_type = serializers.ChoiceField(
        choices=(
            PatientIdentityResolutionLog
            .ResolutionType.choices
        ),
    )

    target_patient_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )

    new_patient = NewPatientChartSerializer(
        required=False,
        allow_null=True,
    )

    note = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=2000,
    )

    def validate(
        self,
        attrs: dict[str, Any],
    ) -> dict[str, Any]:
        resolution_type = attrs["resolution_type"]
        target_patient_id = attrs.get(
            "target_patient_id"
        )
        new_patient = attrs.get("new_patient")

        existing_type = (
            PatientIdentityResolutionLog
            .ResolutionType.EXISTING_PATIENT
        )
        new_type = (
            PatientIdentityResolutionLog
            .ResolutionType.NEW_PATIENT
        )

        if resolution_type == existing_type:
            if target_patient_id is None:
                raise serializers.ValidationError({
                    "target_patient_id": (
                        "기존 환자 차트 병합 시 "
                        "대상 환자 UUID가 필요합니다."
                    ),
                })

            if new_patient is not None:
                raise serializers.ValidationError({
                    "new_patient": (
                        "기존 환자 차트 병합 시 "
                        "신규 환자정보를 입력할 수 없습니다."
                    ),
                })

        elif resolution_type == new_type:
            if new_patient is None:
                raise serializers.ValidationError({
                    "new_patient": (
                        "신규 차트 생성 시 "
                        "환자정보가 필요합니다."
                    ),
                })

            if target_patient_id is not None:
                raise serializers.ValidationError({
                    "target_patient_id": (
                        "신규 차트 생성 시 "
                        "기존 환자 UUID를 입력할 수 없습니다."
                    ),
                })

        return attrs


class PatientAccountClaimIssueSerializer(
    serializers.Serializer
):
    """
    기존 병원 환자에게 모바일 계정 연결 코드를 발급한다.

    의료진:
    - 자신의 소속 병원 기준으로만 발급 가능

    관리자:
    - 요청한 hospital_id 기준으로 발급 가능
    """

    hospital_id = serializers.UUIDField(
        required=False,
        write_only=True,
    )

    def validate(
        self,
        attrs: dict[str, Any],
    ) -> dict[str, Any]:
        request = self.context["request"]
        patient: Patient = self.context["patient"]
        user = request.user

        if patient.status != Patient.Status.ACTIVE:
            raise serializers.ValidationError({
                "patient": (
                    "활성 상태의 정식 환자에게만 "
                    "계정 연결 코드를 발급할 수 있습니다."
                ),
            })

        if patient.user_id is not None:
            raise serializers.ValidationError({
                "patient": (
                    "이미 모바일 계정이 연결된 환자입니다."
                ),
            })

        if user.role == "CLINICIAN":
            clinician = getattr(user, "clinician", None)

            if clinician is None:
                raise serializers.ValidationError({
                    "user": "의료진 프로필을 찾을 수 없습니다.",
                })

            if clinician.approval_status != "APPROVED":
                raise serializers.ValidationError({
                    "user": (
                        "승인 완료된 의료진만 "
                        "연결 코드를 발급할 수 있습니다."
                    ),
                })

            hospital = clinician.hospital

            requested_hospital_id = attrs.get(
                "hospital_id"
            )

            if (
                requested_hospital_id is not None
                and requested_hospital_id
                != hospital.id
            ):
                raise serializers.ValidationError({
                    "hospital_id": (
                        "의료진은 자신의 소속 병원에서만 "
                        "연결 코드를 발급할 수 있습니다."
                    ),
                })

        elif user.role == "ADMIN":
            hospital_id = attrs.get("hospital_id")

            if hospital_id is None:
                raise serializers.ValidationError({
                    "hospital_id": (
                        "관리자 발급 시 병원 선택이 필요합니다."
                    ),
                })

            hospital = Hospital.objects.filter(
                id=hospital_id,
                is_active=True,
            ).first()

            if hospital is None:
                raise serializers.ValidationError({
                    "hospital_id": (
                        "사용 가능한 병원을 찾을 수 없습니다."
                    ),
                })

        else:
            raise serializers.ValidationError({
                "user": (
                    "의료진 또는 관리자만 "
                    "연결 코드를 발급할 수 있습니다."
                ),
            })

        has_appointment = patient.appointments.filter(
            hospital=hospital,
        ).exists()

        has_encounter = patient.encounters.filter(
            hospital=hospital,
        ).exists()

        if not has_appointment and not has_encounter:
            raise serializers.ValidationError({
                "patient": (
                    "선택한 병원에서 환자의 예약 또는 "
                    "진료 이력을 찾을 수 없습니다."
                ),
            })

        attrs["patient"] = patient
        attrs["hospital"] = hospital

        return attrs

    @transaction.atomic
    def create(
        self,
        validated_data: dict[str, Any],
    ) -> dict[str, Any]:
        request = self.context["request"]
        patient: Patient = validated_data["patient"]
        hospital: Hospital = validated_data["hospital"]

        active_claims = (
            PatientAccountClaim.objects
            .select_for_update()
            .filter(
                patient=patient,
                status=PatientAccountClaim.Status.ISSUED,
            )
        )

        for existing_claim in active_claims:
            if existing_claim.is_expired:
                existing_claim.mark_as_expired()
            else:
                existing_claim.revoke()

        raw_code = f"{secrets.randbelow(1_000_000):06d}"

        claim = PatientAccountClaim(
            patient=patient,
            issued_by=request.user,
            expires_at=timezone.now()
            + timedelta(minutes=30),
        )
        claim.set_claim_code(raw_code)
        claim.save()

        return {
            "claim": claim,
            "raw_code": raw_code,
            "hospital": hospital,
        }
