import pytest

from core.apps.accounts.serializers.auth import RegisterSerializer, SendOTPSerializer, VerifyOTPSerializer

"""
Test auth serializers.
"""


@pytest.mark.django_db
class TestRegisterSerializer:
    """
    Test email is normalized and national_id is required for drivers.
    """

    def test_email_normalization(self, user_data):
        serializer = RegisterSerializer(data=user_data)

        assert serializer.is_valid()
        assert serializer.validated_data["email"] == user_data["email"].lower()

    def test_national_id_required_for_drivers(self, user_data):
        user_data["role"] = "driver"
        user_data["national_id"] = None

        serializer = RegisterSerializer(data=user_data)

        assert not serializer.is_valid()

        assert "non_field_errors" in serializer.errors
        assert "National ID is required for drivers." in str(serializer.errors["non_field_errors"])


class TestOTPIdSerializers:
    @pytest.mark.parametrize(
        "phone, is_valid",
        [
            ("0712345678", True),
            ("0112345678", True),
            ("071234567", False),
            ("07123456789", False),
            ("254712345678", False),
            ("abcdefghij", False),
        ],
    )
    def test_send_otp_serializer_validation(self, phone, is_valid):
        data = {"phone": phone}
        serializer = SendOTPSerializer(data=data)
        assert serializer.is_valid() == is_valid

    @pytest.mark.parametrize(
        "phone, otp, is_valid",
        [
            ("0712345678", "123456", True),
            ("0712345678", "12345", False),
            ("0712345678", "1234567", False),
            ("0712345678", "abcdef", False),
            ("12345", "123456", False),
        ],
    )
    def test_verify_otp_serializer_validation(self, phone, otp, is_valid):
        data = {"phone": phone, "otp": otp}
        serializer = VerifyOTPSerializer(data=data)
        assert serializer.is_valid() == is_valid
