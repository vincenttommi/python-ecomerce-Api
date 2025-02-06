from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to allow only admin users to create products.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "is_staff", False)
