import pytest

from core.apps.accounts.serializers.user import UserSerializer


@pytest.mark.django_db
class TestUserSerializer:
    def test_serializer_contains_expected_fields(self, user):
        data = UserSerializer(user).data

        expected_fields = {
            "id",
            "email",
            "phone",
            "full_name",
            "role",
            "is_email_verified",
            "is_phone_verified",
            "created_at",
        }

        assert set(data.keys()) == expected_fields

    def test_serializer_returns_correct_values(self, user):
        data = UserSerializer(user).data

        assert data["email"] == user.email
        assert data["phone"] == user.phone
        assert data["full_name"] == user.full_name

    def test_read_only_fields_cannot_be_updated(self, user, user_data):
        serializer = UserSerializer(
            user,
            data={
                "email": "new@example.com",
                "phone": "0799999999",
                "full_name": "Updated Name",
            },
            partial=True,
        )

        assert serializer.is_valid()

        updated_user = serializer.save()

        updated_user.refresh_from_db()

        assert updated_user.full_name == "Updated Name"

        assert updated_user.email == user_data["email"]
        assert updated_user.phone == user_data["phone"]
