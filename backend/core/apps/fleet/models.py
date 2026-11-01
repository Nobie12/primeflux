from django.db import models

from core.apps.accounts.models import User
from core.apps.logistics.models import Hub


class Vehicle(models.Model):
    VEHICLE_TYPES = [("motorcycle", "Motorcycle"), ("van", "Van"), ("bus", "Bus"), ("lorry", "Lorry")]
    STATUS_CHOICES = [("available", "Available"), ("on_trip", "On Trip"), ("maintenance", "Maintenance")]

    # Ensures a driver can only be assigned to one active vehicle profile at a time
    driver = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_vehicle"
    )
    plate_number = models.CharField(max_length=20, unique=True)
    capacity_weight = models.FloatField(help_text="Max weight in kg")
    capacity_volume = models.FloatField(help_text="Max volume in cubic meters")
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    model = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.plate_number} ({self.vehicle_type})"


class Route(models.Model):
    # Note: Linking to your existing City/Location model
    origin = models.ForeignKey(Hub, on_delete=models.CASCADE, related_name="routes_starting_here")
    destination = models.ForeignKey(Hub, on_delete=models.CASCADE, related_name="routes_ending_here")
    is_active = models.BooleanField(default=True)
    is_multileg = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("origin", "destination")
        ordering = ["origin__name", "destination__name"]

    def __str__(self):
        return f"{self.origin.name} -> {self.destination.name}"


class VehicleSchedule(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("assigned", "Assigned"),
        ("departed", "Departed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="schedules")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="schedules")
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="driving_schedules")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vehicle.plate_number} on {self.route} [{self.departure_time.date()}]"
