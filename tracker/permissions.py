from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    """
    Allow read-only to authenticated users, but writes only to owners.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
