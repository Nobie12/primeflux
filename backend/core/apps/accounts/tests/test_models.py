import uuid

import pytest
from django.db import IntegrityError

from core.apps.accounts.models import User


@pytest.mark.django_db
class TestUserModel:
    def test_id_is_uuid(self, user_data):
        user = User.objects.create_user(**user_data)

        assert isinstance(user.id, uuid.UUID)

    @pytest.mark.parametrize(
        "field",
        [
            "email",
            "phone",
            "national_id",
        ],
    )
    def test_unique_fields(self, user_data, field):
        """Test that duplicate email, phone, or national_id raises IntegrityError."""
        User.objects.create_user(**user_data)

        duplicate_data = {
            "full_name": "Duplicate User",
            "email": "different@example.com",
            "phone": "0789876543",
            "national_id": "88888888",
            "password": "differentpassword",
        }

        # Set the duplicate field to the same value as the original user
        duplicate_data[field] = user_data[field]

        with pytest.raises(IntegrityError):
            User.objects.create_user(**duplicate_data)

    def test_str_representation(self, user_data):
        user = User.objects.create_user(**user_data)
        assert str(user) == user.full_name

    def test_is_active_default(self, user_data):
        user = User.objects.create_user(**user_data)
        assert user.is_active is True

    def test_is_staff_default(self, user_data):
        user = User.objects.create_user(**user_data)
        assert user.is_staff is False

    def test_is_superuser_default(self, user_data):
        user = User.objects.create_user(**user_data)
        assert user.is_superuser is False

    def test_role_default(self, user_data):
        user = User.objects.create_user(**user_data)
        assert user.role == "customer"
