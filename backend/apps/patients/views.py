from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import (NotFound, PermissionDenied, ValidationError as DRFValidationError,)
from rest_framework.response import Response
from rest_framework.views import APIView

from .access import (
    accessible_encounters_for_user,
    accessible_patients_for_user,
)
from .models import (Patient, PatientIdentityResolutionLog, ProvisionalIdentity,)
from .pagination import PatientPagination
from .permissions import (IsClinician, IsClinicianOrAdmin, IsPatient,)
from .serializers import (
    PatientAccountClaimIssueSerializer,
    PatientAppointmentSerializer,
    PatientCTResultSerializer,
    PatientDetailSerializer,
    PatientFavoriteHospitalCreateSerializer,
    PatientFavoriteHospitalSerializer,
    MedicationRecordMarkTakenInputSerializer,
    PatientMedicalHistorySerializer,
    PatientMedicationRecordSerializer,
    PatientMedicationScheduleSerializer,
    PatientNotificationSerializer,
    PatientPrescriptionSerializer,
    PatientReleasedDiagnosticReportSerializer,
    PatientReleasedTestResultSerializer,
    PatientSummarySerializer,
    PatientUpdateSerializer,
    ProvisionalIdentityCreateSerializer,
    ProvisionalIdentityResolveSerializer,
    ProvisionalIdentitySerializer,
    )
from .services import (resolve_to_existing_patient, resolve_to_new_patient, )
from apps.appointments.models import Appointment, Encounter
from apps.appointments.serializers import (
    EncounterDetailSerializer,
)
from apps.clinicians.permissions import (
    IsApprovedClinicianOrAdmin,
)
from apps.medications.models import (MedicationRecord, MedicationSchedule,)
from apps.prescriptions.models import Prescription
from apps.test_results.models import TestResult
from apps.diagnostics.models import DiagnosticReport
from apps.hospitals.models import PatientFavoriteHospital
from django.db import IntegrityError, transaction
from django.utils import timezone
from apps.notifications.models import Notification

