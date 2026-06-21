from rest_framework import serializers

from core.apps.accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "phone", "full_name", "role", "is_email_verified", "is_phone_verified", "created_at"]
        # These should only be updated via the OTP process, not a PATCH request
        read_only_fields = ["id", "email", "phone", "role", "is_email_verified", "is_phone_verified", "created_at"]
