from rest_framework.permissions import BasePermission


class IsPatient(BasePermission):
    """
    환자 계정만 접근할 수 있습니다.
    """

    message = "환자 계정만 접근할 수 있습니다."

    def has_permission(self, request, view) -> bool:
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == "PATIENT"
        )

class IsClinician(BasePermission):
    """
    의료진 계정만 접근할 수 있습니다.

    실제 승인 여부는 Service에서 다시 검증합니다.
    """

    message = "의료진 계정만 접근할 수 있습니다."

    def has_permission(self, request, view) -> bool:
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == "CLINICIAN"
        )

class IsClinicianOrAdmin(BasePermission):
    """
    의료진 또는 관리자 계정만 접근할 수 있습니다.
    """

    message = "의료진 또는 관리자만 접근할 수 있습니다."

    def has_permission(self, request, view) -> bool:
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None)
            in {
                "CLINICIAN",
                "ADMIN",
            }
        )


class IsAdmin(BasePermission):
    """
    관리자 계정만 접근할 수 있습니다.
    """

    message = "관리자만 접근할 수 있습니다."

    def has_permission(self, request, view) -> bool:
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == "ADMIN"
        )