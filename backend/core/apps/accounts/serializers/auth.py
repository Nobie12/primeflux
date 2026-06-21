import re

from django.core.validators import RegexValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as BaseTokenSerializer

from core.apps.accounts.models import Driver, User

# Match your UserManager: 07 or 01 followed by 8 digits
kenyan_phone_regex = r"^(07|01)\d{8}$"
phone_validator = RegexValidator(
    regex=kenyan_phone_regex, message="Phone number must be 10 digits starting with '07' or '01'."
)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    phone = serializers.CharField(validators=[phone_validator])
    license_number = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["full_name", "email", "password", "national_id", "phone", "role", "license_number"]

    def validate_email(self, value):
        return value.lower()

    def validate(self, attrs):
        role = attrs.get("role", "customer")
        license_number = attrs.get("license_number", "").strip().upper()
        national_id = attrs.get("national_id")

        # --- PROCESSING DRIVER SIGNUP ---
        if role == "driver":
            if not national_id or not license_number:
                raise serializers.ValidationError(
                    "Both National ID and License number are strictly required for drivers."
                )

            dl_regex = r"^[A-Z0-9]{6,12}$"
            if not re.match(dl_regex, license_number):
                raise serializers.ValidationError(
                    {"license_number": "Invalid driving license format. Must be 6-12 alphanumeric characters."}
                )

            # Assign the cleaned, uniform uppercase string back to attrs
            attrs["license_number"] = license_number

        return attrs

    def create(self, validated_data):
        """
        User creation with automatic driver creation if user is a driver with an atomic transaction
        """
        license_number = validated_data.pop("license_number", None)
        role = validated_data.get("role", "customer")

        """The Atomic transaction"""
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)

            if role == "driver" and license_number:
                Driver.objects.create(user=user, license_number=license_number, is_available=True, is_verified=False)

        return user


class TokenObtainPairSerializer(BaseTokenSerializer):
    @classmethod
    def get_token(cls, user):
        """
        Runs when the token is being GENERATED.
        Adds data to the ENCODED hash.
        """
        token = super().get_token(user)
        token["role"] = user.role
        return token

    def validate(self, attrs):

        data = super().validate(attrs)

        data["user"] = {
            "full_name": self.user.full_name,
            "email": self.user.email,
            "phone": self.user.phone,
        }

        return data


class SendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(validators=[phone_validator])


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(validators=[phone_validator])
    otp = serializers.CharField(
        min_length=6, max_length=6, validators=[RegexValidator(r"^\d{6}$", "OTP must contain only digits.")]
    )


class SendEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(
        min_length=6, max_length=6, validators=[RegexValidator(r"^\d{6}$", "OTP must contain only digits.")]
    )
