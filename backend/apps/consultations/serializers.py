from django.utils import timezone
from rest_framework import serializers

from apps.appointments.models import Encounter
from apps.clinicians.models import Clinician

from .models import (
    Consultation,
    ConsultationAttachment,
    ConsultationMessage,
    ConsultationParticipant,
    ConsultationStatusHistory,
)


class ConsultationClinicianSerializer(
    serializers.ModelSerializer
):
    clinician_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )
    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )
    hospital_name = serializers.CharField(
        source="hospital.name",
        read_only=True,
    )

    class Meta:
        model = Clinician
        fields = [
            "clinician_id",
            "name",
            "department_name",
            "hospital_name",
        ]


class ConsultationParticipantSerializer(
    serializers.ModelSerializer
):
    participant_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )
    role_label = serializers.CharField(
        source="get_role_display",
        read_only=True,
    )
    clinician = ConsultationClinicianSerializer(
        read_only=True,
    )

    class Meta:
        model = ConsultationParticipant
        fields = [
            "participant_id",
            "clinician",
            "role",
            "role_label",
            "joined_at",
            "left_at",
            "last_read_at",
        ]


class ConsultationAttachmentSerializer(
    serializers.ModelSerializer
):
    attachment_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )
    attachment_type = serializers.SerializerMethodField()
    source_id = serializers.SerializerMethodField()

    class Meta:
        model = ConsultationAttachment
        fields = [
            "attachment_id",
            "attachment_type",
            "source_id",
            "display_name",
            "created_at",
        ]

    def get_attachment_type(self, attachment):
        for field_name in (
            "stored_object",
            "imaging_study",
            "inference_result",
            "test_result",
        ):
            if getattr(
                attachment,
                f"{field_name}_id",
            ) is not None:
                return field_name.upper()

        return "UNKNOWN"

    def get_source_id(self, attachment):
        for field_name in (
            "stored_object",
            "imaging_study",
            "inference_result",
            "test_result",
        ):
            source_id = getattr(
                attachment,
                f"{field_name}_id",
            )
            if source_id is not None:
                return str(source_id)

        return None


class ConsultationMessageSerializer(
    serializers.ModelSerializer
):
    message_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )
    sender = ConsultationClinicianSerializer(
        read_only=True,
    )
    attachments = ConsultationAttachmentSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = ConsultationMessage
        fields = [
            "message_id",
            "sequence",
            "sender",
            "content",
            "is_system",
            "edited_at",
            "attachments",
            "created_at",
        ]


class ConsultationStatusHistorySerializer(
    serializers.ModelSerializer
):
    history_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )
    new_status_label = serializers.CharField(
        source="get_new_status_display",
        read_only=True,
    )
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ConsultationStatusHistory
        fields = [
            "history_id",
            "previous_status",
            "new_status",
            "new_status_label",
            "changed_by_name",
            "reason",
            "created_at",
        ]

    def get_changed_by_name(self, history):
        clinician = getattr(
            history.changed_by,
            "clinician",
            None,
        )
        if clinician is not None:
            return clinician.name

        return history.changed_by.username


