from rest_framework import permissions


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        owner = obj.view.get('owner_field_name')
        if request.user == owner:
            return True
        return False
