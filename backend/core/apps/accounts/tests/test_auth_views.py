from unittest.mock import patch

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


@pytest.mark.django_db
class TestSendOTPView:
    # Use the 'patch' decorator to intercept the service call
    # Make sure the path matches where the view IMPORTS the service
    @patch("core.core_functions.services.otp.OTPService.send_otp")
    def test_otp_is_generated(self, mock_send, api_client):
        # Define what the mock should return
        mock_send.return_value = (True, "OTP sent successfully.")

        url = reverse("send_otp")
        phone = "0723456789"

        response = api_client.post(url, {"phone": phone}, format="json")

        assert response.status_code == 200
        assert response.data["detail"] == "OTP sent successfully."

        # Optional: Verify the mock was actually called correctly
        mock_send.assert_called_once_with(phone)


@pytest.mark.django_db
class TestVerifyOTPView:
    @patch("core.core_functions.services.otp.OTPService.verify_otp")
    def test_verify_otp_success(self, mock_verify, api_client):
        # Setup: Create a user and the mock return value
        phone = "0712345678"
        user = User.objects.create_user(
            full_name="Test User", email="test@primeflux.com", phone=phone, password="password123"
        )
        assert user.is_phone_verified is False  # Pre-condition

        mock_verify.return_value = (True, "Verification successful.")
        url = reverse("verify_otp")

        # Action: Send the request
        response = api_client.post(url, {"phone": phone, "otp": "123456"}, format="json")

        # Assertions
        assert response.status_code == 200
        assert response.data["detail"] == "Verification successful."

        # CRITICAL: Check if the DB actually updated!
        user.refresh_from_db()
        assert user.is_phone_verified is True

    @patch("core.core_functions.services.otp.OTPService.verify_otp")
    def test_verify_otp_failure(self, mock_verify, api_client):
        phone = "0711111111"
        user = User.objects.create_user(
            full_name="Fail User", email="fail@primeflux.com", phone=phone, password="password123"
        )

        # Service returns failure (e.g. wrong code)
        mock_verify.return_value = (False, "Invalid OTP.")
        url = reverse("verify_otp")

        response = api_client.post(url, {"phone": phone, "otp": "000000"}, format="json")

        assert response.status_code == 400
        user.refresh_from_db()
        assert user.is_phone_verified is False


@pytest.mark.django_db
class TestEmailOTPViews:
    @patch("resend.Emails.send")
    def test_send_email_otp_success(self, mock_resend, api_client):
        """Test that email OTP is 'sent' and cooldown is triggered."""
        url = reverse("send_email_otp")
        email = "primeflux18@gmail.com"

        # Mocking the Resend response
        mock_resend.return_value = {"id": "test_id"}

        response = api_client.post(url, {"email": email}, format="json")

        assert response.status_code == 200
        assert response.data["detail"] == "OTP sent successfully."
        assert mock_resend.called

    @patch("resend.Emails.send")
    def test_send_email_otp_cooldown(self, mock_resend, api_client):
        """Test that sending twice quickly triggers a 429."""
        url = reverse("send_email_otp")
        email = "primeflux18@gmail.com"

        # First call
        api_client.post(url, {"email": email}, format="json")

        # Second call immediately after
        response = api_client.post(url, {"email": email}, format="json")

        assert response.status_code == 429
        assert "Please wait" in response.data["detail"]

    @patch("core.core_functions.services.otp.OTPService.verify_email_otp")
    def test_verify_email_otp_success(self, mock_verify, api_client):
        """Test that successful verification updates the User model."""
        email = "primeflux18@gmail.com"
        user = User.objects.create_user(full_name="Verify Me", email=email, phone="0700000000", password="password123")

        # Ensure initial state is False
        assert user.is_email_verified is False

        # Mock service to return success
        mock_verify.return_value = (True, "OTP verified successfully.")

        url = reverse("verify_email_otp")
        response = api_client.post(url, {"email": email, "otp": "123456"}, format="json")

        assert response.status_code == 200

        # Check DB update
        user.refresh_from_db()
        assert user.is_email_verified is True
