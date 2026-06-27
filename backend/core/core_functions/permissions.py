from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsRole(BasePermission):
    """ "
    Stateless Role-Based Access Control evaluating user taxonomy parameters.
    """

    def __init__(self, allowed_roles: tuple[str, ...]) -> None:
        self.allowed_roles = allowed_roles

    @classmethod
    def for_roles(cls, *roles):
        return lambda: cls(roles)

    def has_permission(self, request, view):
        role = getattr(request.user, "role", None)

        return bool(request.user and request.user.is_authenticated and role in self.allowed_roles)


class IsReadOnlyOrAdmin(BasePermission):
    """
    Grants read-only operations to any authenticated token,
    but strictly guards mutations (POST, PUT, PATCH, DELETE) for System Admins.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        if request.method in SAFE_METHODS:
            return True

        return getattr(request.user, "role", None) == "admin"
