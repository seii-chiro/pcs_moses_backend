from rest_framework import permissions

class IsAdministratorUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Check if the user is in the "Administrator" group
            return request.user.groups.filter(name='Administrator').exists()
        return False