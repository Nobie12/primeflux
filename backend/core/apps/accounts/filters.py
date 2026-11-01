import django_filters

from .models import User


class UserFilter(django_filters.FilterSet):
    """A filter set for the User model."""

    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = User
        fields = {
            "phone": ["exact"],
            "national_id": ["exact"],
            "is_phone_verified": ["exact"],
            "is_email_verified": ["exact"],
            "role": ["exact"],
            "full_name": ["icontains"],
            "created_at": ["exact"],
        }
