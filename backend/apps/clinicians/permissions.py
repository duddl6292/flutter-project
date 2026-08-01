from rest_framework.permissions import BasePermission

from apps.accounts.models import User
from .models import Clinician


class IsClinicianOrAdmin(BasePermission):
    message = "의료진 또는 관리자만 접근할 수 있습니다."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role
            in {
                User.Role.CLINICIAN,
                User.Role.ADMIN,
            }
        )


class IsApprovedClinicianOrAdmin(BasePermission):
    message = "승인된 의료진 또는 관리자만 접근할 수 있습니다."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role == User.Role.ADMIN:
            return True

        if request.user.role != User.Role.CLINICIAN:
            return False

        try:
            clinician = request.user.clinician
        except Clinician.DoesNotExist:
            return False

        return (
            clinician.approval_status
            == Clinician.ApprovalStatus.APPROVED
        )