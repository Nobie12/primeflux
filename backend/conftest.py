import pytest


@pytest.fixture
def user_data():
    """Default valid user data for testing."""
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "phone": "0712345678",
        "password": "testpassword",
        "national_id": "12345678",
    }
