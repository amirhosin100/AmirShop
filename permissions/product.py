from rest_framework.permissions import BasePermission


class IsProductOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if obj.market.marketer.user == request.user:
                return True

        return False
