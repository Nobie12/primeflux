import json
from unittest.mock import patch

import pytest


@pytest.mark.django_db
class TestUserView:
    def test_authenticated_user_can_view_profile(
        self,
        authenticated_client,
        user,
    ):
        response = authenticated_client.get("/api/v1/profile/")

        assert response.status_code == 200
        assert response.data["email"] == user.email

    def test_unauthenticated_user_cannot_view_profile(
        self,
        api_client,
    ):
        response = api_client.get("/api/v1/profile/")

        assert response.status_code == 401

    @patch("core.apps.accounts.views.profile.RedisClient")
    def test_cache_hit_returns_cached_data(
        self,
        mock_redis,
        authenticated_client,
        user,
    ):
        cached_data = {
            "email": user.email,
            "full_name": user.full_name,
        }

        mock_redis.return_value.get.return_value = json.dumps(cached_data)

        response = authenticated_client.get("/api/v1/profile/")

        assert response.status_code == 200
        assert response.data["email"] == user.email

    @patch("core.apps.accounts.views.profile.RedisClient")
    def test_cache_miss_stores_profile_data(
        self,
        mock_redis,
        authenticated_client,
    ):
        mock_redis.return_value.get.return_value = None

        response = authenticated_client.get("/api/v1/profile/")

        assert response.status_code == 200

        mock_redis.return_value.set.assert_called_once()

    @patch("core.apps.accounts.views.profile.RedisClient")
    def test_profile_update_invalidates_cache(
        self,
        mock_redis,
        authenticated_client,
        user,
    ):
        response = authenticated_client.patch(
            "/api/v1/profile/",
            {
                "full_name": "Updated Name",
            },
            format="json",
        )

        assert response.status_code == 200

        mock_redis.return_value.delete.assert_called_once_with(f"user_profile:{user.id}")

        user.refresh_from_db()

        assert user.full_name == "Updated Name"