class PatientMeView(APIView):
    """
    로그인한 환자의 본인 정보 조회·수정.

    GET   /api/v1/patients/me/
    PATCH /api/v1/patients/me/
    """

    permission_classes = [IsPatient]

    def get_patient(self, request) -> Patient:
        try:
            return Patient.objects.select_related(
                "user",
                "merged_into",
            ).get(
                user=request.user,
            )
        except Patient.DoesNotExist as exc:
            raise NotFound(
                "환자 프로필을 찾을 수 없습니다."
            ) from exc

    def get(self, request):
        patient = self.get_patient(request)

        serializer = PatientDetailSerializer(
            patient,
        )

        return Response({
            "data": serializer.data,
        })

    def patch(self, request):
        patient = self.get_patient(request)

        serializer = PatientUpdateSerializer(
            patient,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        updated_patient = serializer.save()

        response_serializer = PatientDetailSerializer(
            updated_patient,
        )

        return Response({
            "data": response_serializer.data,
        })

class PatientMedicalHistoryView(APIView):
    """
    로그인 환자의 통합 진료이력 조회.

    GET /api/v1/patients/me/medical-history/
    """

    permission_classes = [IsPatient]

    def get_patient(self, request) -> Patient:
        try:
            return Patient.objects.get(
                user=request.user,
                status=Patient.Status.ACTIVE,
            )
        except Patient.DoesNotExist as exc:
            raise NotFound(
                "활성 상태의 환자 프로필을 찾을 수 없습니다."
            ) from exc

    def get(self, request):
        patient = self.get_patient(request)

        encounter_type = request.query_params.get(
            "encounter_type",
            "",
        ).strip().upper()

        requested_status = request.query_params.get(
            "status",
            "",
        ).strip().upper()

        hospital_id = request.query_params.get(
            "hospital_id",
            "",
        ).strip()

        valid_encounter_types = {
            value
            for value, _label
            in Encounter.EncounterType.choices
        }

        valid_statuses = {
            value
            for value, _label
            in Encounter.Status.choices
        }

        if (
            encounter_type
            and encounter_type
            not in valid_encounter_types
        ):
            raise DRFValidationError({
                "encounter_type": (
                    "올바른 진료 유형이 아닙니다."
                ),
            })

        if (
            requested_status
            and requested_status
            not in valid_statuses
        ):
            raise DRFValidationError({
                "status": (
                    "올바른 진료 상태가 아닙니다."
                ),
            })

        encounters = (
            Encounter.objects
            .filter(patient=patient)
            .select_related(
                "hospital",
                "department",
                "attending_clinician",
                "appointment",
            )
        )

        if encounter_type:
            encounters = encounters.filter(
                encounter_type=encounter_type,
            )

        if requested_status:
            encounters = encounters.filter(
                status=requested_status,
            )

        if hospital_id:
            encounters = encounters.filter(
                hospital_id=hospital_id,
            )

        encounters = encounters.order_by(
            "-created_at",
        )

        paginator = PatientPagination()

        page = paginator.paginate_queryset(
            encounters,
            request,
            view=self,
        )

        serializer = PatientMedicalHistorySerializer(
            page,
            many=True,
        )

        return paginator.get_paginated_response(
            serializer.data
        )

class PatientOwnedDataMixin:
    """
    로그인 사용자와 연결된 활성 Patient를 조회한다.
    """

    def get_patient(self, request) -> Patient:
        try:
            return Patient.objects.get(
                user=request.user,
                status=Patient.Status.ACTIVE,
            )
        except Patient.DoesNotExist as exc:
            raise NotFound(
                "활성 상태의 환자 프로필을 찾을 수 없습니다."
            ) from exc

    def get_paginated_response(
        self,
        *,
        request,
        queryset,
        serializer_class,
    ):
        paginator = PatientPagination()

        page = paginator.paginate_queryset(
            queryset,
            request,
            view=self,
        )

        serializer = serializer_class(
            page,
            many=True,
        )

        return paginator.get_paginated_response(
            serializer.data
        )

class PatientAppointmentListView(
    PatientOwnedDataMixin,
    APIView,
):
    """
    로그인 환자의 예약 목록.

    GET /api/v1/patients/me/appointments/
    """

    permission_classes = [IsPatient]

    def get(self, request):
        patient = self.get_patient(request)

        requested_status = request.query_params.get(
            "status",
            "",
        ).strip().upper()

        valid_statuses = {
            value
            for value, _label
            in Appointment.Status.choices
        }

        if (
            requested_status
            and requested_status not in valid_statuses
        ):
            raise DRFValidationError({
                "status": "올바른 예약 상태가 아닙니다.",
            })

        appointments = (
            Appointment.objects
            .filter(patient=patient)
            .select_related(
                "hospital",
                "department",
                "clinician",
            )
        )

        if requested_status:
            appointments = appointments.filter(
                status=requested_status,
            )

        appointments = appointments.order_by(
            "-scheduled_at",
            "-created_at",
        )

        return self.get_paginated_response(
            request=request,
            queryset=appointments,
            serializer_class=PatientAppointmentSerializer,
        )


class PatientTestResultListView(
    PatientOwnedDataMixin,
    APIView,
):
    """
    로그인 환자에게 공개된 공식 검사결과 목록.

    GET /api/v1/patients/me/test-results/
    """

    permission_classes = [IsPatient]

    def get(self, request):
        patient = self.get_patient(request)

        test_type = request.query_params.get(
            "test_type",
            "",
        ).strip()

        results = (
            TestResult.objects
            .filter(
                encounter__patient=patient,
                is_released_to_patient=True,
                status__in=[
                    TestResult.Status.FINAL,
                    TestResult.Status.CORRECTED,
                ],
            )
            .select_related(
                "encounter",
                "encounter__hospital",
                "case",
            )
        )

        if test_type:
            results = results.filter(
                test_type__iexact=test_type,
            )

        results = results.order_by(
            "-performed_at",
            "-created_at",
        )

        reports = (
            DiagnosticReport.objects
            .filter(
                examination__patient=patient,
                is_released_to_patient=True,
                status__in=[
                    DiagnosticReport.Status.FINAL,
                    DiagnosticReport.Status.CORRECTED,
                ],
            )
            .select_related(
                "examination",
                "examination__encounter",
                "examination__hospital",
            )
            .prefetch_related("assets")
        )
        if test_type:
            reports = reports.filter(examination__category__iexact=test_type)

        serialized = [
            *PatientReleasedTestResultSerializer(results, many=True).data,
            *PatientReleasedDiagnosticReportSerializer(reports, many=True).data,
        ]
        serialized.sort(
            key=lambda item: item.get("performed_at") or "",
            reverse=True,
        )
        paginator = PatientPagination()
        page = paginator.paginate_queryset(serialized, request, view=self)
        return paginator.get_paginated_response(page)


class PatientPrescriptionListView(
    PatientOwnedDataMixin,
    APIView,
):
    """
    로그인 환자의 처방전 목록.

    GET /api/v1/patients/me/prescriptions/
    """

    permission_classes = [IsPatient]

    def get(self, request):
        patient = self.get_patient(request)

        requested_status = request.query_params.get(
            "status",
            "",
        ).strip().upper()

        valid_statuses = {
            value
            for value, _label
            in Prescription.Status.choices
        }

        if (
            requested_status
            and requested_status not in valid_statuses
        ):
            raise DRFValidationError({
                "status": "올바른 처방 상태가 아닙니다.",
            })

        prescriptions = (
            Prescription.objects
            .filter(
                encounter__patient=patient,
            )
            .exclude(
                status=Prescription.Status.DRAFT,
            )
            .select_related(
                "encounter",
                "encounter__hospital",
                "clinician",
            )
            .prefetch_related("items__medication_schedules")
        )

        if requested_status:
            prescriptions = prescriptions.filter(
                status=requested_status,
            )

        prescriptions = prescriptions.order_by(
            "-prescribed_at",
            "-created_at",
        )

        return self.get_paginated_response(
            request=request,
            queryset=prescriptions,
            serializer_class=PatientPrescriptionSerializer,
        )


class PatientMedicationScheduleListView(
    PatientOwnedDataMixin,
    APIView,
):
    """
    로그인 환자의 복약 일정 목록.

    GET /api/v1/patients/me/medication-schedules/
    """

    permission_classes = [IsPatient]

    def get(self, request):
        patient = self.get_patient(request)

        active_value = request.query_params.get(
            "active",
            "",
        ).strip().lower()

        if active_value not in {
            "",
            "true",
            "false",
        }:
            raise DRFValidationError({
                "active": (
                    "active 값은 true 또는 false여야 합니다."
                ),
            })

        schedules = (
            MedicationSchedule.objects
            .filter(
                prescription_item__prescription__encounter__patient=(
                    patient
                ),
            )
            .exclude(
                prescription_item__prescription__status=(
                    Prescription.Status.DRAFT
                ),
            )
            .select_related(
                "prescription_item",
                "prescription_item__prescription",
                (
                    "prescription_item__prescription__"
                    "encounter"
                ),
                (
                    "prescription_item__prescription__"
                    "encounter__hospital"
                ),
            )
        )

        if active_value:
            schedules = schedules.filter(
                is_active=(active_value == "true"),
            )

        schedules = schedules.order_by(
            "start_date",
            "dose_time",
            "created_at",
        )

        return self.get_paginated_response(
            request=request,
            queryset=schedules,
            serializer_class=(
                PatientMedicationScheduleSerializer
            ),
        )


class PatientMedicationRecordListView(
    PatientOwnedDataMixin,
    APIView,
):
    """
    로그인 환자의 실제 복약 기록 목록.

    GET /api/v1/patients/me/medication-records/
    """

    permission_classes = [IsPatient]

    def get(self, request):
        patient = self.get_patient(request)

        requested_status = request.query_params.get(
            "status",
            "",
        ).strip().upper()

        valid_statuses = {
            value
            for value, _label
            in MedicationRecord.Status.choices
        }

        if (
            requested_status
            and requested_status not in valid_statuses
        ):
            raise DRFValidationError({
                "status": "올바른 복약 상태가 아닙니다.",
            })

        records = (
            MedicationRecord.objects
            .filter(
                prescription_item__prescription__encounter__patient=(
                    patient
                ),
            )
            .select_related(
                "schedule",
                "prescription_item",
                "prescription_item__prescription",
                (
                    "prescription_item__prescription__"
                    "encounter"
                ),
            )
        )

        if requested_status:
            records = records.filter(
                status=requested_status,
            )

        records = records.order_by(
            "-scheduled_at",
            "-created_at",
        )

        return self.get_paginated_response(
            request=request,
            queryset=records,
            serializer_class=(
                PatientMedicationRecordSerializer
            ),
        )


class PatientMedicationRecordMarkTakenView(
    PatientOwnedDataMixin,
    APIView,
):
    """
    환자가 복약 완료를 직접 체크/취소한다.

    POST /api/v1/patients/me/medication-records/mark-taken/
    다시 호출하면(이미 TAKEN 상태) 체크가 취소된다.
    """

    permission_classes = [IsPatient]

    def post(self, request):
        patient = self.get_patient(request)

        input_serializer = MedicationRecordMarkTakenInputSerializer(
            data=request.data,
        )
        input_serializer.is_valid(raise_exception=True)
        schedule_id = input_serializer.validated_data["schedule_id"]
        scheduled_at = input_serializer.validated_data["scheduled_at"]

        schedule = get_object_or_404(
            MedicationSchedule.objects.filter(
                prescription_item__prescription__encounter__patient=(
                    patient
                ),
            ),
            id=schedule_id,
        )

        existing = MedicationRecord.objects.filter(
            schedule=schedule,
            scheduled_at=scheduled_at,
        ).first()

        if existing and existing.status == MedicationRecord.Status.TAKEN:
            existing.delete()
            return Response(
                {"data": {"status": "PENDING"}},
            )

        if existing:
            existing.status = MedicationRecord.Status.TAKEN
            existing.taken_at = timezone.now()
            existing.save(
                update_fields=["status", "taken_at", "updated_at"],
            )
            record = existing
        else:
            record = MedicationRecord.objects.create(
                schedule=schedule,
                prescription_item=schedule.prescription_item,
                scheduled_at=scheduled_at,
                status=MedicationRecord.Status.TAKEN,
                taken_at=timezone.now(),
            )

        return Response(
            {
                "data": PatientMedicationRecordSerializer(
                    record,
                ).data,
            },
        )


class PatientCTResultListView(
    PatientOwnedDataMixin,
    APIView,
):
    """
    의료진이 검토하고 공개한 환자용 CT 결과.

    GET /api/v1/patients/me/ct-results/
    """

    permission_classes = [IsPatient]

    def get(self, request):
        patient = self.get_patient(request)

        results = (
            TestResult.objects
            .filter(
                encounter__patient=patient,
                is_released_to_patient=True,
                status__in=[
                    TestResult.Status.FINAL,
                    TestResult.Status.CORRECTED,
                ],
            )
            .select_related(
                "case",
                "encounter",
                "encounter__hospital",
            )
            .order_by(
                "-performed_at",
                "-created_at",
            )
        )

        return self.get_paginated_response(
            request=request,
            queryset=results,
            serializer_class=PatientCTResultSerializer,
        )

class PatientFavoriteHospitalListCreateView(
    PatientOwnedDataMixin,
    APIView,
):
    """
    로그인 환자의 찜 병원 목록 조회·추가.

    GET
    /api/v1/patients/me/favorite-hospitals/

    POST
    /api/v1/patients/me/favorite-hospitals/
    """

    permission_classes = [IsPatient]

    def get(self, request):
        patient = self.get_patient(request)

        favorite_hospitals = (
            PatientFavoriteHospital.objects
            .filter(patient=patient)
            .select_related("hospital")
            .order_by("-created_at")
        )

        return self.get_paginated_response(
            request=request,
            queryset=favorite_hospitals,
            serializer_class=(
                PatientFavoriteHospitalSerializer
            ),
        )

    def post(self, request):
        patient = self.get_patient(request)

        serializer = (
            PatientFavoriteHospitalCreateSerializer(
                data=request.data,
                context={
                    "patient": patient,
                },
            )
        )
        serializer.is_valid(raise_exception=True)

        favorite_hospital = serializer.save()

        response_serializer = (
            PatientFavoriteHospitalSerializer(
                favorite_hospital,
            )
        )

        return Response(
            {
                "data": response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

class PatientFavoriteHospitalDeleteView(
    PatientOwnedDataMixin,
    APIView,
):
    """
    로그인 환자의 특정 병원 찜 삭제.

    DELETE
    /api/v1/patients/me/favorite-hospitals/{hospital_id}/
    """

    permission_classes = [IsPatient]

    def delete(
        self,
        request,
        hospital_id,
    ):
        patient = self.get_patient(request)

        favorite_hospital = get_object_or_404(
            PatientFavoriteHospital.objects.select_related(
                "hospital",
            ),
            patient=patient,
            hospital_id=hospital_id,
        )

        favorite_hospital.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

class PatientNotificationListView(
    PatientOwnedDataMixin,
    APIView,
):
    """
    로그인 환자의 알림 목록 조회.

    GET /api/v1/patients/me/notifications/
    """

    permission_classes = [IsPatient]

    def get(self, request):
        # 활성 Patient 프로필이 실제로 연결되어 있는지 검증한다.
        self.get_patient(request)

        read_value = request.query_params.get(
            "read",
            "",
        ).strip().lower()

        notification_type = request.query_params.get(
            "type",
            "",
        ).strip().upper()

        if read_value not in {
            "",
            "true",
            "false",
        }:
            raise DRFValidationError({
                "read": (
                    "read 값은 true 또는 false여야 합니다."
                ),
            })

        valid_types = {
            value
            for value, _label
            in Notification.Type.choices
        }

        if (
            notification_type
            and notification_type not in valid_types
        ):
            raise DRFValidationError({
                "type": "올바른 알림 유형이 아닙니다.",
            })

        notifications = Notification.objects.filter(
            recipient=request.user,
        )

        if read_value:
            notifications = notifications.filter(
                is_read=(read_value == "true"),
            )

        if notification_type:
            notifications = notifications.filter(
                type=notification_type,
            )

        notifications = notifications.order_by(
            "-created_at",
        )

        paginator = PatientPagination()

        page = paginator.paginate_queryset(
            notifications,
            request,
            view=self,
        )

        serializer = PatientNotificationSerializer(
            page,
            many=True,
        )

        response = paginator.get_paginated_response(
            serializer.data
        )

        response.data["meta"]["unread_count"] = (
            Notification.objects.filter(
                recipient=request.user,
                is_read=False,
            ).count()
        )

        return response

class PatientNotificationReadView(
    PatientOwnedDataMixin,
    APIView,
):
    """
    로그인 환자의 특정 알림을 읽음 처리한다.

    PATCH
    /api/v1/patients/me/notifications/{notification_id}/read/
    """

    permission_classes = [IsPatient]

    @transaction.atomic
    def patch(
        self,
        request,
        notification_id,
    ):
        self.get_patient(request)

        notification = get_object_or_404(
            Notification.objects.select_for_update(),
            id=notification_id,
            recipient=request.user,
        )

        notification.mark_as_read()

        serializer = PatientNotificationSerializer(
            notification,
        )

        return Response({
            "data": serializer.data,
        })

class PatientNotificationReadAllView(
    PatientOwnedDataMixin,
    APIView,
):
    """
    로그인 환자의 읽지 않은 알림을 모두 읽음 처리한다.

    PATCH
    /api/v1/patients/me/notifications/read-all/
    """

    permission_classes = [IsPatient]

    @transaction.atomic
    def patch(self, request):
        self.get_patient(request)

        read_at = timezone.now()

        updated_count = (
            Notification.objects
            .filter(
                recipient=request.user,
                is_read=False,
            )
            .update(
                is_read=True,
                read_at=read_at,
                updated_at=read_at,
            )
        )

        return Response({
            "data": {
                "updated_count": updated_count,
                "read_at": read_at.isoformat(),
                "unread_count": 0,
            },
        })

class PatientListView(APIView):
    """
    의료진·관리자용 환자 목록 및 검색.

    GET /api/v1/patients/
    GET /api/v1/patients/?search=김환자
    GET /api/v1/patients/?status=ACTIVE
    """

    permission_classes = [IsClinicianOrAdmin]

    def get(self, request):
        keyword = request.query_params.get(
            "search",
            "",
        ).strip()

        requested_status = request.query_params.get(
            "status",
            "",
        ).strip().upper()

        patients = accessible_patients_for_user(
            request.user,
            Patient.objects.select_related(
                "user",
                "merged_into",
            ),
        )

        # 기본적으로 통합된 중복 환자는 목록에서 제외합니다.
        if requested_status:
            valid_statuses = {
                value
                for value, _label in Patient.Status.choices
            }

            if requested_status in valid_statuses:
                patients = patients.filter(
                    status=requested_status,
                )
        else:
            patients = patients.exclude(
                status=Patient.Status.MERGED,
            )

        if keyword:
            patients = patients.filter(
                Q(name__icontains=keyword)
                | Q(
                    medical_record_number__icontains=keyword
                )
                | Q(phone__icontains=keyword)
                | Q(user__username__icontains=keyword)
            )

        patients = patients.order_by(
            "name",
            "-created_at",
        )

        paginator = PatientPagination()

        page = paginator.paginate_queryset(
            patients,
            request,
            view=self,
        )

        serializer = PatientSummarySerializer(
            page,
            many=True,
            context={"request": request},
        )

        return paginator.get_paginated_response(
            serializer.data
        )


class PatientDetailView(APIView):
    """
    의료진·관리자용 환자 상세 조회.

    GET /api/v1/patients/{patient_id}/
    """

    permission_classes = [IsClinicianOrAdmin]

    def get(self, request, patient_id):
        patient = get_object_or_404(
            accessible_patients_for_user(
                request.user,
                Patient.objects.select_related(
                    "user",
                    "merged_into",
                ),
            ),
            id=patient_id,
        )

        # 중복 환자가 통합된 경우 최종 정식 환자를 반환합니다.
        if patient.canonical_patient.id != patient.id:
            patient = get_object_or_404(
                accessible_patients_for_user(
                    request.user,
                    Patient.objects.select_related(
                        "user",
                        "merged_into",
                    ),
                ),
                id=patient.canonical_patient.id,
            )

        serializer = PatientDetailSerializer(
            patient,
            context={"request": request},
        )

        return Response({
            "data": serializer.data,
        })


class ClinicianPatientMedicalHistoryView(APIView):
    """
    의료진용 환자 과거 진료 결과 조회.

    GET /api/v1/patients/{patient_id}/medical-history/
    """

    permission_classes = [
        IsClinicianOrAdmin,
        IsApprovedClinicianOrAdmin,
    ]

    def get(self, request, patient_id):
        patient = get_object_or_404(
            accessible_patients_for_user(
                request.user,
                Patient.objects.select_related("merged_into"),
            ),
            id=patient_id,
        ).canonical_patient
        encounters = accessible_encounters_for_user(
            request.user,
            Encounter.objects.filter(
                patient=patient,
                status=Encounter.Status.COMPLETED,
                clinical_records__isnull=False,
            ),
        )
        encounters = (
            encounters
            .select_related(
                "patient",
                "provisional_identity",
                "appointment",
                "department",
                "hospital",
                "attending_clinician",
            )
            .prefetch_related(
                "clinical_records",
                "prescriptions__items",
                "ct_cases",
            )
            .distinct()
        )

        encounters = encounters.order_by(
            "-completed_at",
            "-created_at",
        )
        paginator = PatientPagination()
        page = paginator.paginate_queryset(
            encounters,
            request,
            view=self,
        )

        return paginator.get_paginated_response(
            EncounterDetailSerializer(
                page,
                many=True,
            ).data
        )

class PatientAccountClaimIssueView(APIView):
    """
    의료진·관리자용 환자 계정 연결 코드 발급.

    POST
    /api/v1/patients/{patient_id}/account-claims/
    """

    permission_classes = [IsClinicianOrAdmin]

    def post(self, request, patient_id):
        patient = get_object_or_404(
            accessible_patients_for_user(
                request.user,
                Patient.objects.select_related("user"),
                include_consultation=False,
            ),
            id=patient_id,
        )

        serializer = PatientAccountClaimIssueSerializer(
            data=request.data,
            context={
                "request": request,
                "patient": patient,
            },
        )
        serializer.is_valid(raise_exception=True)

        result = serializer.save()

        claim = result["claim"]
        hospital = result["hospital"]

        return Response(
            {
                "data": {
                    "claim_id": str(claim.id),
                    "patient_id": str(patient.id),
                    "medical_record_number": (
                        patient.medical_record_number
                    ),
                    "patient_name": patient.name,
                    "hospital_id": str(hospital.id),
                    "hospital_name": hospital.name,
                    "claim_code": result["raw_code"],
                    "status": claim.status,
                    "expires_at": (
                        claim.expires_at.isoformat()
                    ),
                }
            },
            status=status.HTTP_201_CREATED,
        )

class ProvisionalIdentityListCreateView(APIView):
    """
    의료진·관리자용 신원미상 환자 목록·생성.

    GET  /api/v1/provisional-identities/
    POST /api/v1/provisional-identities/
    """

    permission_classes = [IsClinicianOrAdmin]

    def get(self, request):
        requested_status = request.query_params.get(
            "status",
            "",
        ).strip().upper()

        identities = (
            ProvisionalIdentity.objects
            .select_related(
                "resolved_patient",
                "resolved_by",
            )
            .all()
        )

        if requested_status:
            valid_statuses = {
                value
                for value, _label
                in ProvisionalIdentity.Status.choices
            }

            if requested_status in valid_statuses:
                identities = identities.filter(
                    status=requested_status,
                )

        serializer = ProvisionalIdentitySerializer(
            identities,
            many=True,
        )

        return Response({
            "data": serializer.data,
            "meta": {
                "total_count": identities.count(),
            },
        })

    def post(self, request):
        serializer = ProvisionalIdentityCreateSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        identity = serializer.save()

        response_serializer = ProvisionalIdentitySerializer(
            identity,
        )

        return Response(
            {
                "data": response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class ProvisionalIdentityDetailView(APIView):
    """
    의료진·관리자용 신원미상 환자 상세 조회.

    GET /api/v1/provisional-identities/{id}/
    """

    permission_classes = [IsClinicianOrAdmin]

    def get(self, request, provisional_identity_id):
        identity = get_object_or_404(
            ProvisionalIdentity.objects.select_related(
                "resolved_patient",
                "resolved_by",
            ),
            id=provisional_identity_id,
        )

        serializer = ProvisionalIdentitySerializer(
            identity,
        )

        return Response({
            "data": serializer.data,
        })

class ProvisionalIdentityResolveView(APIView):
    """
    신원미상 환자의 신원을 확인하고
    기존 또는 신규 Patient 차트로 전환한다.

    POST
    /api/v1/provisional-identities/{id}/resolve/
    """

    permission_classes = [IsClinician]

    def post(
        self,
        request,
        provisional_identity_id,
    ):
        clinician = getattr(
            request.user,
            "clinician",
            None,
        )

        if clinician is None:
            raise PermissionDenied(
                "의료진 프로필을 찾을 수 없습니다."
            )

        serializer = (
            ProvisionalIdentityResolveSerializer(
                data=request.data,
            )
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        resolution_type = validated_data[
            "resolution_type"
        ]

        note = validated_data.get("note", "")

        try:
            if resolution_type == (
                PatientIdentityResolutionLog
                .ResolutionType.EXISTING_PATIENT
            ):
                result = resolve_to_existing_patient(
                    provisional_identity_id=(
                        provisional_identity_id
                    ),
                    target_patient_id=(
                        validated_data[
                            "target_patient_id"
                        ]
                    ),
                    resolved_by=clinician,
                    note=note,
                )

            else:
                result = resolve_to_new_patient(
                    provisional_identity_id=(
                        provisional_identity_id
                    ),
                    new_patient_data=(
                        validated_data["new_patient"]
                    ),
                    resolved_by=clinician,
                    note=note,
                )

        except DjangoValidationError as exc:
            if hasattr(exc, "message_dict"):
                error_detail = exc.message_dict
            else:
                error_detail = {
                    "non_field_errors": exc.messages,
                }

            raise DRFValidationError(
                error_detail
            ) from exc

        except IntegrityError as exc:
            raise DRFValidationError({
                "provisional_identity": (
                    "데이터베이스 무결성 검증으로 "
                    "신원확인 처리가 취소되었습니다."
                ),
            }) from exc

        patient = result.patient
        resolution_log = result.resolution_log

        return Response(
            {
                "data": {
                    "provisional_identity_id": str(
                        result.provisional_identity_uuid
                    ),
                    "resolution_type": (
                        result.resolution_type
                    ),
                    "patient": {
                        "patient_id": str(
                            patient.id
                        ),
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
                        "status": patient.status,
                    },
                    "moved_encounter_count": (
                        result.moved_encounter_count
                    ),
                    "resolution_log": {
                        "log_id": str(
                            resolution_log.id
                        ),
                        "resolved_by_id": str(
                            resolution_log.resolved_by_id
                        ),
                        "resolved_at": (
                            resolution_log
                            .resolved_at
                            .isoformat()
                        ),
                        "provisional_deleted_at": (
                            resolution_log
                            .provisional_deleted_at
                            .isoformat()
                            if resolution_log
                            .provisional_deleted_at
                            else None
                        ),
                        "deletion_snapshot_saved": bool(
                            resolution_log
                            .deletion_snapshot
                        ),
                    },
                }
            },
            status=status.HTTP_200_OK,
        )
