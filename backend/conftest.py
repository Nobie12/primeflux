import pytest
from rest_framework.test import APIClient

from core.apps.accounts.models import User


@pytest.fixture
def api_client():
    """Provide a DRF APIClient instance."""
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


@pytest.fixture
def user(user_data):
    """Create and return a test user."""
    return User.objects.create_user(**user_data)


@pytest.fixture
def authenticated_client(api_client, user):
    """Authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client
