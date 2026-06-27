import django_filters

from .models import City, Hub


class CityFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
    )

    code = django_filters.CharFilter(
        field_name="code",
        lookup_expr="icontains",
    )

    class Meta:
        model = City
        fields = ["name", "code"]


class HubFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
    )

    city = django_filters.NumberFilter(
        field_name="city_id",
    )

    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Hub
        fields = [
            "name",
            "city",
            "is_active",
        ]
