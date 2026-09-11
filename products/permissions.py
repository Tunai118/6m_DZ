from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    message = 'Only moderators can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and request.method != 'POST'
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and request.method != 'POST'
        )