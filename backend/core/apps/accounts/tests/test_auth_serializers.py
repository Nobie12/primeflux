import pytest

from core.apps.accounts.serializers.auth import RegisterSerializer

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
