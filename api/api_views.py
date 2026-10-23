
from django.contrib.auth import authenticate
from datetime import datetime, timezone as datetime_timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN,)

from accounts.security.jwt_auth import (create_access_token, create_refresh_token, decode_refresh_token_payload)
from accounts.models import User, RevokedRefreshToken
from .serializers import (RegisterSerializer,LoginSerializer,)


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=HTTP_400_BAD_REQUEST,)

        user = serializer.save()

        return Response({
            "message": "Registration successful..",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "role": user.role,
            },
        }, status=HTTP_201_CREATED)


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors}, status=HTTP_400_BAD_REQUEST)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(request=request,username=username,password=password,)

        if user is None or not user.is_active:
            return Response({"message": "Invalid email/phone or password."}, status=HTTP_401_UNAUTHORIZED,)

        access_token = create_access_token(user.id, user.role)
        refresh_token = create_refresh_token(user.id, user.role)

        return Response({
            "message": "Login successful.",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "role": user.role,
            },
            "tokens": {
                "access": access_token,
                "refresh": refresh_token,
            },
        }, status=HTTP_200_OK)


# class CreateReactAdminAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         # Must be the Django superuser, not merely a staff user.
#         if not request.user.is_superuser:
#             return Response(
#                 {"message": "Only a Django superuser can create React admins."},
#                 status=HTTP_403_FORBIDDEN,
#             )

#         serializer = ReactAdminCreateSerializer(data=request.data)

#         if not serializer.is_valid():
#             return Response(
#                 {"errors": serializer.errors},
#                 status=HTTP_400_BAD_REQUEST,
#             )

#         user = serializer.save()

#         return Response({
#             "message": "React admin created successfully.",
#             "user": {
#                 "id": user.id,
#                 "name": user.name,
#                 "email": user.email,
#                 "phone": user.phone,
#                 "role": user.role,
#             },
#         }, status=HTTP_201_CREATED)


class TestAuthAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            "message": "Authentication successful.",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "role": user.role,
            },
        }, status=HTTP_200_OK)


class RefreshAPIView(APIView):

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not isinstance(refresh_token, str) or not refresh_token:
            return Response({"message": "Refresh token is required."}, status=HTTP_400_BAD_REQUEST,)

        # Validate the refresh token and retrieve its payload.
        try:
            payload = decode_refresh_token_payload(refresh_token)
        except AuthenticationFailed as exc:
            return Response({"message": str(exc)}, status=HTTP_401_UNAUTHORIZED)

        # Reject refresh tokens that have already been revoked.
        if RevokedRefreshToken.objects.filter(jti=payload["jti"]).exists():
            return Response({"message": "Refresh token has been revoked."}, status=HTTP_401_UNAUTHORIZED)

        # Confirm that the user still exists and is active.
        try:
            user = User.objects.get(id=payload["user_id"], is_active=True,)
        except User.DoesNotExist:
            return Response({"message": "User not found or inactive."}, status=HTTP_401_UNAUTHORIZED,)

        # Use the current database role, not the old token's role.
        access_token = create_access_token(user.id,user.role)

        return Response(
            {
                "message": "Access token refreshed successfully.",
                "access_token": access_token,
            },
            status=HTTP_200_OK,
        )


class LogoutAPIView(APIView):

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not isinstance(refresh_token, str) or not refresh_token:
            return Response({"message": "Refresh token is required."}, status=HTTP_400_BAD_REQUEST)

        # Validate the refresh token before revoking it.
        try:
            payload = decode_refresh_token_payload(refresh_token)
        except AuthenticationFailed as exc:
            return Response({"message": str(exc)}, status=HTTP_401_UNAUTHORIZED)

        jti = payload["jti"]

        # Make logout safe to repeat for an already-revoked token.
        if RevokedRefreshToken.objects.filter(jti=jti).exists():
            return Response({"message": "Refresh token has already been revoked."}, status=HTTP_200_OK)

        expires_at = datetime.fromtimestamp(payload["exp"], tz=datetime_timezone.utc)
        RevokedRefreshToken.objects.create(jti=jti,expires_at=expires_at,)

        return Response({"message": "Logged out successfully."}, status=HTTP_200_OK)
