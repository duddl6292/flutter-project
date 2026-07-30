from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from .models import User


class _HasRole(BasePermission):
    allowed_roles: tuple[str, ...] = ()

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.allowed_roles
        )


class IsPatient(_HasRole):
    allowed_roles = (User.Role.PATIENT,)


class IsClinician(_HasRole):
    allowed_roles = (User.Role.CLINICIAN,)


class IsAdmin(_HasRole):
    allowed_roles = (User.Role.ADMIN,)


class IsPatientOrClinician(_HasRole):
    allowed_roles = (User.Role.PATIENT, User.Role.CLINICIAN)
