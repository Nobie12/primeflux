from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as BaseTokenSerializer

from core.apps.accounts.models import User

# Match your UserManager: 07 or 01 followed by 8 digits
kenyan_phone_regex = r"^(07|01)\d{8}$"
phone_validator = RegexValidator(
    regex=kenyan_phone_regex, message="Phone number must be 10 digits starting with '07' or '01'."
)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["full_name", "email", "password", "national_id", "phone", "role"]

    def validate_email(self, value):
        return value.lower()

    def validate(self, attrs):
        if attrs.get("role") == "driver" and not attrs.get("national_id"):
            raise serializers.ValidationError("National ID is required for drivers.")

        return attrs

    def create(self, validated_data):

        return User.objects.create_user(**validated_data)


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
