from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly

class IsAdminIsOwnerOrReadOnly(IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS or (
                request.user == obj.author) or request.user.is_staff)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Доступ администратору или только чтение"""

    def has_permission(self, request, obj):
        return (request.method in SAFE_METHODS or request.user.is_staff)


