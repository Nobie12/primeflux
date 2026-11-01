from rest_framework import serializers

from core.apps.accounts.models import Driver
from core.apps.accounts.serializers.user import UserSerializer


class DriverProfileSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source="user", read_only=True)
    current_hub_id = serializers.CharField(source="current_hub", read_only=True, allow_null=True)

    class Meta:
        model = Driver
        fields = ["id", "is_available", "is_verified", "user_details", "current_hub_id", "license_number"]

        read_only_fields = ["id", "license_number", "is_verified"]
