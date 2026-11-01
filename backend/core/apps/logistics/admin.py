from django.contrib import admin

from .models import City, Hub


@admin.action(description="Mark selected hubs as Active")
def make_hubs_active(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="Mark selected hubs as Inactive")
def make_hubs_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    # Columns displayed in the list view table
    list_display = ("name", "code", "get_hubs_count")

    # Input bars for searching records
    search_fields = ("name", "code")

    # Default order of items in the table view
    ordering = ("name",)

    # Custom calculated column to show how many hubs are in a city
    @admin.display(description="Total Active Hubs")
    def get_hubs_count(self, obj):
        return obj.hubs.count()


@admin.register(Hub)
class HubAdmin(admin.ModelAdmin):
    # Columns displayed in the list view table
    list_display = ("name", "city", "address_summary", "is_active")

    # Sidebar quick filters
    list_filter = ("is_active", "city")

    # Search cross-references the related city table smoothly using '__name'
    search_fields = ("name", "address", "city__name", "city__code")

    # Default sorting configuration
    ordering = ("city__name", "name")

    # Batch action tools for rapid mock status changes
    actions = [make_hubs_active, make_hubs_inactive]

    def get_queryset(self, request):
        """
        Optimizes dashboard data fetching performance by pulling
        related city objects in a single joint SQL command execution.
        """
        return super().get_queryset(request).select_related("city")

    @admin.display(description="Hub Address")
    def address_summary(self, obj):
        """Truncates long address strings nicely for a cleaner table layout."""
        if obj.address and len(obj.address) > 40:
            return f"{obj.address[:37]}..."
        return obj.address or "No address provided"
