from django.urls import path

from .views import (
    RouteListCreateView,
    RouteRetrieveUpdateDestroyView,
    VehicleListCreateView,
    VehicleRetrieveUpdateDestroyView,
    VehicleScheduleListCreateView,
    VehicleScheduleRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("vehicles/", VehicleListCreateView.as_view(), name="vehicle-list-create"),
    path("vehicles/<int:pk>/", VehicleRetrieveUpdateDestroyView.as_view(), name="vehicle-detail"),
    path("routes/", RouteListCreateView.as_view(), name="route-list-create"),
    path("routes/<int:pk>/", RouteRetrieveUpdateDestroyView.as_view(), name="route-detail"),
    path("schedules/", VehicleScheduleListCreateView.as_view(), name="schedule-list-create"),
    path("schedules/<int:pk>/", VehicleScheduleRetrieveUpdateDestroyView.as_view(), name="schedule-detail"),
]
