from rest_framework import permissions
from apps.user.models import Marketer


class IsMarketer(permissions.BasePermission):

    def has_permission(self, request, view):
        if Marketer.objects.filter(user=request.user).exists():
            return True

        return False


class IsOwnerMarket(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.marketer.user == request.user:
            return True

        return False
