from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from django.conf import settings
from django.utils import timezone


class User(AbstractUser):
    SUPER_USER = "SUPER_USER"
    REACT_ADMIN = "REACT_ADMIN"
    REACT_USER = "REACT_USER"

    ROLE_CHOICES = [
        (SUPER_USER, "SUPER_USER"),
        (REACT_ADMIN, "REACT_ADMIN"),
        (REACT_USER, "REACT_USER"),
    ]

    username = None
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=20,choices=ROLE_CHOICES,default=REACT_USER)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone", "name"]

    objects: UserManager = UserManager()

    def __str__(self):
        return self.email


# JTI stands for JWT ID (JSON Web Token ID). Stores the unique ID of the revoked refresh token.
class RevokedRefreshToken(models.Model):
    jti = models.CharField(max_length=50, unique=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.jti


# Model to store OTP and reset token for password reset functionality
class PasswordResetOTP(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="password_reset_otp")
    otp_hash = models.CharField(max_length=128, blank=True)
    otp_expires_at = models.DateTimeField(null=True, blank=True)
    otp_attempts = models.PositiveSmallIntegerField(default=0)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    reset_token_hash = models.CharField(max_length=128, blank=True)
    reset_token_expires_at = models.DateTimeField(null=True,blank=True)

    used_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Password reset for {self.user.email}"


