from django.contrib import admin

from .models import Driver, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "role", "is_staff", "is_active")
    search_fields = ("full_name", "email", "phone")
    list_filter = ("is_staff", "is_active")


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ("get_name", "get_phone", "get_national_id", "is_available", "current_hub", "is_verified")

    search_fields = ("user__full_name", "user__phone", "license_number", "current_hub__name")
    list_filter = ("is_available", "is_verified", "current_hub")

    @admin.display(description="Driver Name")
    def get_name(self, obj):
        return obj.user.full_name

    @admin.display(description="Phone Number")
    def get_phone(self, obj):
        return obj.user.phone

    @admin.display(description="National ID")
    def get_national_id(self, obj):
        return obj.user.national_id if obj.user.national_id else "N/A"
