import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Fixture to provide a DRF APIClient instance."""
    return APIClient()


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
