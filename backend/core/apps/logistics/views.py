import json

from rest_framework import generics, serializers
from rest_framework.response import Response

from core.core_functions.permissions import IsReadOnlyOrAdmin, IsRole
from core.core_functions.services.cache.redis_client import RedisClient

from .filters import CityFilter, HubFilter
from .models import City, Hub
from .serializers import CitySerializer, HubSerializer

CACHE_KEY_HUBS = "logistics:hubs:active"


class CityListCreateView(generics.ListCreateAPIView):
    queryset = City.objects.all().order_by("name")
    serializer_class = CitySerializer
    permission_classes = [IsReadOnlyOrAdmin]

    filterset_class = CityFilter

    search_fields = ["name", "code", "id"]
    ordering_fields = ["name", "code"]


class HubListCreateView(generics.ListCreateAPIView):
    queryset = Hub.objects.select_related("city").filter(is_active=True).order_by("name")
    serializer_class = HubSerializer
    permission_classes = [IsReadOnlyOrAdmin]

    filterset_class = HubFilter

    search_fields = ["name", "address", "city__name"]
    ordering_fields = ["city__name", "created_at"]

    def list(self, request, *args, **kwargs):
        """
        Get cached result. If not list from db and the cache
        """
        redis = RedisClient()
        cached_hubs = redis.get(CACHE_KEY_HUBS)

        if cached_hubs:
            return Response(json.loads(cached_hubs))

        response = super().list(request, *args, **kwargs)
        redis.set(CACHE_KEY_HUBS, json.dumps(response.data), ex=86400)
        return response

    def perform_create(self, serializer: serializers.BaseSerializer) -> None:
        serializer.save()
        RedisClient().delete(CACHE_KEY_HUBS)


class HubRetrieveDestroyUpdate(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles fetching, updating, or deleting a SPECIFIC city asset
    via its unique ID identifier path parameter.
    """

    queryset = Hub.objects.select_related("city").all()
    serializer_class = HubSerializer
    permission_classes = [IsRole.for_roles("admin")]

    def perform_update(self, serializer: serializers.BaseSerializer) -> None:
        serializer.save()
        RedisClient().delete(CACHE_KEY_HUBS)

    def perform_destroy(self, instance: Hub) -> None:
        instance.delete()
        RedisClient().delete(CACHE_KEY_HUBS)


class CityRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles fetching, updating, or deleting a SPECIFIC geopolitical Location.
    """

    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsReadOnlyOrAdmin]
