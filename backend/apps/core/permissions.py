from rest_framework.permissions import BasePermission


class RolePermission(BasePermission):
    def has_permission(self, request, view):
        roles = getattr(view, "allowed_roles", ())
        return request.user.is_authenticated and (
            not roles or request.user.role in roles
        )


class ClinicianOrAdmin(RolePermission):
    def has_permission(self, request, view):
        view.allowed_roles = ("CLINICIAN", "ADMIN")
        return super().has_permission(request, view)


class PatientOnly(RolePermission):
    def has_permission(self, request, view):
        view.allowed_roles = ("PATIENT",)
        return super().has_permission(request, view)
