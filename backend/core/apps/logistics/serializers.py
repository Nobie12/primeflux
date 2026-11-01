from rest_framework import serializers

from .models import City, Hub


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name", "code"]


class HubSerializer(serializers.ModelSerializer):
    city_details = CitySerializer(source="city", read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), source="city", write_only=True)

    class Meta:
        model = Hub
        fields = ["id", "name", "city_id", "city_details", "address", "is_active"]
