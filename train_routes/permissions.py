from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminrOrReadOnly(BasePermission):
    """
    Object-level permission to only allow admins of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_permission(self, request, view):
        return bool(
            (
                request.method in SAFE_METHODS
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )
