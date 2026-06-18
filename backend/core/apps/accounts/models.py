import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models

from core.apps.logistics.models import Hub

from .managers import DriverManager, UserManager


class Roles(models.TextChoices):
    CUSTOMER = "customer"
    DRIVER = "driver"
    ADMIN = "admin"


class User(AbstractBaseUser, PermissionsMixin):
    phone_regex = RegexValidator(
        regex=r"^(07|01)\d{8}$", message="Phone number must be 10 digits starting with '07' or '01'."
    )
    national_id_regex = RegexValidator(regex=r"^\d{8}$", message="National ID must be exactly 8 digits.")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    password = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=10,
        validators=[phone_regex],
        unique=True,
    )
    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.CUSTOMER)
    national_id = models.CharField(
        max_length=8,
        validators=[national_id_regex],
        unique=True,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "phone"]

    def __str__(self):
        return self.full_name


class Driver(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="driver_profile", limit_choices_to={"role": "driver"}
    )

    license_number = models.CharField(max_length=20, unique=True)
    is_available = models.BooleanField(default=True)
    current_hub = models.ForeignKey(
        Hub, on_delete=models.SET_NULL, null=True, blank=True, related_name="drivers_present"
    )
    is_verified = models.BooleanField(default=False)

    objects = DriverManager()

    def __str__(self):
        return f"Driver: {self.user.full_name}"
