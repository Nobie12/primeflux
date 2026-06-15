import os

import pytest
from rest_framework.test import APIClient


def pytest_configure():
    """
    Forcefully inject secure fallbacks into the process environment
    before Django initializes the project settings layer.
    """
    os.environ.setdefault("SECRET_KEY", "ci-test-insecure-signing-key-string-value-here")
    os.environ.setdefault("RESEND_API_KEY", "re_mock_testing_key")


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
