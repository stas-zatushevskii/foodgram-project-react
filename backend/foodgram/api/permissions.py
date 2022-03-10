from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (request.method
                in permissions.SAFE_METHODS or obj.author == request.user)


class ReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAdminOrReadOnly(permissions.BasePermission):
    """Доступ администратору или только чтение"""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    and request.user.is_admin))


class IsAdminUserReadOnly(permissions.BasePermission):
    """Доступ администратору или только чтение"""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    or request.user.is_admin))


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_admin or request.user.is_staff