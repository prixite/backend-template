from rest_framework import permissions

from core.models import SIGNUP_USER


class SignupPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True

        return request.user.username == SIGNUP_USER


class UserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True

        post_allowed_actions = ['send_link']
        action_allowed = view.action not in post_allowed_actions

        if request.method == 'POST' and action_allowed:
            return False

        return True


class IsAdminOrReadonly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff or request.method in permissions.SAFE_METHODS:
            return True

        return False


class IsDefaultUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.email == SIGNUP_USER
        )


class IsNotDefaultUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if (request.user and
                request.user.is_authenticated and
                request.user.email == SIGNUP_USER):
            return False
        return True
