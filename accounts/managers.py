from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, phone, password=None, name=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        if not phone:
            raise ValueError("Phone number is required")

        email = self.normalize_email(email)

        # Normal React users by default
        extra_fields.setdefault("role", self.model.REACT_USER)

        user = self.model(email=email,phone=phone,name=name,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user


    def create_superuser(self, email, phone, password=None, name=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        # Django superuser must always have SUPERUSER role
        extra_fields["role"] = self.model.SUPER_USER

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email=email,phone=phone,password=password,name=name,**extra_fields)


