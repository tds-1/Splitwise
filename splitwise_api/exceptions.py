from rest_framework.exceptions import PermissionDenied


class AuthenticationError(PermissionDenied):
    default_detail = "User not authenticated"
