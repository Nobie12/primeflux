import pytest

from core.apps.accounts.models import Roles, User


@pytest.mark.django_db
class TestUserManager:
    def test_create_user(self):
        user = User.objects.create_user(
            email="test@example.com", full_name="Test User", phone="0712345678", password="testpassword"
        )
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.phone == "0712345678"
        assert user.check_password("testpassword")

    def test_email_normalization(self):
        email = "TEST@EXAMPLE.COM"
        user = User.objects.create_user(
            email=email, full_name="Test User", phone="0712345678", password="testpassword"
        )
        assert user.email == "TEST@example.com"

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email="superuser@example.com", full_name="Super User", phone="0711223344", password="superpassword"
        )
        assert superuser.email == "superuser@example.com"
        assert superuser.full_name == "Super User"
        assert superuser.phone == "0711223344"
        assert superuser.check_password("superpassword")
        assert superuser.is_staff is True
        assert superuser.is_superuser is True

    @pytest.mark.parametrize(
        "missing_field, value, expected_message",
        [
            ("email", "", "The email field is required."),
            ("email", None, "The email field is required."),
            ("full_name", "", "The full name field is required."),
            ("full_name", None, "The full name field is required."),
            ("phone", "", "The phone field is required."),
            ("phone", None, "The phone field is required."),
            ("password", "", "The password field is required."),
            ("password", None, "The password field is required."),
        ],
    )
    def test_create_user_with_missing_required_fields(self, missing_field, value, expected_message, user_data):
        """Test that missing required fields raises ValueError with appropriate message."""

        base_data = user_data.copy()  # Use the fixture data as base

        base_data[missing_field] = value

        with pytest.raises(ValueError) as exec_info:
            User.objects.create_user(**base_data)
        assert expected_message in str(exec_info.value)

    @pytest.mark.parametrize(
        "invalid_phone",
        [
            "071234567",  # 9 digits (Too short)
            "07123456789",  # 11 digits (Too long)
            "0212345678",  # Starts with 02 (Forbidden)
            "abcdefghij",  # Non-numeric
            "7123456789",  # Missing leading 0
        ],
    )
    def test_create_user_invalid_phone_raises_error(self, user_data, invalid_phone):
        """Test that invalid phone formats raise ValueError with specific message."""
        data = user_data.copy()
        data["phone"] = invalid_phone

        expected_msg = "Phone number must be 10 digits starting with '07' or '01'."

        with pytest.raises(ValueError, match=expected_msg):
            User.objects.create_user(**data)

    def test_create_user_valid_phone_prefixes(self, user_data):
        """Test that both 07 and 01 prefixes are accepted."""
        # Test 01 prefix
        data_01 = user_data.copy()
        data_01["phone"] = "0112345678"
        data_01["email"] = "01@example.com"
        user_01 = User.objects.create_user(**data_01)
        assert user_01.phone.startswith("01")

        # Test 07 prefix
        data_07 = user_data.copy()
        data_07.pop("national_id", 87654321)
        data_07["phone"] = "0712345678"
        data_07["email"] = "07@example.com"
        user_07 = User.objects.create_user(**data_07)
        assert user_07.phone.startswith("07")

    ### --- NATIONAL ID VALIDATION TESTS --- ###

    @pytest.mark.parametrize(
        "invalid_id",
        [
            "1234567",  # 7 digits
            "123456789",  # 9 digits
            "123A5678",  # Contains a letter
            "0000000",  # Too short
        ],
    )
    def test_create_user_invalid_national_id_raises_error(self, user_data, invalid_id):
        """Test that invalid National ID lengths or formats raise ValueError."""
        data = user_data.copy()
        data["national_id"] = invalid_id

        expected_msg = "National ID must be exactly 8 digits."

        with pytest.raises(ValueError, match=expected_msg):
            User.objects.create_user(**data)

    def test_create_user_with_none_national_id(self, user_data):
        """Ensure national_id can be None (if your model allows it)."""
        data = user_data.copy()
        data["national_id"] = None
        user = User.objects.create_user(**data)
        assert user.national_id is None

    def test_create_driver(self, user_data):
        # Overriding the default manually
        user_data.pop("role", None)  # Remove it if it exists
        user = User.objects.create_user(**user_data, role=Roles.DRIVER)
        assert user.role == Roles.DRIVER  # Verified!
