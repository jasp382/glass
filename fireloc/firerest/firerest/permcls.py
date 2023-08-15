"""
Permissions related
"""

from rest_framework.permissions import BasePermission

class IsFireloc(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='fireloc').exists()
