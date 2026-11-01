from django.contrib import admin

from .models import Route, Vehicle, VehicleSchedule

# ==============================================================================
# BATCH ACTIONS
# ==============================================================================


@admin.action(description="Mark selected vehicles as Available")
def set_vehicles_available(modeladmin, request, queryset):
    queryset.update(status="available")


@admin.action(description="Mark selected vehicles as Maintenance")
def set_vehicles_maintenance(modeladmin, request, queryset):
    queryset.update(status="maintenance")


@admin.action(description="Mark selected schedules as Departed")
def set_schedules_departed(modeladmin, request, queryset):
    queryset.update(status="departed")


@admin.action(description="Mark selected schedules as Completed")
def set_schedules_completed(modeladmin, request, queryset):
    queryset.update(status="completed")


@admin.action(description="Cancel selected schedules")
def set_schedules_cancelled(modeladmin, request, queryset):
    queryset.update(status="cancelled")


# ==============================================================================
# ADMIN CONFIGURATIONS
# ==============================================================================


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "plate_number",
        "vehicle_type",
        "model",
        "get_driver_name",
        "capacity_weight",
        "capacity_volume",
        "status",
    )
    list_filter = ("vehicle_type", "status")
    search_fields = ("plate_number", "model", "driver__full_name", "driver__email")
    ordering = ("plate_number",)
    actions = [set_vehicles_available, set_vehicles_maintenance]

    def get_queryset(self, request):
        """Optimizes query performance by eager loading the linked driver."""
        return super().get_queryset(request).select_related("driver")

    @admin.display(description="Assigned Driver")
    def get_driver_name(self, obj):
        if obj.driver:
            return f"{obj.driver.full_name} ({obj.driver.email})"
        return "Unassigned"


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = (
        "get_route_name",
        "origin",
        "destination",
        "is_active",
        "is_multileg",
        "get_schedules_count",
    )
    list_filter = ("is_active", "is_multileg")
    search_fields = (
        "origin__name",
        "origin__city__name",
        "destination__name",
        "destination__city__name",
    )
    ordering = ("origin__name", "destination__name")

    def get_queryset(self, request):
        """Optimizes query performance by eager loading hubs and their related cities."""
        return (
            super().get_queryset(request).select_related("origin", "origin__city", "destination", "destination__city")
        )

    @admin.display(description="Route Pathway")
    def get_route_name(self, obj):
        return f"{obj.origin.name} ➔ {obj.destination.name}"

    @admin.display(description="Scheduled Trips")
    def get_schedules_count(self, obj):
        return obj.schedules.count()


@admin.register(VehicleSchedule)
class VehicleScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "get_vehicle_info",
        "get_route_info",
        "get_driver_info",
        "departure_time",
        "arrival_time",
        "status",
    )
    list_filter = ("status", "route", "departure_time")
    search_fields = (
        "vehicle__plate_number",
        "driver__full_name",
        "route__origin__name",
        "route__destination__name",
    )
    ordering = ("-departure_time",)
    actions = [set_schedules_departed, set_schedules_completed, set_schedules_cancelled]
    date_hierarchy = "departure_time"

    def get_queryset(self, request):
        """Optimizes query performance by eager loading vehicle, driver, and route relationships."""
        return (
            super()
            .get_queryset(request)
            .select_related(
                "vehicle",
                "driver",
                "route",
                "route__origin",
                "route__destination",
            )
        )

    @admin.display(description="Vehicle")
    def get_vehicle_info(self, obj):
        return f"{obj.vehicle.plate_number} ({obj.vehicle.vehicle_type})"

    @admin.display(description="Route")
    def get_route_info(self, obj):
        return f"{obj.route.origin.name} ➔ {obj.route.destination.name}"

    @admin.display(description="Assigned Driver")
    def get_driver_info(self, obj):
        return obj.driver.full_name
