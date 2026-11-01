from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse

from core.apps.accounts.models import User
from core.apps.fleet.models import Route, Vehicle, VehicleSchedule
from core.apps.logistics.models import City, Hub

pytestmark = pytest.mark.django_db


# ==============================================================================
# FIXTURES
# ==============================================================================


@pytest.fixture
def admin_user():
    return User.objects.create_user(
        email="admin@primeflux.com",
        full_name="Fleet Admin",
        phone="0712345678",
        role="admin",
        password="Password123!",
    )


@pytest.fixture
def driver_user():
    return User.objects.create_user(
        email="driver@primeflux.com",
        full_name="John Driver",
        phone="0712345679",
        role="driver",
        password="Password123!",
    )


@pytest.fixture
def customer_user():
    return User.objects.create_user(
        email="customer@primeflux.com",
        full_name="Jane Customer",
        phone="0712345680",
        role="customer",
        password="Password123!",
    )


@pytest.fixture
def hubs():
    city1 = City.objects.create(name="Nairobi", code="NBO")
    city2 = City.objects.create(name="Mombasa", code="MBA")
    hub1 = Hub.objects.create(name="Nairobi Central", city=city1)
    hub2 = Hub.objects.create(name="Mombasa Port", city=city2)
    return hub1, hub2


@pytest.fixture
def vehicle(driver_user):
    return Vehicle.objects.create(
        driver=driver_user,
        plate_number="KDA 123A",
        capacity_weight=1500.0,
        capacity_volume=12.5,
        vehicle_type="van",
        model="Toyota HiAce",
        status="available",
    )


@pytest.fixture
def route(hubs):
    hub1, hub2 = hubs
    return Route.objects.create(origin=hub1, destination=hub2, is_active=True)


# ==============================================================================
# VEHICLE TESTS
# ==============================================================================


class TestVehicleAPI:
    def test_admin_can_create_vehicle(self, api_client, admin_user, driver_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse("vehicle-list-create", kwargs={"version": "v1"})
        payload = {
            "driver": driver_user.id,
            "plate_number": "KDB 456B",
            "capacity_weight": 3000.0,
            "capacity_volume": 20.0,
            "vehicle_type": "lorry",
            "model": "Isuzu FRR",
            "status": "available",
        }
        response = api_client.post(url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["plate_number"] == "KDB 456B"

    def test_assigning_non_driver_fails(self, api_client, admin_user, customer_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse("vehicle-list-create", kwargs={"version": "v1"})
        payload = {
            "driver": customer_user.id,
            "plate_number": "KDC 789C",
            "capacity_weight": 1000.0,
            "capacity_volume": 8.0,
            "vehicle_type": "van",
            "model": "Nissan NV200",
        }
        response = api_client.post(url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "driver" in response.data

    def test_customer_cannot_create_vehicle(self, api_client, customer_user):
        api_client.force_authenticate(user=customer_user)
        url = reverse("vehicle-list-create", kwargs={"version": "v1"})
        response = api_client.post(url, {"plate_number": "KDD 000D"})
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ==============================================================================
# ROUTE TESTS
# ==============================================================================


class TestRouteAPI:
    def test_admin_can_create_route(self, api_client, admin_user, hubs):
        hub1, hub2 = hubs
        api_client.force_authenticate(user=admin_user)
        url = reverse("route-list-create", kwargs={"version": "v1"})
        payload = {"origin": hub1.id, "destination": hub2.id, "is_active": True}
        response = api_client.post(url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["origin_name"] == hub1.name

    def test_authenticated_user_can_list_routes(self, api_client, customer_user, route):
        api_client.force_authenticate(user=customer_user)
        url = reverse("route-list-create", kwargs={"version": "v1"})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1


# ==============================================================================
# VEHICLE SCHEDULE TESTS
# ==============================================================================


class TestVehicleScheduleAPI:
    def test_admin_can_create_schedule(self, api_client, admin_user, driver_user, vehicle, route):
        api_client.force_authenticate(user=admin_user)
        url = reverse("schedule-list-create", kwargs={"version": "v1"})
        now = timezone.now()
        payload = {
            "vehicle": vehicle.id,
            "route": route.id,
            "driver": driver_user.id,
            "departure_time": now + timedelta(hours=2),
            "arrival_time": now + timedelta(hours=8),
            "status": "scheduled",
        }
        response = api_client.post(url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "scheduled"

    def test_update_schedule_status(self, api_client, admin_user, driver_user, vehicle, route):
        now = timezone.now()
        sched = VehicleSchedule.objects.create(
            vehicle=vehicle,
            route=route,
            driver=driver_user,
            departure_time=now,
            arrival_time=now + timedelta(hours=5),
            status="scheduled",
        )
        api_client.force_authenticate(user=admin_user)
        url = reverse("schedule-detail", kwargs={"version": "v1", "pk": sched.id})
        response = api_client.patch(url, {"status": "departed"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "departed"
