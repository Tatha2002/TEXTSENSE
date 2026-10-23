from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from accounts.models import User
from accounts.security.jwt_auth import decode_access_token


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AuthenticationFailed("Authorization header must be: Bearer <token>")

        token = parts[1]
        user_id = decode_access_token(token)

        try:
            user = User.objects.get(id=user_id,is_active=True)

        except User.DoesNotExist as exc:
            raise AuthenticationFailed("User not found or inactive.") from exc

        return user, token
