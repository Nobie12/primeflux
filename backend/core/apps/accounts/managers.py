import re
from typing import cast

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom manager for the User model.
    Handles user and superuser creation.
    """

    def create_user(
        self,
        full_name: str,
        email: str,
        password: str,
        phone: str,
        role: str = "customer",
        national_id: str | None = None,
        **extra_fields,
    ):
        required_fields = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "password": password,
        }

        for field_name, value in required_fields.items():
            if not value:
                raise ValueError(f"The {field_name.replace('_', ' ')} field is required.")

        if not re.match(r"^(07|01)\d{8}$", phone):
            raise ValueError("Phone number must be 10 digits starting with '07' or '01'.")

        if national_id:
            if not re.match(r"^\d{8}$", str(national_id)):
                raise ValueError("National ID must be exactly 8 digits.")

        email = self.normalize_email(email)

        user = cast(
            AbstractBaseUser,
            self.model(
                full_name=full_name,
                email=email,
                phone=phone,
                role=role or "customer",
                national_id=national_id,
                **extra_fields,
            ),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        full_name: str,
        email: str,
        password: str,
        phone: str,
        role: str = "admin",
        national_id: str | None = None,
        **extra_fields,
    ):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            full_name=full_name,
            email=email,
            password=password,
            phone=phone,
            role="admin",
            national_id=national_id,
            **extra_fields,
        )


class DriverManagerQuerySet(models.QuerySet):
    def available(self):
        return self.filter(is_available=True)

    def located_at(self, hub_id):
        return self.filter(current_hub_id=hub_id)


class DriverManager(models.Manager):
    """
    Statically defined manager that safely exposes custom QuerySet methods
    to satisfy mypy static type checking rules.
    """

    def get_queryset(self) -> DriverManagerQuerySet:
        return DriverManagerQuerySet(self.model, using=self._db)

    def available(self):
        return self.get_queryset().available()

    def located_at(self, hub_id):
        return self.get_queryset().located_at(hub_id)
