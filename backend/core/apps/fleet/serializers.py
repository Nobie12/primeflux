from rest_framework import serializers

from .models import Route, Vehicle, VehicleSchedule


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = "__all__"

    def validate_driver(self, value):
        if value and value.role != "driver":
            raise serializers.ValidationError("Assigned user account taxonomy must possess the role 'driver'.")
        return value


class RouteSerializer(serializers.ModelSerializer):
    origin_name = serializers.ReadOnlyField(source="origin.name")
    destination_name = serializers.ReadOnlyField(source="destination.name")

    class Meta:
        model = Route
        fields = "__all__"


class VehicleScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleSchedule
        fields = "__all__"
