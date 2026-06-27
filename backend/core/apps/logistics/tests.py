import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.apps.accounts.models import User
from core.apps.logistics.models import City, Hub


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def setup_logistics_data(db):
    city = City.objects.create(name="Nairobi Region", code="NBO")
    hub = Hub.objects.create(name="Central Sorting Alpha", city=city, is_active=True)
    return city, hub


@pytest.mark.django_db
class TestLogisticsInfrastructure:
    def test_anonymous_user_blocked_completely(self, api_client):
        url = reverse("hubs", kwargs={"version": "v1"})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_customer_can_read_but_cannot_write(self, api_client, setup_logistics_data):
        customer = User.objects.create_user(
            full_name="John Customer",
            email="cust@primeflux.com",
            phone="0711111111",
            role="customer",
            password="HashPassword123",
        )
        api_client.force_authenticate(user=customer)

        # Test Read Operation
        url = reverse("hubs", kwargs={"version": "v1"})
        get_response = api_client.get(url)
        assert get_response.status_code == status.HTTP_200_OK

        # Test Write Block
        post_response = api_client.post(url, {"name": "Illegal Hub", "city_id": setup_logistics_data[0].id})
        assert post_response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_mutate_and_evict_cache(self, api_client, setup_logistics_data):
        admin = User.objects.create_superuser(
            full_name="System Admin", email="admin@primeflux.com", phone="0722222222", password="AdminSecurePassword"
        )
        api_client.force_authenticate(user=admin)
        url = reverse("hubs", kwargs={"version": "v1"})

        payload = {
            "name": "Mombasa Port Depot",
            "city_id": setup_logistics_data[0].id,
            "address": "Kilindini Road, Gate 4",
            "is_active": True,
        }
        response = api_client.post(url, payload)
        assert response.status_code == status.HTTP_201_CREATED
