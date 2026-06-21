import pytest

from core.apps.accounts.filters import UserFilter
from core.apps.accounts.models import User


@pytest.mark.django_db
class TestUserFilter:
    def test_filter_by_role(self, user_data):
        User.objects.create_user(
            **{
                **user_data,
                "email": "admin@test.com",
                "phone": "0700000001",
                "national_id": "11111111",
                "role": "admin",
            }
        )

        customer = User.objects.create_user(
            **{
                **user_data,
                "email": "customer@test.com",
                "phone": "0700000002",
                "national_id": "22222222",
                "role": "customer",
            }
        )

        filtered = UserFilter(
            {"role": "customer"},
            queryset=User.objects.all(),
        ).qs

        assert filtered.count() == 1
        assert filtered.first() == customer

    def test_filter_by_phone(self, user):
        filtered = UserFilter(
            {"phone": user.phone},
            queryset=User.objects.all(),
        ).qs

        assert filtered.count() == 1
        assert filtered.first() == user

    def test_filter_by_email_verification(self, user_data):
        verified = User.objects.create_user(
            **{
                **user_data,
                "email": "verified@test.com",
                "phone": "0700000001",
                "national_id": "11111111",
                "is_email_verified": True,
            }
        )

        User.objects.create_user(
            **{
                **user_data,
                "email": "unverified@test.com",
                "phone": "0700000002",
                "national_id": "22222222",
                "is_email_verified": False,
            }
        )

        filtered = UserFilter(
            {"is_email_verified": True},
            queryset=User.objects.all(),
        ).qs

        assert filtered.count() == 1
        assert filtered.first() == verified

    def test_filter_by_full_name(self, user_data):
        john = User.objects.create_user(
            **{
                **user_data,
                "email": "john@test.com",
                "phone": "0700000001",
                "national_id": "11111111",
                "full_name": "John Doe",
            }
        )

        User.objects.create_user(
            **{
                **user_data,
                "email": "mary@test.com",
                "phone": "0700000002",
                "national_id": "22222222",
                "full_name": "Mary Jane",
            }
        )

        filtered = UserFilter(
            {"full_name__icontains": "john"},
            queryset=User.objects.all(),
        ).qs

        assert filtered.count() == 1
        assert filtered.first() == john
