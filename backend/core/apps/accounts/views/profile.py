import json

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.apps.accounts.serializers.user import UserSerializer
from core.core_functions.services.cache.redis_client import RedisClient


class UserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Get the actual model instance of the user"""
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        """Retrieve the cached data and if not cache it"""
        client = RedisClient()

        cache_key = f"user_profile:{request.user.id}"

        cached_data = client.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))

        user = self.get_object()
        data = self.get_serializer(user).data

        client.set(
            cache_key,
            json.dumps(data),
            ex=3600,
        )

        return Response(data)

    def perform_update(self, serializer):
        user = serializer.save()

        client = RedisClient()
        client.delete(f"user_profile:{user.id}")