class ConsultationSerializer(
    serializers.ModelSerializer
):
    consultation_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )
    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    priority_label = serializers.CharField(
        source="get_priority_display",
        read_only=True,
    )
    encounter_id = serializers.UUIDField(
        source="encounter.id",
        read_only=True,
    )
    encounter_number = serializers.CharField(
        source="encounter.encounter_number",
        read_only=True,
    )
    patient_id = serializers.UUIDField(
        source="encounter.patient.id",
        read_only=True,
    )
    patient_number = serializers.CharField(
        source=(
            "encounter.patient."
            "medical_record_number"
        ),
        read_only=True,
        allow_null=True,
    )
    patient_name = serializers.CharField(
        source="encounter.patient.name",
        read_only=True,
    )
    patient_birth_date = serializers.DateField(
        source="encounter.patient.birth_date",
        read_only=True,
        allow_null=True,
    )
    patient_sex = serializers.CharField(
        source="encounter.patient.sex",
        read_only=True,
        allow_null=True,
    )
    department_name = serializers.CharField(
        source="encounter.department.name",
        read_only=True,
    )
    requester = ConsultationClinicianSerializer(
        source="requester_clinician",
        read_only=True,
    )
    consultant = ConsultationClinicianSerializer(
        source="consultant_clinician",
        read_only=True,
    )
    participants = ConsultationParticipantSerializer(
        many=True,
        read_only=True,
    )
    messages = ConsultationMessageSerializer(
        many=True,
        read_only=True,
    )
    status_history = (
        ConsultationStatusHistorySerializer(
            many=True,
            read_only=True,
        )
    )
    my_role = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Consultation
        fields = [
            "consultation_id",
            "encounter_id",
            "encounter_number",
            "patient_id",
            "patient_number",
            "patient_name",
            "patient_birth_date",
            "patient_sex",
            "department_name",
            "requester",
            "consultant",
            "participants",
            "subject",
            "priority",
            "priority_label",
            "question",
            "response",
            "status",
            "status_label",
            "my_role",
            "unread_count",
            "messages",
            "status_history",
            "due_at",
            "accepted_at",
            "completed_at",
            "cancelled_at",
            "created_at",
            "updated_at",
        ]

    def _my_participant(self, consultation):
        request = self.context.get("request")
        if (
            request is None
            or not hasattr(request.user, "clinician")
        ):
            return None

        clinician_id = request.user.clinician.id

        return next(
            (
                participant
                for participant
                in consultation.participants.all()
                if (
                    participant.clinician_id
                    == clinician_id
                    and participant.left_at is None
                )
            ),
            None,
        )

    def get_my_role(self, consultation):
        participant = self._my_participant(
            consultation
        )

        return (
            participant.role
            if participant is not None
            else None
        )

    def get_unread_count(self, consultation):
        participant = self._my_participant(
            consultation
        )
        if participant is None:
            return 0

        return sum(
            1
            for message in consultation.messages.all()
            if (
                message.sender_id
                != participant.clinician_id
                and (
                    participant.last_read_at is None
                    or message.created_at
                    > participant.last_read_at
                )
            )
        )


class ConsultationCreateSerializer(
    serializers.Serializer
):
    encounter_id = serializers.UUIDField()
    consultant_clinician_id = serializers.UUIDField()
    subject = serializers.CharField(max_length=200)
    priority = serializers.ChoiceField(
        choices=Consultation.Priority.choices,
        default=Consultation.Priority.ROUTINE,
    )
    question = serializers.CharField()
    due_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )

    def validate_encounter_id(self, value):
        clinician = (
            self.context["request"].user.clinician
        )

        try:
            encounter = (
                Encounter.objects
                .select_related(
                    "patient",
                    "department",
                    "hospital",
                )
                .get(
                    id=value,
                    attending_clinician=clinician,
                    patient__isnull=False,
                )
            )
        except Encounter.DoesNotExist as exc:
            raise serializers.ValidationError(
                "협진을 요청할 수 있는 "
                "진료 건을 찾을 수 없습니다."
            ) from exc

        self.context["encounter"] = encounter
        return value

    def validate_consultant_clinician_id(
        self,
        value,
    ):
        requester = (
            self.context["request"].user.clinician
        )
        if value == requester.id:
            raise serializers.ValidationError(
                "본인에게 협진을 요청할 수 없습니다."
            )

        try:
            consultant = (
                Clinician.objects
                .select_related(
                    "user",
                    "department",
                    "hospital",
                )
                .get(
                    id=value,
                    approval_status=(
                        Clinician.ApprovalStatus.APPROVED
                    ),
                )
            )
        except Clinician.DoesNotExist as exc:
            raise serializers.ValidationError(
                "협진 가능한 의료진을 "
                "찾을 수 없습니다."
            ) from exc

        self.context["consultant"] = consultant
        return value

    def validate_subject(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "협진 제목을 입력해주세요."
            )
        return value

    def validate_question(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "협진 요청 내용을 입력해주세요."
            )
        return value

    def validate_due_at(self, value):
        if (
            value is not None
            and value <= timezone.now()
        ):
            raise serializers.ValidationError(
                "답변 희망일은 현재보다 이후여야 합니다."
            )
        return value


class ConsultationMessageCreateSerializer(
    serializers.Serializer
):
    content = serializers.CharField()

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "메시지 내용을 입력해주세요."
            )
        return value


class ConsultationCompleteSerializer(
    serializers.Serializer
):
    response = serializers.CharField()

    def validate_response(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "최종 협진 답변을 입력해주세요."
            )
        return value


class ConsultationCancelSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
    )
