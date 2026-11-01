from rest_framework import generics

from core.core_functions.permissions import IsReadOnlyOrAdmin

from .models import Route, Vehicle, VehicleSchedule
from .serializers import RouteSerializer, VehicleScheduleSerializer, VehicleSerializer


class VehicleListCreateView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all().select_related("driver")
    serializer_class = VehicleSerializer
    permission_classes = [IsReadOnlyOrAdmin]


class VehicleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all().select_related("driver")
    serializer_class = VehicleSerializer
    permission_classes = [IsReadOnlyOrAdmin]


class RouteListCreateView(generics.ListCreateAPIView):
    queryset = Route.objects.all().select_related("origin", "destination")
    serializer_class = RouteSerializer
    permission_classes = [IsReadOnlyOrAdmin]


class RouteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Route.objects.all().select_related("origin", "destination")
    serializer_class = RouteSerializer
    permission_classes = [IsReadOnlyOrAdmin]


class VehicleScheduleListCreateView(generics.ListCreateAPIView):
    queryset = VehicleSchedule.objects.all().select_related("vehicle", "route", "driver")
    serializer_class = VehicleScheduleSerializer
    permission_classes = [IsReadOnlyOrAdmin]


class VehicleScheduleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VehicleSchedule.objects.all().select_related("vehicle", "route", "driver")
    serializer_class = VehicleScheduleSerializer
    permission_classes = [IsReadOnlyOrAdmin]
