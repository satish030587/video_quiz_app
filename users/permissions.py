from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """Permission to allow only superadmins"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superadmin
