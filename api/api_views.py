
from django.contrib.auth import authenticate
from datetime import datetime, timezone as datetime_timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN,)

from accounts.security.jwt_auth import (create_access_token, create_refresh_token, decode_refresh_token_payload)
from accounts.models import User, RevokedRefreshToken
from .serializers import (RegisterSerializer, LoginSerializer)

import secrets
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.utils import timezone

from rest_framework.permissions import AllowAny
from accounts.models import PasswordResetOTP
from .serializers import (ForgotPasswordSerializer, VerifyResetOTPSerializer, ResetPasswordSerializer)
User = get_user_model()



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

        email_or_phone = serializer.validated_data["email_or_phone"]
        password = serializer.validated_data["password"]

        user = authenticate(request=request, username=email_or_phone, password=password,)

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


class TestAuthAPIView(APIView):
    permission_classes = [IsAuthenticated]  # used only by authenticated users

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


# used for refreshing the access token using a valid refresh token
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


# API view for logging out the user by revoking the provided refresh token
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


# API view for handling forgot password requests
class ForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny]     # allow unauthenticated and authenticated users
    authentication_classes = []

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"].strip()
        user = User.objects.filter(email__iexact=email).first()

        # Use the same response whether the email exists or not.
        response_data = {
            "message": (
                "If an account exists with this email, "
                "an OTP will be sent."
            )
        }

        if user is None:
            return Response(response_data, status=HTTP_200_OK)

        now = timezone.now()
        reset_record = PasswordResetOTP.objects.filter(user=user).first()

        # Allow only one OTP request per minute per user.
        if (reset_record and reset_record.last_sent_at and now - reset_record.last_sent_at < timedelta(seconds=60)):
            return Response(response_data, status=HTTP_200_OK)

        # Generate a cryptographically random six-digit OTP.
        otp = str(secrets.randbelow(900000) + 100000)

        if reset_record is None:
            reset_record = PasswordResetOTP(user=user)

        # Store a hash, never the plain OTP.
        reset_record.otp_hash = make_password(otp)
        reset_record.otp_expires_at = now + timedelta(minutes=5)
        reset_record.otp_attempts = 0
        reset_record.last_sent_at = now
        reset_record.verified_at = None
        reset_record.reset_token_hash = ""
        reset_record.reset_token_expires_at = None
        reset_record.used_at = None

        reset_record.save()

        send_mail(subject="TEXTSENSE Password Reset OTP",
            message=(
                f"Hello {user.name},\n\n"
                f"Your password reset OTP is: {otp}\n\n"
                "This OTP expires in 5 minutes.\n"
                "Do not share this OTP with anyone."
            ),
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(response_data, status=HTTP_200_OK)


# API view for verifying the OTP sent to the user's email during password reset
class VerifyResetOTPAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = VerifyResetOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"].strip()
        otp = serializer.validated_data["otp"]

        user = User.objects.filter(email__iexact=email).first()

        if user is None:
            return Response({"message": "Invalid or expired OTP."}, status=HTTP_400_BAD_REQUEST)

        reset_record = PasswordResetOTP.objects.filter(user=user).first()

        if (reset_record is None or reset_record.used_at is not None or reset_record.verified_at is not None
            or not reset_record.otp_hash):

            return Response({"message": "Invalid or expired OTP."}, status=HTTP_400_BAD_REQUEST)

        now = timezone.now()

        if (reset_record.otp_expires_at is None or now >= reset_record.otp_expires_at):
            return Response({"message": "OTP has expired. Request a new OTP."}, status=HTTP_400_BAD_REQUEST)

        if reset_record.otp_attempts >= 5:
            return Response({"message": "Too many attempts. Request a new OTP."}, status=HTTP_400_BAD_REQUEST)

        # Count each attempt, including the successful one.
        reset_record.otp_attempts += 1

        if not check_password(otp, reset_record.otp_hash):
            reset_record.save(update_fields=["otp_attempts", "updated_at"])

            return Response({"message": "Invalid or expired OTP."}, status=HTTP_400_BAD_REQUEST)

        # OTP is correct. Invalidate it immediately.
        reset_record.otp_hash = ""
        reset_record.verified_at = now

        # Generate a temporary, single-use reset token.
        reset_token = secrets.token_urlsafe(32)

        reset_record.reset_token_hash = make_password(reset_token)
        reset_record.reset_token_expires_at = (now + timedelta(minutes=10))

        reset_record.save()

        return Response(
            {
                "message": "OTP verified successfully.",
                "reset_token": reset_token,
                "expires_in": 600,
            },
            status=HTTP_200_OK
        )


# API view for resetting the user's password using the reset token obtained after OTP verification
class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        email = data["email"].strip()
        reset_token = data["reset_token"]
        new_password = data["new_password"]

        user = User.objects.filter(email__iexact=email).first()

        if user is None:
            return Response({"message": "Invalid or expired reset token."}, status=HTTP_400_BAD_REQUEST)

        reset_record = PasswordResetOTP.objects.filter(user=user).first()

        if (reset_record is None or reset_record.verified_at is None or reset_record.used_at is not None
            or not reset_record.reset_token_hash):
            return Response({"message": "Invalid or expired reset token."}, status=HTTP_400_BAD_REQUEST)

        now = timezone.now()

        if (reset_record.reset_token_expires_at is None or now >= reset_record.reset_token_expires_at):
            return Response({"message": "Invalid or expired reset token."}, status=HTTP_400_BAD_REQUEST)

        if not check_password(reset_token, reset_record.reset_token_hash):
            return Response({"message": "Invalid or expired reset token."}, status=HTTP_400_BAD_REQUEST)

        # Apply Django's configured password validators.
        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as exc:
            return Response({"errors": {"new_password": exc.messages}}, status=HTTP_400_BAD_REQUEST)

        # Hash the new password using Django's standard mechanism.
        user.set_password(new_password)
        user.save(update_fields=["password"])

        # Make the reset token unusable after success.
        reset_record.used_at = now
        reset_record.reset_token_hash = ""
        reset_record.reset_token_expires_at = None
        reset_record.otp_hash = ""
        reset_record.save()

        return Response(
            {
                "message": (
                    "Password reset successful. "
                    "You can now log in with your new password."
                )
            },
            status=HTTP_200_OK
        )


