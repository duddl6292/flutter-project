from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.exceptions import (
    InvalidToken,
    TokenError,
)

from .serializers import (
    AccountEmailUpdateSerializer,
    ClinicianLoginSerializer,
    ClinicianSignupSerializer,
    PasswordChangeSerializer,
    PatientClaimSignupSerializer,
    PatientLoginSerializer,
    PatientSignupSerializer,
)


def _current_account_data(user):
    clinician = getattr(user, "clinician", None)

    clinician_data = None

    if clinician is not None:
        clinician_data = {
            "id": str(clinician.id),
            "name": clinician.name,
            "license_number": clinician.license_number,
            "approval_status": clinician.approval_status,
            "hospital_id": str(clinician.hospital_id),
            "hospital_name": clinician.hospital.name,
            "department_id": str(clinician.department_id),
            "department_code": clinician.department.code,
            "department_name": clinician.department.name,
        }

    return {
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
        },
        "clinician": clinician_data,
    }


class CurrentAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "data": _current_account_data(
                request.user,
            ),
        })

    def patch(self, request):
        serializer = AccountEmailUpdateSerializer(
            instance=request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "data": _current_account_data(user),
        })


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "data": {
                "changed": True,
            },
        })


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

class PatientClaimSignupView(APIView):
    """
    기존 병원 환자의 모바일 계정 연결 회원가입.

    POST /api/v1/auth/patient/claim/
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PatientClaimSignupSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        result = serializer.save()

        return Response(
            {
                "data": result,
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
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(str(exc)) from exc

        return Response(
            {
                "data": serializer.validated_data,
            },
            status=status.HTTP_200_OK,
        )
