from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow creators of an object or admins to view/edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Admins / Staff have full access
        if request.user and request.user.is_staff:
            return True

        # Creators have access to their own patients
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user

        return False
