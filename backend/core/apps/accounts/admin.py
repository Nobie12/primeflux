from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "role", "is_staff", "is_active")
    search_fields = ("full_name", "email", "phone")
    list_filter = ("is_staff", "is_active")
