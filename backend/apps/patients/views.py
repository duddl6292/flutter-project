from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Patient, ProvisionalIdentity
from .pagination import PatientPagination
from .permissions import IsClinicianOrAdmin, IsPatient
from .serializers import (
    PatientDetailSerializer,
    PatientSummarySerializer,
    PatientUpdateSerializer,
    ProvisionalIdentityCreateSerializer,
    ProvisionalIdentitySerializer,
)


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

        patients = Patient.objects.select_related(
            "user",
            "merged_into",
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
            Patient.objects.select_related(
                "user",
                "merged_into",
            ),
            id=patient_id,
        )

        # 중복 환자가 통합된 경우 최종 정식 환자를 반환합니다.
        patient = patient.canonical_patient

        serializer = PatientDetailSerializer(
            patient,
        )

        return Response({
            "data": serializer.data,
        })


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