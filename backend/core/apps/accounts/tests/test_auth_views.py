import pytest
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken

from core.apps.accounts.models import User

"""
test login and logout views.
"""


@pytest.mark.django_db
class TestLoginView:
    """
    Test if the pair tokens are returned and are valid, and if
    the role is embeded in the access and extra fields added to the token.
    """

    def test_tokens_returned(self, api_client, user_data):
        raw_password = user_data["password"]
        user = User.objects.create_user(**user_data)

        url = reverse("login")

        response = api_client.post(
            url,
            {
                "email": user_data["email"],
                "password": raw_password,
            },
            format="json",
        )

        # test if the tokens are returned
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

        # test if the access token is valid and contains the role
        access_token = response.data["access"]
        token = AccessToken(access_token)  # deode the token to check its content

        assert token["role"] == "customer"
        assert token["user_id"] == str(user.id)

        # assert the extra fields are added as json to the response and not the token
        assert response.data["user"]["email"] == user_data["email"]
        assert response.data["user"]["full_name"] == user_data["full_name"]
        assert response.data["user"]["phone"] == user_data["phone"]


@pytest.mark.django_db
class TestLogoutView:
    """
    Test if the refresh token is blacklisted after logout.
    """

    def test_logout(self, api_client, user_data):
        raw_password = user_data["password"]
        User.objects.create_user(**user_data)

        url = reverse("login")

        response = api_client.post(
            url,
            {
                "email": user_data["email"],
                "password": raw_password,
            },
            format="json",
        )

        access_token = response.data["access"]
        refresh_token = response.data["refresh"]

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Logout
        logout_url = reverse("logout")
        response = api_client.post(
            logout_url,
            {
                "refresh": refresh_token,
            },
            format="json",
        )

        assert response.status_code == 205
        assert response.data["message"] == "Successfully logged out."
