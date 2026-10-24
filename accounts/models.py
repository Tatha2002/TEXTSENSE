from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager


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


