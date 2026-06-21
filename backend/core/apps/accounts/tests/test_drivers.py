import pytest

from core.apps.accounts.models import Driver, Roles, User
from core.apps.accounts.serializers.auth import RegisterSerializer
from core.apps.logistics.models import Hub, Location


@pytest.fixture
def test_setup_data(db):
    """Sets up locations, hubs, and base drivers for structural querying tests."""
    location = Location.objects.create(name="Nairobi Central", code="NBO")
    hub_alpha = Hub.objects.create(name="Hub Alpha", Location=location, is_active=True)
    hub_beta = Hub.objects.create(name="Hub Beta", Location=location, is_active=True)

    # Driver 1: Available, stationed at Hub Alpha
    u1 = User.objects.create_user(
        email="driver1@primeflux.com",
        full_name="Driver One",
        phone="0711111111",
        password="password",
        role=Roles.DRIVER,
        national_id="11111111",
    )
    d1 = Driver.objects.create(user=u1, license_number="DL111111", is_available=True, current_hub=hub_alpha)

    # Driver 2: Unavailable, stationed at Hub Beta
    u2 = User.objects.create_user(
        email="driver2@primeflux.com",
        full_name="Driver Two",
        phone="0722222222",
        password="password",
        role=Roles.DRIVER,
        national_id="22222222",
    )
    d2 = Driver.objects.create(user=u2, license_number="DL222222", is_available=False, current_hub=hub_beta)

    return {
        "hub_alpha": hub_alpha,
        "hub_beta": hub_beta,
        "driver_available": d1,
        "driver_unavailable": d2,
    }


@pytest.mark.django_db
class TestDriverManagerAndQuerySet:
    """Tests custom QuerySet filters of DriverManager."""

    def test_queryset_available_filter(self, test_setup_data):
        available_drivers = Driver.objects.available()
        assert available_drivers.count() == 1
        assert test_setup_data["driver_available"] in available_drivers
        assert test_setup_data["driver_unavailable"] not in available_drivers

    def test_queryset_located_at_filter(self, test_setup_data):
        hub_alpha = test_setup_data["hub_alpha"]
        hub_beta = test_setup_data["hub_beta"]

        drivers_at_alpha = Driver.objects.located_at(hub_id=hub_alpha.id)
        drivers_at_beta = Driver.objects.located_at(hub_id=hub_beta.id)

        assert drivers_at_alpha.count() == 1
        assert drivers_at_beta.count() == 1
        assert test_setup_data["driver_available"] in drivers_at_alpha
        assert test_setup_data["driver_unavailable"] in drivers_at_beta


@pytest.mark.django_db
class TestDriverRegistrationPipeline:
    """Tests the driver creation path inside RegisterSerializer, including edge cases."""

    def test_successful_driver_registration_creates_profile(self, user_data):
        """Verify driver registration provisions both the User and the Driver profile."""
        data = user_data.copy()
        data.update(
            {
                "email": "newdriver@primeflux.com",
                "phone": "0799999999",
                "national_id": "99999999",
                "role": "driver",
                "license_number": "dl99382a",  # Sent in lowercase to test upper string cleanup
            }
        )

        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        user = serializer.save()

        # Check User Row properties
        assert user.role == Roles.DRIVER

        # Check Driver Row properties
        assert hasattr(user, "driver_profile")
        assert user.driver_profile.license_number == "DL99382A"  # Upper string formatting transformation verified
        assert user.driver_profile.is_available is True
        assert user.driver_profile.is_verified is False

    @pytest.mark.parametrize(
        "invalid_dl",
        [
            "DL",  # Too short
            "DL1234567890123",  # Too long
            "DL-1234!",  # Special characters outside alpha-numeric regex bounds
        ],
    )
    def test_driver_registration_invalid_license_format(self, user_data, invalid_dl):
        """Ensures bad driving license configurations fail validation hooks."""
        data = user_data.copy()
        data.update(
            {
                "email": "bad_dl@primeflux.com",
                "phone": "0788888888",
                "national_id": "88888888",
                "role": "driver",
                "license_number": invalid_dl,
            }
        )

        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "license_number" in serializer.errors


@pytest.mark.django_db
class TestDriverModelEnforcements:
    """Tests hard database constraints on Driver Profiles."""

    def test_duplicate_license_number_raises_integrity_error(self, test_setup_data, user_data):
        """Ensures unique constraint rules prevent duplicated licenses at database boundaries."""
        from django.db import IntegrityError

        # Create a new standalone user with role=driver
        u = User.objects.create_user(
            email="cheater@primeflux.com",
            full_name="Copy Cat",
            phone="0755555555",
            password="password",
            role=Roles.DRIVER,
            national_id="55555555",
        )

        # Attempt to inject an existing license number used by test_setup_data fixture
        with pytest.raises(IntegrityError):
            Driver.objects.create(
                user=u,
                license_number="DL111111",  # Already assigned to Driver One
            )
