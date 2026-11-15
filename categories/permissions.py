from rest_framework.permissions import BasePermission

class IsTextSenseAdmin(BasePermission):

    def has_permission(self, request, view):

        user = request.user

        return (user and user.is_authenticated
            and (
                user.is_superuser
                or user.role in [
                    "SUPER_USER",
                    "REACT_ADMIN"
                ]
            )
        )


# Note
# Django superusers can manage categories.
# React admins can manage categories.
# Normal React users cannot manage categories.