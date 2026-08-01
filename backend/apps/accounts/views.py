from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer,
)

from .serializers import (
    ClinicianLoginSerializer,
    ClinicianSignupSerializer,
    PatientLoginSerializer,
    PatientSignupSerializer,
)


class PatientSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PatientSignupSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        patient = serializer.save()

        return Response(
            {
                "data": {
                    "user_id": str(patient.user_id),
                    "patient_id": str(patient.id),
                    "username": patient.user.username,
                    "email": patient.user.email,
                    "role": patient.user.role,
                    "name": patient.name,
                }
            },
            status=status.HTTP_201_CREATED,
        )


class PatientLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PatientLoginSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        return Response(
            {
                "data": serializer.validated_data,
            },
            status=status.HTTP_200_OK,
        )


class ClinicianSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ClinicianSignupSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        clinician = serializer.save()

        return Response(
            {
                "data": {
                    "user_id": str(clinician.user_id),
                    "clinician_id": str(clinician.id),
                    "name": clinician.name,
                    "license_number": (
                        clinician.license_number
                    ),
                    "hospital_id": str(
                        clinician.hospital_id
                    ),
                    "department_id": str(
                        clinician.department_id
                    ),
                    "approval_status": (
                        clinician.approval_status
                    ),
                }
            },
            status=status.HTTP_201_CREATED,
        )


class ClinicianLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ClinicianLoginSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        return Response(
            {
                "data": serializer.validated_data,
            },
            status=status.HTTP_200_OK,
        )


class TokenRefreshAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenRefreshSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        return Response(
            {
                "data": serializer.validated_data,
            },
            status=status.HTTP_200_OK,
        )