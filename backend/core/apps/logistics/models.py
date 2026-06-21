from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Hub(models.Model):
    name = models.CharField(max_length=100, unique=True)
    Location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="hubs")
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.Location.name} - {self.name}"
